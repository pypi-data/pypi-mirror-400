"""
结构化错误信息 - 支持错误分类、错误码、国际化

提供统一的错误处理接口，便于国际化支持和错误追踪。
"""
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """错误类别"""
    # 技能相关错误
    SKILL_NOT_FOUND = "skill_not_found"
    SKILL_INVALID = "skill_invalid"
    SKILL_EXECUTION_FAILED = "skill_execution_failed"

    # 参数相关错误
    PARAM_MISSING = "param_missing"
    PARAM_INVALID = "param_invalid"
    PARAM_TYPE_ERROR = "param_type_error"

    # 权限相关错误
    PERMISSION_DENIED = "permission_denied"
    FILE_ACCESS_DENIED = "file_access_denied"
    NETWORK_ACCESS_DENIED = "network_access_denied"

    # 依赖相关错误
    DEPENDENCY_MISSING = "dependency_missing"
    DEPENDENCY_VERSION_CONFLICT = "dependency_version_conflict"
    DEPENDENCY_INSTALL_FAILED = "dependency_install_failed"

    # 执行相关错误
    EXECUTION_TIMEOUT = "execution_timeout"
    SCRIPT_NOT_FOUND = "script_not_found"
    COMMAND_PARSE_FAILED = "command_parse_failed"

    # 匹配相关错误
    NO_MATCHING_SKILL = "no_matching_skill"
    LLM_PARSE_FAILED = "llm_parse_failed"

    # 配置相关错误
    CONFIG_INVALID = "config_invalid"
    CONFIG_MISSING = "config_missing"

    # 系统错误
    INTERNAL_ERROR = "internal_error"
    UNKNOWN_ERROR = "unknown_error"


# 错误消息模板（支持多语言）
ERROR_MESSAGES = {
    "zh_CN": {
        ErrorCategory.SKILL_NOT_FOUND: "技能 '{skill_name}' 未找到",
        ErrorCategory.SKILL_INVALID: "技能 '{skill_name}' 配置无效: {reason}",
        ErrorCategory.SKILL_EXECUTION_FAILED: "技能 '{skill_name}' 执行失败: {reason}",

        ErrorCategory.PARAM_MISSING: "缺少必需参数: {param_name}",
        ErrorCategory.PARAM_INVALID: "参数 '{param_name}' 无效: {reason}",
        ErrorCategory.PARAM_TYPE_ERROR: "参数 '{param_name}' 类型错误，期望 {expected_type}，实际 {actual_type}",

        ErrorCategory.PERMISSION_DENIED: "权限被拒绝: {reason}",
        ErrorCategory.FILE_ACCESS_DENIED: "文件访问被拒绝: {file_path} 不在白名单中",
        ErrorCategory.NETWORK_ACCESS_DENIED: "网络访问被拒绝",

        ErrorCategory.DEPENDENCY_MISSING: "缺少依赖: {package_name}",
        ErrorCategory.DEPENDENCY_VERSION_CONFLICT: "依赖版本冲突: {package_name} ({reason})",
        ErrorCategory.DEPENDENCY_INSTALL_FAILED: "依赖安装失败: {package_name} - {reason}",

        ErrorCategory.EXECUTION_TIMEOUT: "执行超时 ({timeout}秒)",
        ErrorCategory.SCRIPT_NOT_FOUND: "脚本未找到: {script_path}",
        ErrorCategory.COMMAND_PARSE_FAILED: "命令解析失败: {reason}",

        ErrorCategory.NO_MATCHING_SKILL: "未找到匹配的技能",
        ErrorCategory.LLM_PARSE_FAILED: "LLM 解析失败: {reason}",

        ErrorCategory.CONFIG_INVALID: "配置无效: {reason}",
        ErrorCategory.CONFIG_MISSING: "缺少配置: {config_name}",

        ErrorCategory.INTERNAL_ERROR: "内部错误: {reason}",
        ErrorCategory.UNKNOWN_ERROR: "未知错误: {reason}",
    },
    "en_US": {
        ErrorCategory.SKILL_NOT_FOUND: "Skill '{skill_name}' not found",
        ErrorCategory.SKILL_INVALID: "Skill '{skill_name}' is invalid: {reason}",
        ErrorCategory.SKILL_EXECUTION_FAILED: "Skill '{skill_name}' execution failed: {reason}",

        ErrorCategory.PARAM_MISSING: "Missing required parameter: {param_name}",
        ErrorCategory.PARAM_INVALID: "Invalid parameter '{param_name}': {reason}",
        ErrorCategory.PARAM_TYPE_ERROR: "Parameter '{param_name}' type error, expected {expected_type}, got {actual_type}",

        ErrorCategory.PERMISSION_DENIED: "Permission denied: {reason}",
        ErrorCategory.FILE_ACCESS_DENIED: "File access denied: {file_path} not in whitelist",
        ErrorCategory.NETWORK_ACCESS_DENIED: "Network access denied",

        ErrorCategory.DEPENDENCY_MISSING: "Missing dependency: {package_name}",
        ErrorCategory.DEPENDENCY_VERSION_CONFLICT: "Dependency version conflict: {package_name} ({reason})",
        ErrorCategory.DEPENDENCY_INSTALL_FAILED: "Dependency installation failed: {package_name} - {reason}",

        ErrorCategory.EXECUTION_TIMEOUT: "Execution timeout ({timeout}s)",
        ErrorCategory.SCRIPT_NOT_FOUND: "Script not found: {script_path}",
        ErrorCategory.COMMAND_PARSE_FAILED: "Command parse failed: {reason}",

        ErrorCategory.NO_MATCHING_SKILL: "No matching skill found",
        ErrorCategory.LLM_PARSE_FAILED: "LLM parse failed: {reason}",

        ErrorCategory.CONFIG_INVALID: "Invalid configuration: {reason}",
        ErrorCategory.CONFIG_MISSING: "Missing configuration: {config_name}",

        ErrorCategory.INTERNAL_ERROR: "Internal error: {reason}",
        ErrorCategory.UNKNOWN_ERROR: "Unknown error: {reason}",
    },
}


