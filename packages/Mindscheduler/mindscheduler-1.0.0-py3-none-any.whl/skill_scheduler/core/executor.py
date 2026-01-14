import os
import signal
import subprocess
import tempfile
import shlex
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

from .dependency_manager import DependencyManager

logger = logging.getLogger(__name__)


class Executor:
    def __init__(
        self,
        timeout: int = 30,
        max_memory_mb: int = 512,
        work_dir: str = "./temp",
        auto_install_deps: bool = True,
        metrics_registry=None
    ):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.auto_install_deps = auto_install_deps
        self.metrics_registry = metrics_registry

    def execute(self, skill, params: Dict[str, Any]) -> Tuple[str, bool]:
        # 通知监控：技能开始执行
        execution_id = None
        if self.metrics_registry:
            execution_id = self.metrics_registry.notify_skill_start(skill.name, params)
            logger.debug(f"Started execution {execution_id} for skill '{skill.name}'")

        try:
            # 检查权限
            if hasattr(skill, 'check_permissions'):
                allowed, error = skill.check_permissions(params)
                if not allowed:
                    if self.metrics_registry:
                        self.metrics_registry.notify_skill_complete(
                            execution_id,
                            success=False,
                            error_message=error
                        )
                    logger.warning(f"Permission denied for skill '{skill.name}': {error}")
                    return error, False

            # 自动安装依赖（可通过配置禁用）
            if self.auto_install_deps and skill.dependencies:
                install_success, install_msg = self.install_dependencies(skill.dependencies)
                if not install_success:
                    error = f"Dependency installation failed: {install_msg}"
                    if self.metrics_registry:
                        self.metrics_registry.notify_skill_complete(
                            execution_id,
                            success=False,
                            error_message=error
                        )
                    logger.error(f"Dependency installation failed for skill '{skill.name}'")
                    return error, False

            valid, error_msg = skill.validate_params(params)
            if not valid:
                if self.metrics_registry:
                    self.metrics_registry.notify_skill_complete(
                        execution_id,
                        success=False,
                        error_message=error_msg
                    )
                logger.warning(f"Parameter validation failed for skill '{skill.name}': {error_msg}")
                return error_msg, False

            # 应用参数转换（如：读取文件内容）
            params = self._apply_param_transforms(skill, params)

            # 智能推断：自动检测脚本中的占位符，添加必要的参数转换
            if hasattr(skill, 'script_path') and skill.script_path:
                params = self._auto_infer_param_transforms(skill, params)

            # 执行方式优先级：
            # 1. execution_rules - 多步骤执行规则
            # 2. command - 直接命令
            # 3. script_path - 指定的脚本路径
            # 如果都没有定义，报错

            if hasattr(skill, 'execution_rules') and skill.execution_rules:
                output, success = self._execute_with_rules(skill, params)
            elif skill.command:
                output, success = self._execute_command(skill, params)
            elif hasattr(skill, 'script_path') and skill.script_path:
                output, success = self._execute_script(skill, params)
            else:
                # 没有定义任何执行方式
                error = (
                    f"Skill '{skill.name}' has no execution method defined. "
                    f"Please specify one of: command, script, or execution_rules in skill.md"
                )
                if self.metrics_registry:
                    self.metrics_registry.notify_skill_complete(
                        execution_id,
                        success=False,
                        error_message=error
                    )
                logger.error(f"No execution method defined for skill '{skill.name}'")
                return error, False

            # 通知监控：执行完成
            if self.metrics_registry:
                self.metrics_registry.notify_skill_complete(
                    execution_id,
                    success=success,
                    error_message=None if success else output
                )

            if success:
                logger.info(f"Skill '{skill.name}' executed successfully")
            else:
                logger.error(f"Skill '{skill.name}' execution failed")

            return output, success

        except Exception as e:
            error = f"Unexpected error executing skill '{skill.name}': {str(e)}"
            if self.metrics_registry:
                self.metrics_registry.notify_skill_error(execution_id, e)
            logger.exception(f"Unexpected error executing skill '{skill.name}'")
            return error, False

    def _parse_command(self, cmd: str, params: Dict[str, Any]) -> List[str]:
        """安全解析命令字符串为参数列表（避免 shell=True）"""
        # 首先进行参数替换
        try:
            cmd = cmd.format(skill_dir="${_skill_dir_}", **params)
        except KeyError as e:
            return None

        # 替换 skill_dir 为实际路径
        cmd = cmd.replace("${_skill_dir_}", str(params.get("skill_dir", ".")))

        # 使用 shlex 分割命令（安全地处理引号）
        try:
            parsed = shlex.split(cmd)
            return parsed
        except ValueError as e:
            # 引号不匹配等错误
            return None

    def _execute_command(self, skill, params: Dict[str, Any]) -> Tuple[str, bool]:
        # 不需要添加 skill_dir 到参数，get_command 会使用 self.skill_dir
        cmd = skill.get_command(params)
        if not cmd:
            return "No command or script found", False

        # 解析命令为参数列表
        cmd_list = self._parse_command(cmd, params)
        if not cmd_list:
            return "Failed to parse command", False

        # 设置环境变量，确保子进程使用 UTF-8 编码
        import os
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            result = subprocess.run(
                cmd_list,
                shell=False,  # 使用 shell=False 避免命令注入
                capture_output=True,
                encoding='utf-8',  # 明确使用 UTF-8 编码
                errors='replace',  # 遇到无法解码的字符时替换为 ?
                timeout=skill.timeout or self.timeout,
                cwd=self.work_dir,
                env=env  # 传入环境变量
            )

            if result.returncode == 0:
                return result.stdout, True
            else:
                return result.stderr or result.stdout, False

        except subprocess.TimeoutExpired:
            return f"Execution timeout after {skill.timeout or self.timeout}s", False
        except Exception as e:
            return str(e), False

    def _apply_param_transforms(self, skill, params: Dict[str, Any]) -> Dict[str, Any]:
        """应用参数转换规则

        支持的转换类型：
        - read_file_bytes: 读取文件为 bytes（用于 {{content}} 占位符）
        - read_file_text: 读取文件为文本
        """
        if not hasattr(skill, 'param_transforms') or not skill.param_transforms:
            return params

        import os
        result = params.copy()

        for target_param, transform_config in skill.param_transforms.items():
            transform_type = transform_config.get("type")

            if transform_type == "read_file_bytes":
                # 读取文件为 bytes
                # source_param: 指定从哪个参数获取文件路径
                # 如果没有指定 source_param，则从 target_param 本身获取（假设它就是文件路径）
                source_param = transform_config.get("source_param", target_param)

                if source_param not in params:
                    # 源参数不存在，跳过转换
                    continue

                file_path = params[source_param]

                if isinstance(file_path, str):
                    # 如果是相对路径，先尝试相对于当前工作目录，找不到则相对于技能目录
                    if not os.path.isabs(file_path):
                        # 先尝试直接使用相对路径（相对于当前工作目录）
                        if os.path.exists(file_path):
                            abs_path = file_path
                        else:
                            # 如果不存在，尝试相对于技能目录
                            abs_path = str(skill.skill_dir / file_path)
                    else:
                        abs_path = file_path

                    try:
                        with open(abs_path, 'rb') as f:
                            result[target_param] = f.read()
                    except Exception as e:
                        result["_transform_error"] = f"Failed to read file {abs_path}: {e}"
                        return result

            elif transform_type == "read_file_text":
                # 读取文件为文本
                source_param = transform_config.get("source_param", target_param)
                encoding = transform_config.get("encoding", "utf-8")

                if source_param not in params:
                    continue

                file_path = params[source_param]

                if isinstance(file_path, str):
                    if not os.path.isabs(file_path):
                        if os.path.exists(file_path):
                            abs_path = file_path
                        else:
                            abs_path = str(skill.skill_dir / file_path)
                    else:
                        abs_path = file_path

                    try:
                        with open(abs_path, 'r', encoding=encoding) as f:
                            result[target_param] = f.read()
                    except Exception as e:
                        result["_transform_error"] = f"Failed to read file {abs_path}: {e}"
                        return result

        return result

    def _auto_infer_param_transforms(self, skill, params: Dict[str, Any]) -> Dict[str, Any]:
        """智能推断：自动检测脚本中的占位符，添加必要的参数转换

        例如：
        - 检测到 {{file_content}} → 自动从 file 参数读取文件内容
        - 检测到 {{file_text}} → 自动从 file 参数读取文件文本
        """
        import os
        import re

        result = params.copy()

        # 获取脚本文件路径
        script_file = skill.skill_dir / skill.script_path
        if not script_file.exists():
            return result

        # 读取脚本内容，检测占位符
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception:
            return result

        # 检测脚本中的占位符 {{param_name}}
        placeholders = re.findall(r'\{\{([a-zA-Z0-9_]+)\}\}', script_content)

        for placeholder in placeholders:
            # 如果参数已经存在，跳过
            if placeholder in result:
                continue

            # 智能推断占位符的来源
            # 规则1: file_content → 从 file 参数读取为 bytes
            if placeholder == "file_content" and "file" in params:
                file_path = params["file"]
                if isinstance(file_path, str):
                    if not os.path.isabs(file_path):
                        abs_path = file_path if os.path.exists(file_path) else str(skill.skill_dir / file_path)
                    else:
                        abs_path = file_path

                    try:
                        with open(abs_path, 'rb') as f:
                            result[placeholder] = f.read()
                        logger.info(f"Auto-inferred: read file content for '{placeholder}' from '{file_path}'")
                    except Exception as e:
                        logger.warning(f"Failed to auto-read file for '{placeholder}': {e}")

            # 规则2: file_text → 从 file 参数读取为文本
            elif placeholder == "file_text" and "file" in params:
                file_path = params["file"]
                if isinstance(file_path, str):
                    if not os.path.isabs(file_path):
                        abs_path = file_path if os.path.exists(file_path) else str(skill.skill_dir / file_path)
                    else:
                        abs_path = file_path

                    try:
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            result[placeholder] = f.read()
                        logger.info(f"Auto-inferred: read file text for '{placeholder}' from '{file_path}'")
                    except Exception as e:
                        logger.warning(f"Failed to auto-read file for '{placeholder}': {e}")

            # 规则3: {type}_content → 从 type 参数读取
            # 例如: pdf_content → 从 pdf 参数读取
            elif placeholder.endswith("_content"):
                source_param = placeholder[:-8]  # 去掉 _content 后缀
                if source_param in params:
                    source_value = params[source_param]
                    if isinstance(source_value, str) and source_param.endswith("file"):
                        # 是一个文件路径参数
                        if not os.path.isabs(source_value):
                            abs_path = source_value if os.path.exists(source_value) else str(skill.skill_dir / source_value)
                        else:
                            abs_path = source_value

                        try:
                            with open(abs_path, 'rb') as f:
                                result[placeholder] = f.read()
                            logger.info(f"Auto-inferred: read content for '{placeholder}' from '{source_value}'")
                        except Exception as e:
                            logger.warning(f"Failed to auto-read for '{placeholder}': {e}")

        return result

    def _execute_with_rules(self, skill, params: Dict[str, Any]) -> Tuple[str, bool]:
        """执行定义了 execution_rules 的多步骤技能"""
        execution_rules = skill.execution_rules
        if not execution_rules:
            return "No execution rules defined", False

        outputs = []

        # 按步骤顺序执行（step1, step2, step3...）
        sorted_steps = sorted(execution_rules.keys())

        for step_key in sorted_steps:
            step_config = execution_rules[step_key]
            if not isinstance(step_config, dict):
                continue

            # 获取步骤描述
            description = step_config.get("description", "")

            # 处理不同类型的动作
            if "script" in step_config:
                # 执行脚本
                script_output, success = self._execute_custom_script(skill, step_config["script"], params)
                if not success:
                    error_msg = step_config.get("error_message", f"Step {step_key} failed")
                    return f"{error_msg}\n{script_output}", False
                outputs.append(script_output)

            elif "action" in step_config:
                action = step_config["action"]
                if action == "check_file_suffix":
                    # 文件格式校验（自动从 permissions.read_file 提取允许的后缀）
                    file_path = params.get("file_path", "")

                    # 获取允许的文件后缀
                    if hasattr(skill, 'allowed_extensions') and skill.allowed_extensions:
                        valid = any(file_path.endswith(ext) for ext in skill.allowed_extensions)
                        if not valid:
                            ext_list = ", ".join(skill.allowed_extensions)
                            error_msg = step_config.get(
                                "error_message",
                                f"File format not supported. Allowed: {ext_list}"
                            )
                            return error_msg, False

        return "\n".join(outputs), True

    def _execute_custom_script(self, skill, script_template: str, params: Dict[str, Any]) -> Tuple[str, bool]:
        """执行自定义脚本

        Args:
            skill: 技能对象
            script_template: 脚本模板，如 "python scripts/read_md_file.py {{file_path}} --encoding={{encoding}}"
            params: 参数字典

        Returns:
            (output, success)
        """
        import re
        import os

        # 替换模板参数 {{param_name}}
        def replace_params(match):
            param_name = match.group(1)
            value = params.get(param_name, "")
            return str(value)

        # 处理 {{param}} 格式的参数（支持参数名包含字母、数字、下划线）
        script_cmd = re.sub(r'\{\{([a-zA-Z0-9_]+)\}\}', replace_params, script_template)

        # 检查是否还有未替换的 {{...}} 占位符
        if "{{" in script_cmd and "}}" in script_cmd:
            missing_params = re.findall(r'\{\{([a-zA-Z0-9_]+)\}\}', script_cmd)
            return f"Missing parameters: {', '.join(missing_params)}", False

        # 解析命令
        try:
            cmd_list = shlex.split(script_cmd)
        except ValueError as e:
            return f"Failed to parse script command: {e}", False

        # 获取脚本文件路径
        if len(cmd_list) < 2:
            return f"Invalid script command: {script_cmd}", False

        script_file = cmd_list[1]
        # 如果是相对路径，转换为相对于技能目录的绝对路径
        if not os.path.isabs(script_file):
            script_file = str(skill.skill_dir / script_file)

        if not os.path.exists(script_file):
            return f"Script not found: {script_file}", False

        # 读取脚本内容
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception as e:
            return f"Failed to read script: {e}", False

        # 检查脚本中是否有占位符需要替换
        has_placeholders = "{{" in script_content and "}}" in script_content

        script_to_execute = script_file
        temp_script_file = None

        if has_placeholders:
            # 检查是否需要导入 base64
            needs_base64 = False
            for param_name, param_value in params.items():
                if isinstance(param_value, bytes) and f"{{{param_name}}}" in script_content:
                    needs_base64 = True
                    break

            # 替换脚本中的占位符
            def replace_script_params(match):
                param_name = match.group(1)
                if param_name not in params:
                    raise ValueError(f"Missing parameter: {param_name}")

                value = params[param_name]

                # 根据参数类型处理
                if isinstance(value, bytes):
                    # 对于 bytes 类型，转换为 base64 编码的字符串
                    import base64
                    return f"base64.b64decode('{base64.b64encode(value).decode('ascii')}')"
                elif isinstance(value, str):
                    # 对于字符串，转义引号
                    return repr(value)
                else:
                    return str(value)

            # 替换脚本中的占位符
            try:
                script_content = re.sub(r'\{\{([a-zA-Z0-9_]+)\}\}', replace_script_params, script_content)
            except ValueError as e:
                return str(e), False

            # 如果需要 base64，在脚本开头添加 import
            if needs_base64:
                script_content = "import base64\n" + script_content

            # 创建临时脚本文件
            temp_script_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                dir=skill.skill_dir,
                encoding='utf-8',
                delete=False
            )
            temp_script_file.write(script_content)
            temp_script_file.close()
            script_to_execute = temp_script_file.name
            cmd_list[1] = script_to_execute

        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                encoding='utf-8',
                errors='replace',
                timeout=skill.timeout or self.timeout,
                cwd=skill.skill_dir,
                env=env
            )

            if result.returncode == 0:
                return result.stdout, True
            else:
                return result.stderr or result.stdout, False

        except subprocess.TimeoutExpired:
            return f"Script execution timeout after {skill.timeout or self.timeout}s", False
        except Exception as e:
            return str(e), False
        finally:
            # 清理临时文件
            if temp_script_file and os.path.exists(temp_script_file.name):
                try:
                    os.unlink(temp_script_file.name)
                except:
                    pass

    def _execute_script(self, skill, params: Dict[str, Any]) -> Tuple[str, bool]:
        """
        执行指定的脚本文件

        注意：script_path 必须在 skill.md 中定义，不再支持默认的 main.py
        """
        if not hasattr(skill, 'script_path') or not skill.script_path:
            return "Error: No script path defined in skill.md", False

        script_path = (skill.skill_dir / skill.script_path).resolve()

        if not script_path.exists():
            return f"Script not found: {script_path}", False

        # 读取脚本内容
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # 检查是否需要模板替换（查找 {{param_name}} 占位符）
        import re
        needs_template = bool(re.search(r'\{\{\w+\}\}', script_content))

        actual_script_path = script_path
        if needs_template:
            # 进行模板替换
            for key, value in params.items():
                placeholder = f"{{{{{key}}}}}"
                script_content = script_content.replace(placeholder, repr(value))

            # 写入临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(script_content)
                actual_script_path = Path(f.name)

        cmd = ["python", str(actual_script_path)]
        # 只在不需要模板替换时传递命令行参数
        if not needs_template:
            for key, value in params.items():
                # 检查参数类型（从 skill.inputs 中获取）
                input_spec = None
                if hasattr(skill, 'inputs') and key in skill.inputs:
                    input_spec = skill.inputs[key]

                # 布尔类型参数特殊处理
                if input_spec and input_spec.type == "boolean":
                    # 布尔值 true: 传递 --flag
                    # 布尔值 false: 传递 --no_flag（如果存在）或不传递
                    bool_value = str(value).lower() in ("true", "1", "yes")
                    if bool_value:
                        cmd.append(f"--{key}")
                    else:
                        # 尝试 --no_key 格式
                        cmd.append(f"--no_{key}")
                else:
                    # 非布尔参数，正常传递
                    cmd.extend([f"--{key}", str(value)])

        logger.debug(f"Executing command: {cmd}")

        # 设置环境变量，确保子进程使用 UTF-8 编码
        import os
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding='utf-8',  # 明确使用 UTF-8 编码
                errors='replace',  # 遇到无法解码的字符时替换为 ?
                timeout=skill.timeout or self.timeout,
                cwd=None,  # 使用当前工作目录，而不是 skill.skill_dir
                env=env  # 传入环境变量
            )

            if result.returncode == 0:
                return result.stdout, True
            else:
                return result.stderr or result.stdout, False

        except subprocess.TimeoutExpired:
            return f"Execution timeout after {skill.timeout or self.timeout}s", False
        except Exception as e:
            return str(e), False
        finally:
            # 清理临时文件
            if needs_template and actual_script_path != script_path:
                try:
                    actual_script_path.unlink()
                except:
                    pass

    def install_dependencies(self, dependencies: list) -> Tuple[bool, str]:
        """
        安装依赖包（使用 DependencyManager 进行版本冲突检查）

        Args:
            dependencies: 依赖列表（如 ["pandas>=1.5.0", "numpy"]）

        Returns:
            (success, message) 成功状态和消息
        """
        if not dependencies:
            return True, "No dependencies to install"

        # 使用 DependencyManager 处理依赖安装
        manager = DependencyManager(auto_install=self.auto_install_deps, timeout=300)
        return manager.install_dependencies(dependencies)
