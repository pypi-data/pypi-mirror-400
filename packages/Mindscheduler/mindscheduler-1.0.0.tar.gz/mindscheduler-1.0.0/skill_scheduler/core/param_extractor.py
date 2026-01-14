"""
参数提取器 - 从自然语言查询中提取技能参数

支持多种参数格式和别名匹配，专为中英文混合场景设计。
"""
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .skill import Skill


@dataclass
class ExtractionPattern:
    """参数提取模式"""
    primary_name: str
    aliases: List[str]
    description_keywords: List[str] = None

    def __post_init__(self):
        if self.description_keywords is None:
            self.description_keywords = []


class ParamExtractor:
    """参数提取器 - 从查询中提取技能参数"""

    # 默认参数别名映射
    DEFAULT_PARAM_ALIASES = {
        "file": ["file_path", "filepath", "path", "文件", "文件路径", "路径"],
        "file_path": ["file", "filepath", "path", "文件", "文件路径", "路径"],
        "path": ["file", "file_path", "filepath", "文件", "文件路径"],
        "name": ["username", "user_name", "名字", "名称"],
        "text": ["content", "message", "文本", "内容"],
        "input": ["input_file", "source", "输入", "源文件"],
        "output": ["output_file", "dest", "destination", "输出", "目标文件"],
        "encoding": ["charset", "编码"],
        "directory": ["dir", "folder", "目录", "文件夹"],
    }

    # 文件扩展名模式
    FILE_EXTENSIONS = r'\.(pdf|txt|md|csv|json|xml|html|yaml|yml|py|js|ts|jsx|tsx|css|scss|sql|doc|docx|xlsx|xls)[^a-zA-Z0-9]*'

    def __init__(self, skill: Skill, custom_aliases: Optional[Dict[str, List[str]]] = None):
        """
        初始化参数提取器

        Args:
            skill: 技能对象
            custom_aliases: 自定义别名映射，会与默认别名合并
        """
        self.skill = skill
        self.aliases = {**self.DEFAULT_PARAM_ALIASES}
        if custom_aliases:
            for param_name, alias_list in custom_aliases.items():
                if param_name in self.aliases:
                    self.aliases[param_name].extend(alias_list)
                else:
                    self.aliases[param_name] = alias_list

        # 为每个输入参数创建提取模式
        self.extraction_patterns = self._build_extraction_patterns()

    def _build_extraction_patterns(self) -> Dict[str, ExtractionPattern]:
        """为技能的每个输入参数构建提取模式"""
        patterns = {}

        for param_name, input_spec in self.skill.inputs.items():
            # 收集该参数的所有别名
            param_aliases = self.aliases.get(param_name, [])

            # 从描述中提取关键词
            desc_keywords = self._extract_keywords_from_description(input_spec.description)

            patterns[param_name] = ExtractionPattern(
                primary_name=param_name,
                aliases=param_aliases,
                description_keywords=desc_keywords
            )

        return patterns

    def _extract_keywords_from_description(self, description: str) -> List[str]:
        """从参数描述中提取关键词"""
        if not description:
            return []

        keywords = []
        desc_lower = description.lower()

        # 常见关键词映射
        keyword_patterns = {
            "文件": ["file", "文件"],
            "路径": ["path", "路径", "filepath"],
            "目录": ["directory", "dir", "目录", "文件夹"],
            "文本": ["text", "文本", "内容", "content"],
            "编码": ["encoding", "编码", "charset"],
            "输出": ["output", "输出", "out"],
            "输入": ["input", "输入", "in"],
        }

        for keyword, patterns in keyword_patterns.items():
            if any(pattern in desc_lower for pattern in patterns):
                keywords.append(keyword)

        return keywords

    def extract(self, query: str) -> Dict[str, Any]:
        """
        从查询中提取参数

        Args:
            query: 自然语言查询字符串

        Returns:
            提取的参数字典
        """
        params = {}

        for param_name, pattern in self.extraction_patterns.items():
            value = self._extract_param_value(query, pattern)
            if value is not None:
                params[param_name] = value

        return params

    def _extract_param_value(self, query: str, pattern: ExtractionPattern) -> Optional[str]:
        """
        为单个参数提取值

        Args:
            query: 查询字符串
            pattern: 参数提取模式

        Returns:
            提取的值，未找到则返回 None
        """
        # 生成匹配模式列表
        match_patterns = self._generate_match_patterns(pattern)

        # 尝试每个模式
        for match_pattern in match_patterns:
            match = re.search(match_pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _generate_match_patterns(self, pattern: ExtractionPattern) -> List[str]:
        """为参数生成所有可能的匹配模式"""
        patterns = []
        param_name = pattern.primary_name

        # 1. 精确参数名匹配
        patterns.extend([
            rf"--{param_name}\s+(\S+)",
            rf"--{param_name}=(\S+)",
            rf"{param_name}\s*[=:：]\s*(\S+)",
        ])

        # 2. 别名匹配
        for alias in pattern.aliases:
            if alias == param_name:
                continue
            patterns.extend([
                rf"--{alias}\s+(\S+)",
                rf"--{alias}=(\S+)",
                rf"{alias}\s*[=:：]\s*(\S+)",
            ])

        # 3. 文件路径特殊处理（如果是文件相关参数）
        if self._is_file_param(pattern):
            patterns.extend([
                # 捕获完整路径（包括相对路径）
                r'文件路径\s*[是为：]\s*(\S+)',
                r'路径\s*[是为：]\s*(\S+)',
                rf'(?:{param_name}|{"|".join(pattern.aliases[:3])})\s+(\.\/[\w\.\-\/\\]+\.{self.FILE_EXTENSIONS})',
                # 匹配常见文件扩展名
                r'([\w\-./\\]+\.(?:txt|md|pdf|csv|json|xml|yaml|yml|html|py|js|ts|css|sql|docx|xlsx))',
            ])

        return patterns

    def _is_file_param(self, pattern: ExtractionPattern) -> bool:
        """判断是否为文件相关参数"""
        param_name = pattern.primary_name.lower()
        aliases_lower = [a.lower() for a in pattern.aliases]
        keywords_lower = [k.lower() for k in pattern.description_keywords]

        file_indicators = ["file", "path", "文件", "路径", "目录"]

        return (
            any(indicator in param_name for indicator in file_indicators) or
            any(indicator in alias for alias in aliases_lower for indicator in file_indicators) or
            any(indicator in keyword for keyword in keywords_lower for indicator in file_indicators)
        )


def extract_params_from_query(skill: Skill, query: str) -> Dict[str, Any]:
    """
    便捷函数：从查询中提取技能参数

    Args:
        skill: 技能对象
        query: 自然语言查询字符串

    Returns:
        提取的参数字典
    """
    extractor = ParamExtractor(skill)
    return extractor.extract(query)