import os
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class SkillType(Enum):
    ATOMIC = "atomic"


@dataclass
class SkillInput:
    name: str
    type: str
    required: bool
    description: str = ""
    default: Any = None


@dataclass
class SkillOutput:
    type: str
    description: str = ""


@dataclass
class SkillPermission:
    read_file: List[str] = None
    write_file: List[str] = None
    network: bool = False
    execute_script: bool = True

    def __post_init__(self):
        if self.read_file is None:
            self.read_file = []
        if self.write_file is None:
            self.write_file = []


class Skill:
    def __init__(self, name: str, skill_dir: Path):
        self.name = name
        self.skill_dir = skill_dir
        self.config = {}
        self.inputs: Dict[str, SkillInput] = {}
        self.output: Optional[SkillOutput] = None
        self.dependencies: List[str] = []
        self.timeout: int = 30
        self.command: Optional[str] = None
        self.permissions: Optional[SkillPermission] = None

        # 新增字段
        self.schema_version: str = "v1"
        self.type: SkillType = SkillType.ATOMIC
        self.title: str = ""
        self.author: str = ""
        self.homepage: str = ""
        self.license: str = ""

        # execution_rules 支持
        self.execution_rules: Optional[Dict[str, Any]] = None
        self.script_path: Optional[str] = None  # 自定义脚本路径

        self._load_config()

    def _load_config(self):
        # 只支持 Markdown 格式 (skill.md)
        markdown_file = self.skill_dir / "skill.md"

        if not markdown_file.exists():
            raise FileNotFoundError(f"Skill config not found: {markdown_file}")

        self.config = self._load_markdown_config(markdown_file)

        self._parse_metadata()
        self._parse_inputs()
        self._parse_output()
        self._parse_permissions()

    def _load_markdown_config(self, md_file: Path) -> Dict[str, Any]:
        """加载 Markdown 格式的配置"""
        # 参数 md_file 用于检测是否存在，实际使用 self.skill_dir
        from ..parsers.markdown_parser import parse_skill_definition
        return parse_skill_definition(self.skill_dir)

    def _parse_metadata(self):
        self.schema_version = self.config.get("schema_version", "v1")
        self.type = SkillType(self.config.get("type", "atomic"))
        self.title = self.config.get("title", self.name)
        self.author = self.config.get("author", "")
        self.homepage = self.config.get("homepage", "")
        self.license = self.config.get("license", "MIT")
        self.version = self.config.get("version", "1.0.0")

        # 解析 dependencies - 支持字符串或列表格式
        deps_config = self.config.get("dependencies", [])
        if isinstance(deps_config, str):
            # 字符串格式: "pandas>=1.5.0, numpy>=1.20" 或 "pandas>=1.5.0"
            self.dependencies = [d.strip() for d in deps_config.split(',') if d.strip()]
        else:
            self.dependencies = deps_config if deps_config else []

        self.timeout = self.config.get("timeout", 30)
        self.command = self.config.get("command")

        # 解析 execution_rules 和自定义脚本路径
        self.execution_rules = self.config.get("execution_rules")

        # 解析参数转换配置
        self.param_transforms = self.config.get("param_transforms", {})

        # 解析允许的文件后缀（用于灵活的文件格式校验）
        self.allowed_extensions = self._parse_allowed_extensions()

        # 解析脚本路径（优先级：直接定义的 script > execution_rules 中的 script > 从文档推断）
        # 1. 检查 Front Matter 中是否直接定义了 script 字段
        self.script_path = self.config.get("script")

        # 2. 如果没有直接定义，从 execution_rules 中提取
        if not self.script_path and self.execution_rules:
            for step_key, step_config in self.execution_rules.items():
                if isinstance(step_config, dict) and "script" in step_config:
                    self.script_path = step_config["script"]
                    break

        # 3. 智能推断：从文档中推断 script 路径
        if not self.script_path:
            self.script_path = self._infer_script_from_docs()

        # 支持额外字段（兼容不同格式的 skill.md）
        self.disable_model_invocation = self.config.get("disable-model-invocation", False)
        self.priority = self.config.get("priority", 5)  # 默认中等优先级

        # Claude Skill 规范字段
        self.allowed_tools = self.config.get("allowed-tools", [])
        self.model = self.config.get("model", "")

    def _parse_allowed_extensions(self) -> List[str]:
        """解析允许的文件后缀列表"""
        extensions = []

        # 从 permissions.read_file 中提取
        if self.permissions and self.permissions.read_file:
            for pattern in self.permissions.read_file:
                if pattern.startswith("*."):
                    extensions.append(pattern.replace("*.", "."))

        # 从配置的 allowed_extensions 中提取（如果有的话）
        if "allowed_extensions" in self.config:
            extensions.extend(self.config["allowed_extensions"])

        return extensions

    def _parse_allowed_tools(self) -> Dict[str, List[str]]:
        """解析 allowed-tools 字段

        支持格式: Python(pdfplumber, pdfrw), Bash(file:write)
        返回: {"Python": ["pdfplumber", "pdfrw"], "Bash": ["file:write"]}
        """
        allowed_tools = self.allowed_tools
        if not allowed_tools:
            return {}

        result = {}
        if isinstance(allowed_tools, str):
            # 解析字符串格式: "Python(pdfplumber, pdfrw), Bash(file:write)"
            import re
            pattern = r'(\w+)\(([^)]*)\)'
            matches = re.findall(pattern, allowed_tools)
            for tool_name, tools_str in matches:
                tools = [t.strip() for t in tools_str.split(',') if t.strip()]
                result[tool_name] = tools
        elif isinstance(allowed_tools, list):
            # 列表格式: ["Python(pdfplumber)", "Bash(file:write)"]
            import re
            for item in allowed_tools:
                match = re.match(r'(\w+)\(([^)]*)\)', item)
                if match:
                    tool_name, tools_str = match.groups()
                    tools = [t.strip() for t in tools_str.split(',') if t.strip()]
                    result[tool_name] = tools

        return result

    def _parse_inputs(self):
        inputs = self.config.get("inputs", {})
        # 支持两种格式：文档中的 input 和当前使用的 inputs
        if not inputs:
            inputs = self.config.get("input", [])

        if isinstance(inputs, list):
            for inp in inputs:
                self.inputs[inp["name"]] = SkillInput(
                    name=inp["name"],
                    type=inp.get("type", "string"),
                    required=inp.get("required", False),
                    description=inp.get("description", ""),
                    default=inp.get("default")
                )
        elif isinstance(inputs, dict):
            for name, spec in inputs.items():
                self.inputs[name] = SkillInput(
                    name=name,
                    type=spec.get("type", "string"),
                    required=spec.get("required", False),
                    description=spec.get("description", ""),
                    default=spec.get("default")
                )

        # 智能推断：如果没有定义 inputs，尝试从文档中推断
        if not self.inputs:
            self._infer_inputs_from_docs()

    def _infer_inputs_from_docs(self):
        """从文档中智能推断输入参数"""
        import re

        # 获取文档内容
        documentation = self.get_documentation()
        if not documentation:
            return

        # 方法 1: 从 Input Parameters 表格中提取
        # 查找表格（从表头到表格结束）
        table_pattern = r'\|\s*Parameter\s*\|\s*Type\s*\|\s*Required\s*\|.*?\n((?:\|.*?\|\s*\n)+)'
        table_match = re.search(table_pattern, documentation, re.IGNORECASE)
        if table_match:
            table_content = table_match.group(1)
            # 提取表格行（更宽松的匹配）
            # 匹配 | param_name | ... | Yes/No | ...
            rows = re.findall(r'\|\s*(\w+)\s*\|[^|]*\|\s*(Yes|No|true|false)\s*\|', table_content, re.IGNORECASE)
            for param_name, required in rows:
                is_required = required.lower() in ("yes", "true")
                self.inputs[param_name] = SkillInput(
                    name=param_name,
                    type="string",
                    required=is_required,
                    description=f"Inferred parameter: {param_name}",
                    default=None
                )

        # 方法 2: 从 Usage Examples 中提取参数（如 $file_path, {{file}}）
        if not self.inputs:
            # 匹配 $param_name 或 {{param_name}}
            param_matches = re.findall(r'[\$\{]\{?(\w+)\}?\}?', documentation)
            for param_name in set(param_matches):
                if param_name not in ['file_path', 'file', 'input', 'output']:
                    continue
                if param_name not in self.inputs:
                    self.inputs[param_name] = SkillInput(
                        name=param_name,
                        type="string",
                        required=True,
                        description=f"Inferred from documentation: {param_name}",
                        default=None
                    )

    def _infer_script_from_docs(self) -> Optional[str]:
        """从文档中智能推断脚本路径"""
        import re

        # 获取文档内容
        documentation = self.get_documentation()
        if not documentation:
            return None

        # 方法 1: 从代码块中提取 python script 路径
        # 匹配 ```bash python scripts/xxx.py ```
        bash_scripts = re.findall(r'```bash\s+python\s+([\w/\-\.]+\.py)', documentation)
        if bash_scripts:
            return bash_scripts[0]

        # 方法 2: 从 $ command 格式中提取
        # 匹配 python scripts/read_file.py $file_path
        cmd_scripts = re.findall(r'python\s+([\w/\-\.]+\.py)', documentation)
        if cmd_scripts:
            return cmd_scripts[0]

        # 方法 3: 检查 scripts 目录下是否有对应名称的脚本
        scripts_dir = self.skill_dir / "scripts"
        if scripts_dir.exists():
            # 优先查找与技能同名的脚本
            possible_scripts = [
                f"scripts/{self.name}.py",
                f"scripts/{self.name}/main.py",
                f"scripts/main.py",
                f"scripts/handler.py",
            ]
            for script_path in possible_scripts:
                if (self.skill_dir / script_path).exists():
                    return script_path

        return None

    def _parse_output(self):
        output = self.config.get("output", {})
        if output:
            self.output = SkillOutput(
                type=output.get("type", "string"),
                description=output.get("description", "")
            )

    def _parse_permissions(self):
        perms = self.config.get("permissions")
        if perms:
            # 支持两种权限格式
            # 格式1 (详细): {read_file: [...], write_file: [...], network: bool, execute_script: bool}
            # 格式2 (简化): {read: bool, write: bool, network: bool}

            if "read_file" in perms or "write_file" in perms:
                # 详细格式
                self.permissions = SkillPermission(
                    read_file=perms.get("read_file", []),
                    write_file=perms.get("write_file", []),
                    network=perms.get("network", False),
                    execute_script=perms.get("execute_script", True)
                )
            else:
                # 简化格式: {read: bool, write: bool, network: bool}
                read_allowed = perms.get("read", False)
                write_allowed = perms.get("write", False)

                # 简化格式下，如果 read=true，允许读取所有文件（不限制）
                # 如果 write=true，允许写入所有文件（不限制）
                self.permissions = SkillPermission(
                    read_file=[] if read_allowed else [],  # 空列表表示不限制（或根据需求改为通配符）
                    write_file=[] if write_allowed else [],
                    network=perms.get("network", False),
                    execute_script=perms.get("execute_script", True)
                )

                # 标记是否为简化权限模式（用于权限检查逻辑）
                self._simple_permission_mode = True
        else:
            self.permissions = SkillPermission()
            self._simple_permission_mode = False

    @property
    def description(self) -> str:
        return self.config.get("description", "")

    @property
    def tags(self) -> List[str]:
        return self.config.get("tags", [])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        for name, input_spec in self.inputs.items():
            if input_spec.required and name not in params:
                return False, f"Missing required parameter: {name}"

            if name in params:
                value = params[name]
                expected_type = input_spec.type

                if expected_type == "integer":
                    try:
                        params[name] = int(value)
                    except (ValueError, TypeError):
                        return False, f"Parameter '{name}' must be an integer"

                elif expected_type == "float":
                    try:
                        params[name] = float(value)
                    except (ValueError, TypeError):
                        return False, f"Parameter '{name}' must be a float"

                elif expected_type == "boolean":
                    if isinstance(value, str):
                        params[name] = value.lower() in ("true", "1", "yes")
                    else:
                        params[name] = bool(value)

        return True, ""

    def get_command(self, params: Dict[str, Any]) -> str:
        """获取命令（用于 command 类型执行）"""
        if not self.command:
            # 如果没有 command，使用 script_path
            if self.script_path:
                script_full_path = (self.skill_dir / self.script_path).resolve()
                return f"python {script_full_path}"
            return None

        # Merge params with default values from skill inputs
        format_params = {"skill_dir": self.skill_dir}
        for name, input_spec in self.inputs.items():
            format_params[name] = params.get(name, input_spec.default if input_spec.default is not None else "")
        # Also add any extra params that aren't in inputs
        for key, value in params.items():
            if key not in format_params:
                format_params[key] = value

        cmd = self.command.format(**format_params)
        return cmd

    def check_permissions(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """检查权限"""
        if not self.permissions:
            return True, ""

        # 简化权限模式：read/write 是布尔值而不是白名单列表
        if getattr(self, '_simple_permission_mode', False):
            # 在简化模式下，如果 permissions.read_file 为空列表但 read=true，表示允许所有读取
            # 权限检查已在设置时处理，这里直接返回
            # 只检查网络权限
            if hasattr(self, '_needs_network') and self._needs_network(params):
                if not self.permissions.network:
                    return False, "Network access denied"
            return True, ""

        # 检查文件读取权限（详细白名单模式）
        if self.permissions.read_file:
            for param_value in params.values():
                if isinstance(param_value, str) and ('/' in param_value or '\\' in param_value):
                    allowed = False
                    for pattern in self.permissions.read_file:
                        if self._match_path_pattern(param_value, pattern):
                            allowed = True
                            break
                    if not allowed:
                        return False, f"File access denied: {param_value} not in whitelist"

        # 检查网络访问权限
        if hasattr(self, '_needs_network') and self._needs_network(params):
            if not self.permissions.network:
                return False, "Network access denied"

        return True, ""

    def _match_path_pattern(self, path: str, pattern: str) -> bool:
        """检查路径是否匹配白名单模式"""
        import fnmatch
        path_abs = os.path.abspath(path)

        # 处理通配符模式（如 *.txt）
        if '*' in pattern or '?' in pattern or '[' in pattern:
            # 对于通配符模式，只检查文件名部分
            from pathlib import Path as PathlibPath
            path_name = PathlibPath(path_abs).name
            # 如果模式是简单的 *.ext，直接匹配文件名
            if pattern.startswith('*.'):
                return fnmatch.fnmatch(path_name, pattern)
            # 否则使用完整路径进行匹配
            return fnmatch.fnmatch(path_abs, pattern)

        # 对于具体路径，进行绝对路径匹配
        pattern_abs = os.path.abspath(pattern)

        if os.path.exists(pattern_abs) and os.path.isfile(pattern_abs):
            return path_abs == pattern_abs

        if os.path.exists(pattern_abs) and os.path.isdir(pattern_abs):
            return path_abs.startswith(pattern_abs + os.sep)

        return fnmatch.fnmatch(path_abs, pattern_abs)

    def get_documentation(self) -> str:
        """获取技能的完整 Markdown 文档（用于 LLM 上下文）"""
        try:
            from ..parsers.markdown_parser import get_skill_documentation
            return get_skill_documentation(self.skill_dir)
        except Exception:
            return ""

    def get_full_definition(self) -> str:
        """获取技能的完整定义（包括 Front Matter 和文档）"""
        try:
            md_file = self.skill_dir / "skill.md"
            with open(md_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""


class SkillManager:
    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self._load_skills()

    def _load_skills(self):
        if not self.skills_dir.exists():
            return

        for skill_path in self.skills_dir.iterdir():
            # 只检查 skill.md 文件
            skill_md = skill_path / "skill.md"

            if skill_path.is_dir() and skill_md.exists():
                try:
                    # 使用解析器加载配置
                    from ..parsers.markdown_parser import parse_skill_definition
                    config = parse_skill_definition(skill_path)

                    skill_type = config.get("type", "atomic")

                    # 只创建 Skill 对象（不再区分类型）
                    skill = Skill(skill_path.name, skill_path)

                    self.skills[skill.name] = skill
                except Exception as e:
                    logger.warning(f"Failed to load skill {skill_path.name}: {e}")

    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

    def list_skills(self) -> List[Skill]:
        return list(self.skills.values())

    def list_skill_names(self) -> List[str]:
        return list(self.skills.keys())

    def search_by_tags(self, tags: List[str]) -> List[Skill]:
        results = []
        for skill in self.skills.values():
            if any(tag in skill.tags for tag in tags):
                results.append(skill)
        return results