@dataclass
class SkillError:
    """
    结构化错误信息

    Attributes:
        category: 错误类别
        code: 错误码（自动从 category 生成）
        message: 错误消息（根据语言环境自动生成）
        details: 错误详细信息
        context: 错误上下文信息
        suggestions: 解决建议
        language: 语言环境 (zh_CN, en_US)
        cause: 原始异常（如果有）
    """
    category: ErrorCategory
    details: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    language: str = "zh_CN"
    cause: Optional[Exception] = None

    def __post_init__(self):
        """自动生成错误码和消息"""
        self.code = self.category.value

        # 生成错误消息
        if not hasattr(self, '_message'):
            self._message = self._generate_message()

    @property
    def message(self) -> str:
        """获取格式化的错误消息"""
        return self._generate_message()

    def _generate_message(self) -> str:
        """根据错误类别和详细信息生成消息"""
        # 获取消息模板
        lang = self.language if self.language in ERROR_MESSAGES else "zh_CN"
        template = ERROR_MESSAGES[lang].get(self.category)

        if not template:
            # 回退到英文
            template = ERROR_MESSAGES["en_US"].get(self.category, str(self.category.value))

        try:
            # 使用 details 填充模板
            return template.format(**self.details)
        except KeyError as e:
            # 模板填充失败，返回基础消息
            logger.warning(f"Failed to format error message: {e}, template: {template}, details: {self.details}")
            return template

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            包含所有错误信息的字典
        """
        result = {
            "success": False,
            "error": self.code,
            "category": self.category.name,
            "message": self.message,
        }

        if self.details:
            result["details"] = self.details

        if self.context:
            result["context"] = self.context

        if self.suggestions:
            result["suggestions"] = self.suggestions

        if self.cause:
            result["cause"] = str(self.cause)

        return result

    def __str__(self) -> str:
        """字符串表示"""
        return self.message

    def __repr__(self) -> str:
        """调试表示"""
        return f"SkillError(category={self.category.name}, code={self.code}, message='{self.message}')"


class ErrorHandler:
    """
    错误处理器

    提供便捷的错误创建和处理方法
    """

    # 默认语言环境
    DEFAULT_LANGUAGE = "zh_CN"

    @classmethod
    def set_language(cls, language: str):
        """设置默认语言环境"""
        cls.DEFAULT_LANGUAGE = language

    @classmethod
    def skill_not_found(
        cls,
        skill_name: str,
        available_skills: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> SkillError:
        """创建技能未找到错误"""
        suggestions = []
        if available_skills:
            suggestions = [
                f"可用技能: {', '.join(available_skills[:5])}",
                "使用 list_skills() 查看所有可用技能"
            ]

        return SkillError(
            category=ErrorCategory.SKILL_NOT_FOUND,
            details={"skill_name": skill_name},
            context={"available_skills": available_skills} if available_skills else {},
            suggestions=suggestions,
            language=language or cls.DEFAULT_LANGUAGE
        )

    @classmethod
    def param_missing(
        cls,
        param_name: str,
        skill_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> SkillError:
        """创建参数缺失错误"""
        suggestions = [f"请提供参数: {param_name}"]
        if skill_name:
            suggestions.append(f"使用 get_skill_info('{skill_name}') 查看参数说明")

        return SkillError(
            category=ErrorCategory.PARAM_MISSING,
            details={"param_name": param_name},
            context={"skill_name": skill_name} if skill_name else {},
            suggestions=suggestions,
            language=language or cls.DEFAULT_LANGUAGE
        )

    @classmethod
    def param_invalid(
        cls,
        param_name: str,
        reason: str,
        language: Optional[str] = None
    ) -> SkillError:
        """创建参数无效错误"""
        return SkillError(
            category=ErrorCategory.PARAM_INVALID,
            details={"param_name": param_name, "reason": reason},
            suggestions=[f"检查参数 '{param_name}' 的值是否正确"],
            language=language or cls.DEFAULT_LANGUAGE
        )

    @classmethod
    def permission_denied(
        cls,
        resource: str,
        reason: Optional[str] = None,
        language: Optional[str] = None
    ) -> SkillError:
        """创建权限拒绝错误"""
        return SkillError(
            category=ErrorCategory.PERMISSION_DENIED,
            details={"reason": reason or f"访问 '{resource}' 被拒绝"},
            suggestions=["检查 skill.md 中的 permissions 配置"],
            language=language or cls.DEFAULT_LANGUAGE
        )

    @classmethod
    def execution_failed(
        cls,
        skill_name: str,
        reason: str,
        cause: Optional[Exception] = None,
        language: Optional[str] = None
    ) -> SkillError:
        """创建执行失败错误"""
        return SkillError(
            category=ErrorCategory.SKILL_EXECUTION_FAILED,
            details={"skill_name": skill_name, "reason": reason},
            suggestions=[
                "检查技能脚本是否存在",
                "查看详细日志了解失败原因"
            ],
            cause=cause,
            language=language or cls.DEFAULT_LANGUAGE
        )

    @classmethod
    def dependency_conflict(
        cls,
        package_name: str,
        reason: str,
        language: Optional[str] = None
    ) -> SkillError:
        """创建依赖冲突错误"""
        return SkillError(
            category=ErrorCategory.DEPENDENCY_VERSION_CONFLICT,
            details={"package_name": package_name, "reason": reason},
            suggestions=[
                f"更新或降级 {package_name} 版本",
                "检查依赖版本兼容性"
            ],
            language=language or cls.DEFAULT_LANGUAGE
        )

    @classmethod
    def execution_timeout(
        cls,
        timeout: int,
        language: Optional[str] = None
    ) -> SkillError:
        """创建执行超时错误"""
        return SkillError(
            category=ErrorCategory.EXECUTION_TIMEOUT,
            details={"timeout": timeout},
            suggestions=[
                "增加 timeout 配置",
                "优化脚本执行时间"
            ],
            language=language or cls.DEFAULT_LANGUAGE
        )

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        language: Optional[str] = None
    ) -> SkillError:
        """从异常创建错误"""
        # 根据异常类型映射到错误类别
        error_map = {
            FileNotFoundError: ErrorCategory.SCRIPT_NOT_FOUND,
            PermissionError: ErrorCategory.PERMISSION_DENIED,
            TimeoutError: ErrorCategory.EXECUTION_TIMEOUT,
            ValueError: ErrorCategory.PARAM_INVALID,
            TypeError: ErrorCategory.PARAM_TYPE_ERROR,
        }

        exc_type = type(exc)
        category = error_map.get(exc_type, ErrorCategory.UNKNOWN_ERROR)

        return SkillError(
            category=category,
            details={"reason": str(exc)},
            cause=exc,
            language=language or cls.DEFAULT_LANGUAGE
        )


def create_error_result(error: SkillError) -> Dict[str, Any]:
    """
    创建标准格式的错误结果字典

    Args:
        error: SkillError 对象

    Returns:
        标准格式的错误结果字典
    """
    return error.to_dict()


def handle_exception(
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    处理异常并返回标准格式错误

    Args:
        exc: 异常对象
        context: 额外的上下文信息
        language: 语言环境

    Returns:
        标准格式的错误结果字典
    """
    error = ErrorHandler.from_exception(exc, language=language)
    if context:
        error.context.update(context)

    return error.to_dict()
