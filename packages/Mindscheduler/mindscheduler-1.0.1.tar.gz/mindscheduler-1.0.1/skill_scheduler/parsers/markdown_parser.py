"""
Markdown + Front Matter 技能定义解析器

支持使用 Markdown 文件定义技能，配置部分使用 YAML Front Matter，
文档部分使用 Markdown 格式。
"""
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SkillMetadata:
    """技能元数据"""
    schema_version: str = "v1"
    name: str = ""
    version: str = "1.0.0"
    type: str = "atomic"
    title: str = ""
    description: str = ""
    author: str = ""
    homepage: str = ""
    license: str = "MIT"
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class SkillInput:
    """输入参数定义"""
    name: str
    type: str
    required: bool = False
    description: str = ""
    default: Any = None


@dataclass
class SkillOutput:
    """输出定义"""
    type: str
    description: str = ""


@dataclass
class SkillPermission:
    """权限定义"""
    read_file: List[str] = None
    write_file: List[str] = None
    network: bool = False
    execute_script: bool = True

    def __post_init__(self):
        if self.read_file is None:
            self.read_file = []
        if self.write_file is None:
            self.write_file = []


class MarkdownSkillParser:
    """Markdown 技能定义解析器（仅支持 skill.md 格式）"""

    # Front Matter 分隔符
    FRONT_MATTER_PATTERN = r'^---\s*$'

    # 必需字段（只有 name 和 description）
    REQUIRED_FIELDS = ["name", "description"]

    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.markdown_file = skill_dir / "skill.md"

        if not self.markdown_file.exists():
            raise FileNotFoundError(f"No skill.md found in {skill_dir}")

        self.config_file = self.markdown_file
        self.format = "markdown"

    def parse(self) -> Dict[str, Any]:
        """解析技能定义"""
        return self._parse_markdown()

    def _parse_markdown(self) -> Dict[str, Any]:
        """解析 Markdown 格式的技能定义"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分离 Front Matter 和 Markdown 内容
        front_matter, markdown_content = self._split_front_matter(content)

        # 解析 Front Matter (YAML)
        config = yaml.safe_load(front_matter) or {}

        # 保存原始 Markdown 内容（供后续推断使用）
        config["_markdown_content"] = markdown_content

        # 验证必需字段
        self._validate_required_fields(config)

        # 从 Markdown 内容中提取额外信息
        metadata = self._extract_metadata_from_markdown(markdown_content)

        # 合并配置（Markdown 中的配置优先）
        config = {**config, **metadata}

        # 如果没有 name，从目录名获取
        if "name" not in config:
            config["name"] = self.skill_dir.name

        # 智能推断：如果没有 script，从文档中推断
        if "script" not in config:
            inferred_script = self._infer_script_from_documentation(markdown_content, config)
            if inferred_script:
                config["script"] = inferred_script

        # 智能推断：如果没有 inputs，从文档中推断
        if "inputs" not in config:
            inferred_inputs = self._infer_inputs_from_documentation(markdown_content, config)
            if inferred_inputs:
                config["inputs"] = inferred_inputs

        # 智能推断：如果没有 dependencies，从脚本中推断
        if "dependencies" not in config or not config["dependencies"]:
            inferred_deps = self._infer_dependencies_from_script(config)
            if inferred_deps:
                config["dependencies"] = inferred_deps

        return config

    def _infer_dependencies_from_script(self, config: Dict[str, Any]) -> List[str]:
        """从脚本 import 语句中推断依赖"""
        script_path = self._get_script_path(config)
        if not script_path:
            return []

        script_file = self.skill_dir / script_path
        if not script_file.exists():
            return []

        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # 常见的 PDF 处理库映射
            lib_mapping = {
                'PyPDF2': 'PyPDF2>=3.0',
                'pypdf': 'pypdf>=3.0',
                'pdfplumber': 'pdfplumber>=0.10.3',
                'pdfrw': 'pdfrw>=0.4',
                'Pillow': 'Pillow>=9.0',
                'pandas': 'pandas>=1.5.0',
                'numpy': 'numpy>=1.20.0',
            }

            dependencies = []
            for lib, version_spec in lib_mapping.items():
                if lib in script_content:
                    dependencies.append(version_spec)

            return dependencies
        except Exception:
            return []

    def _validate_required_fields(self, config: Dict[str, Any]):
        """验证必需字段"""
        missing_fields = [f for f in self.REQUIRED_FIELDS if f not in config or not config[f]]
        if missing_fields:
            raise ValueError(
                f"Missing required fields in {self.config_file}: {', '.join(missing_fields)}. "
                f"Required: {', '.join(self.REQUIRED_FIELDS)}"
            )

    def _split_front_matter(self, content: str) -> Tuple[str, str]:
        """分离 Front Matter 和 Markdown 内容"""
        lines = content.split('\n')

        # 查找 Front Matter 边界
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if re.match(self.FRONT_MATTER_PATTERN, line):
                if start_idx is None:
                    start_idx = i + 1  # 第一个 --- 后面开始
                elif end_idx is None:
                    end_idx = i  # 第二个 --- 之前结束
                    break

        if start_idx is None or end_idx is None:
            # 没有 Front Matter，全部是 Markdown
            return "", content

        front_matter = '\n'.join(lines[start_idx:end_idx])
        markdown_content = '\n'.join(lines[end_idx + 1:])

        return front_matter, markdown_content

    def _extract_metadata_from_markdown(self, content: str) -> Dict[str, Any]:
        """从 Markdown 内容中提取元数据"""
        metadata = {}

        # 提取标题（第一个 # 标题）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()

        # 提取引用块作为描述
        desc_match = re.search(r'^>\s*(.+)$', content, re.MULTILINE)
        if desc_match:
            metadata["description"] = desc_match.group(1).strip()

        # 提取代码块中的示例
        code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
        if code_blocks:
            metadata["examples"] = [
                {"lang": lang, "code": code.strip()}
                for lang, code in code_blocks
            ]

        # 提取参数表格（只在找到时设置，不覆盖 Front Matter 的 inputs）
        table_inputs = self._extract_param_table(content)
        if table_inputs:
            # 只在有额外信息时才覆盖（合并而非完全覆盖）
            metadata["inputs"] = table_inputs

        return metadata

    def _infer_script_from_documentation(self, content: str, config: Dict[str, Any]) -> Optional[str]:
        """从文档中推断脚本文件名

        按优先级查找:
        1. 代码块中的脚本执行命令 (python scripts/xxx.py)
        2. 文件列表或目录结构示例
        3. 默认值 scripts/main.py
        """
        # 方法1: 从 Python 代码块中查找脚本文件引用
        python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        for code in python_blocks:
            # 查找文件创建/写入模式
            script_matches = re.findall(
                r'(open|Path)\(["\']([\w/.\-]+\.py)["\']\)',
                code
            )
            for match in script_matches:
                script_path = match.group(1)  # 捕获的路径
                # 如果是相对路径且在 scripts/ 目录下
                if 'scripts/' in script_path:
                    return script_path

            # 查找 subprocess 调用
            subprocess_matches = re.findall(
                r'subprocess\.(run|call)\(["\'].*?python\s+(\S+?)["\']',
                code
            )
            for match in subprocess_matches:
                script_path = match.strip('"\'')
                if 'scripts/' in script_path:
                    return script_path

        # 方法2: 从文件结构示例中推断
        # 查找类似 "skills/xxx/scripts/handler.py" 的模式
        structure_matches = re.findall(
            r'(?:skills/[\w-]+/|directory\s*structure.*?)?(scripts/[\w.-]+\.py)',
            content,
            re.IGNORECASE
        )
        if structure_matches:
            return structure_matches[0]

        # 方法3: 查找文件名提及
        filename_matches = re.findall(
            r'(?:script|file|program|command):\s*["\']?(scripts/[\w.-]+\.py)["\']?',
            content,
            re.IGNORECASE
        )
        if filename_matches:
            return filename_matches[0].strip('"\' ')

        # 方法4: 默认回退
        return "scripts/main.py"

    def _infer_inputs_from_documentation(self, content: str, config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """从文档中智能推断输入参数

        查找模式（按优先级）:
        1. 脚本中的 argparse 定义
        2. Input Parameters 表格
        3. 使用示例中的 $param 或 {{param}}
        """
        inferred_inputs = {}

        # 方法1: 从脚本文件中的 argparse 定义提取（最准确）
        script_path = self._get_script_path(config)
        if script_path:
            script_file = self.skill_dir / script_path
            if script_file.exists():
                try:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        script_content = f.read()

                    # 查找 argparse 参数定义
                    if 'argparse' in script_content:
                        # 匹配 add_argument("--param") 或 add_argument("param")
                        arg_matches = re.findall(
                            r'add_argument\(["\'](-?[\w-]+)["\']',
                            script_content
                        )
                        for arg_name in arg_matches:
                            if not arg_name.startswith('-'):  # 跳过短选项如 -f
                                # 去掉前导 --
                                clean_name = arg_name.lstrip('-')
                                inferred_inputs[clean_name] = {
                                    "name": clean_name,
                                    "type": "string",
                                    "required": True,  # 默认为必需
                                    "description": f"Parameter: {clean_name}"
                                }
                        # 如果找到了 argparse，就使用它
                        if inferred_inputs:
                            return inferred_inputs
                except Exception:
                    pass

        # 方法2: 从 Input Parameters 表格提取
        table_inputs = self._extract_param_table(content)
        if table_inputs:
            return table_inputs

        # 方法3: 从文档中的参数占位符提取
        # 匹配 $file_path 或 {{file_content}} 等
        param_patterns = [
            r'\$\w+',  # $param
            r'\{\{[\w_]+\}\}',  # {{param}}
        ]
        for pattern in param_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                param_name = match.strip('${}').strip()
                if param_name and param_name not in inferred_inputs:
                    inferred_inputs[param_name] = {
                        "name": param_name,
                        "type": "string",
                        "required": True,
                        "description": f"Inferred from documentation: {param_name}"
                    }

        return inferred_inputs

    def _get_script_path(self, config: Dict[str, Any]) -> Optional[str]:
        """获取脚本路径"""
        # 优先使用配置中的 script
        if "script" in config:
            return config["script"]

        # 从文档推断
        doc = config.get("_markdown_content", "")
        if not doc:
            # 尝试读取文档
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    full_content = f.read()
                _, doc = self._split_front_matter(full_content)
            except:
                return None

        # 从代码块中查找 python script 命令
        matches = re.findall(r'```bash\s+python\s+([\w/\-\.]+\.py)', doc)
        if matches:
            return matches[0]

        # 默认查找 scripts 目录
        scripts_dir = self.skill_dir / "scripts"
        if scripts_dir.exists():
            possible_scripts = [
                "scripts/main.py",
                "scripts/handler.py",
                "scripts/script.py",
            ]
            for script in possible_scripts:
                if (self.skill_dir / script).exists():
                    return script

        return None

    def _extract_param_table(self, content: str) -> Dict[str, Dict[str, Any]]:
        """从 Markdown 表格中提取参数定义"""
        inputs = {}

        # 查找参数表格（在 "### 输入参数" 或类似标题下）
        # 匹配从标题到表格结束，支持标题和表格之间有空行
        table_pattern = r'(?:输入参数|参数|Inputs|Input\s+Parameters)[^\n]*\n+((?:\|.+?\|\n)+)'
        table_match = re.search(table_pattern, content, re.IGNORECASE | re.DOTALL)

        if table_match:
            table = table_match.group(1)
            rows = [line.strip() for line in table.split('\n') if line.strip().startswith('|')]

            if len(rows) >= 2:
                # 第一行是表头，跳过分隔行（第二行）
                headers = [h.strip() for h in rows[0].split('|')[1:-1]]
                for row in rows[2:]:  # 跳过表头和分隔符
                    cells = [c.strip() for c in row.split('|')[1:-1]]
                    if len(cells) >= 2:
                        param_name = cells[0]
                        # 检查 required 列（支持中文"是"、英文"Yes"/"true"）
                        required_value = cells[2].lower() if len(cells) > 2 else ""
                        is_required = required_value in ("是", "yes", "true", "1")
                        inputs[param_name] = {
                            "type": cells[1] if len(cells) > 1 else "string",
                            "required": is_required,
                            "description": cells[3] if len(cells) > 3 else ""
                        }

        return inputs

    def get_documentation(self) -> str:
        """获取技能的 Markdown 文档"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        _, markdown_content = self._split_front_matter(content)
        return markdown_content.strip()


def parse_skill_definition(skill_dir: Path) -> Dict[str, Any]:
    """解析技能定义（仅支持 skill.md）"""
    parser = MarkdownSkillParser(skill_dir)
    return parser.parse()


def get_skill_documentation(skill_dir: Path) -> str:
    """获取技能文档"""
    parser = MarkdownSkillParser(skill_dir)
    return parser.get_documentation()
