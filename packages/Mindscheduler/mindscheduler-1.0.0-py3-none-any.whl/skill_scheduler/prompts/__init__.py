"""
提示词模板库
支持 YAML 配置的提示词模板，动态参数注入
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class PromptTemplate:
    """提示词模板类"""

    def __init__(self, name: str, template_path: Path):
        self.name = name
        self.template_path = template_path
        self.config = {}
        self._load_template()

    def _load_template(self):
        if not self.template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {self.template_path}")

        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    @property
    def system_prompt(self) -> str:
        return self.config.get("system_prompt", "")

    @property
    def user_prompt_template(self) -> str:
        return self.config.get("user_prompt_template", "")

    def format(self, **kwargs) -> str:
        """格式化用户提示词"""
        template = self.user_prompt_template
        return template.format(**kwargs)

    def format_system(self, **kwargs) -> str:
        """格式化系统提示词"""
        template = self.system_prompt
        return template.format(**kwargs)

    def get_examples(self) -> list:
        """获取少样本示例"""
        return self.config.get("few_shot_examples", [])

    def get_flow_templates(self) -> Dict[str, Any]:
        """获取流程模板"""
        return self.config.get("flow_templates", {})


class PromptTemplateLibrary:
    """提示词模板库"""

    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            # 默认使用框架内置的 prompts 目录
            prompts_dir = Path(__file__).parent

        self.prompts_dir = Path(prompts_dir)
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        if not self.prompts_dir.exists():
            return

        for yaml_file in self.prompts_dir.glob("*.yaml"):
            try:
                template = PromptTemplate(yaml_file.stem, yaml_file)
                self.templates[template.name] = template
            except Exception as e:
                logger.warning(f"Failed to load prompt template {yaml_file.name}: {e}")

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        return self.templates.get(name)

    def list_templates(self) -> list:
        return list(self.templates.keys())

    def get_intent_template(self) -> PromptTemplate:
        """获取意图理解模板"""
        return self.templates.get("intent_understanding")

    def get_flow_template(self) -> PromptTemplate:
        """获取流程编排模板"""
        return self.templates.get("flow_orchestration")


# 全局单例
_global_library: Optional[PromptTemplateLibrary] = None


def get_prompt_library() -> PromptTemplateLibrary:
    """获取全局提示词模板库"""
    global _global_library
    if _global_library is None:
        _global_library = PromptTemplateLibrary()
    return _global_library
