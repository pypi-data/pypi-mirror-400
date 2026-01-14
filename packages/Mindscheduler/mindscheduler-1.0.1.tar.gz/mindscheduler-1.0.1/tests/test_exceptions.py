"""
测试结构化异常处理

测试 SkillError、ErrorHandler 和相关功能
"""
import pytest

from skill_scheduler.core.exceptions import (
    ErrorCategory,
    SkillError,
    ErrorHandler,
    create_error_result,
    handle_exception,
    ERROR_MESSAGES
)


class TestErrorCategory:
    """测试 ErrorCategory 枚举"""

    def test_all_categories_exist(self):
        """测试所有预期的错误类别都存在"""
        # 技能相关
        assert ErrorCategory.SKILL_NOT_FOUND
        assert ErrorCategory.SKILL_INVALID
        assert ErrorCategory.SKILL_EXECUTION_FAILED

        # 参数相关
        assert ErrorCategory.PARAM_MISSING
        assert ErrorCategory.PARAM_INVALID

        # 权限相关
        assert ErrorCategory.PERMISSION_DENIED
        assert ErrorCategory.FILE_ACCESS_DENIED

        # 依赖相关
        assert ErrorCategory.DEPENDENCY_MISSING
        assert ErrorCategory.DEPENDENCY_VERSION_CONFLICT

        # 执行相关
        assert ErrorCategory.EXECUTION_TIMEOUT
        assert ErrorCategory.SCRIPT_NOT_FOUND

    def test_category_values(self):
        """测试错误类别值"""
        assert ErrorCategory.SKILL_NOT_FOUND.value == "skill_not_found"
        assert ErrorCategory.PARAM_MISSING.value == "param_missing"


class TestSkillError:
    """测试 SkillError 数据类"""

    def test_creation(self):
        """测试创建 SkillError"""
        error = SkillError(
            category=ErrorCategory.SKILL_NOT_FOUND,
            details={"skill_name": "test-skill"}
        )

        assert error.category == ErrorCategory.SKILL_NOT_FOUND
        assert error.code == "skill_not_found"
        assert error.details["skill_name"] == "test-skill"

    def test_auto_message_generation(self):
        """测试自动生成错误消息"""
        error = SkillError(
            category=ErrorCategory.PARAM_MISSING,
            details={"param_name": "file"},
            language="zh_CN"
        )

        assert "file" in error.message
        assert error.message is not None

    def test_english_message(self):
        """测试英文错误消息"""
        error = SkillError(
            category=ErrorCategory.SKILL_NOT_FOUND,
            details={"skill_name": "test"},
            language="en_US"
        )

        assert "not found" in error.message.lower()

    def test_chinese_message(self):
        """测试中文错误消息"""
        error = SkillError(
            category=ErrorCategory.SKILL_NOT_FOUND,
            details={"skill_name": "test"},
            language="zh_CN"
        )

        assert "未找到" in error.message or "找不到" in error.message

    def test_to_dict(self):
        """测试转换为字典"""
        error = SkillError(
            category=ErrorCategory.SKILL_NOT_FOUND,
            details={"skill_name": "test"},
            suggestions=["使用 list_skills()"]
        )

        error_dict = error.to_dict()

        assert error_dict["success"] is False
        assert error_dict["error"] == "skill_not_found"
        assert "message" in error_dict
        assert "suggestions" in error_dict

    def test_str_representation(self):
        """测试字符串表示"""
        error = SkillError(
            category=ErrorCategory.PARAM_MISSING,
            details={"param_name": "file"}
        )

        str_repr = str(error)
        assert str_repr is not None
        assert len(str_repr) > 0

    def test_repr(self):
        """测试调试表示"""
        error = SkillError(
            category=ErrorCategory.SKILL_NOT_FOUND,
            details={"skill_name": "test"}
        )

        repr_str = repr(error)
        assert "SkillError" in repr_str
        assert "skill_not_found" in repr_str

    def test_with_cause(self):
        """测试带原始异常的错误"""
        original_error = ValueError("Something went wrong")
        error = SkillError(
            category=ErrorCategory.PARAM_INVALID,
            details={"param_name": "test"},
            cause=original_error
        )

        error_dict = error.to_dict()
        assert "cause" in error_dict


class TestErrorHandler:
    """测试 ErrorHandler 类"""

    def test_skill_not_found(self):
        """测试技能未找到错误"""
        error = ErrorHandler.skill_not_found(
            skill_name="non-existent",
            available_skills=["skill1", "skill2"]
        )

        assert error.category == ErrorCategory.SKILL_NOT_FOUND
        assert error.details["skill_name"] == "non-existent"
        assert len(error.suggestions) > 0

    def test_param_missing(self):
        """测试参数缺失错误"""
        error = ErrorHandler.param_missing(
            param_name="file",
            skill_name="file-reader"
        )

        assert error.category == ErrorCategory.PARAM_MISSING
        assert error.details["param_name"] == "file"
        assert len(error.suggestions) > 0

    def test_param_invalid(self):
        """测试参数无效错误"""
        error = ErrorHandler.param_invalid(
            param_name="count",
            reason="must be a positive integer"
        )

        assert error.category == ErrorCategory.PARAM_INVALID
        assert "count" in error.details["param_name"]

    def test_permission_denied(self):
        """测试权限拒绝错误"""
        error = ErrorHandler.permission_denied(
            resource="/etc/passwd",
            reason="Access denied"
        )

        assert error.category == ErrorCategory.PERMISSION_DENIED

    def test_execution_failed(self):
        """测试执行失败错误"""
        error = ErrorHandler.execution_failed(
            skill_name="test-skill",
            reason="Script not found"
        )

        assert error.category == ErrorCategory.SKILL_EXECUTION_FAILED
        assert error.details["skill_name"] == "test-skill"

    def test_dependency_conflict(self):
        """测试依赖冲突错误"""
        error = ErrorHandler.dependency_conflict(
            package_name="pandas",
            reason="Requires numpy<1.20, but 1.21 is installed"
        )

        assert error.category == ErrorCategory.DEPENDENCY_VERSION_CONFLICT
        assert len(error.suggestions) > 0

    def test_execution_timeout(self):
        """测试执行超时错误"""
        error = ErrorHandler.execution_timeout(timeout=30)

        assert error.category == ErrorCategory.EXECUTION_TIMEOUT
        assert error.details["timeout"] == 30

    def test_from_exception_file_not_found(self):
        """测试从 FileNotFoundError 创建错误"""
        exc = FileNotFoundError("script.py not found")
        error = ErrorHandler.from_exception(exc)

        assert error.category == ErrorCategory.SCRIPT_NOT_FOUND
        assert error.cause == exc

    def test_from_exception_permission_error(self):
        """测试从 PermissionError 创建错误"""
        exc = PermissionError("Access denied")
        error = ErrorHandler.from_exception(exc)

        assert error.category == ErrorCategory.PERMISSION_DENIED

    def test_from_exception_timeout_error(self):
        """测试从 TimeoutError 创建错误"""
        exc = TimeoutError("Operation timed out")
        error = ErrorHandler.from_exception(exc)

        assert error.category == ErrorCategory.EXECUTION_TIMEOUT

    def test_from_exception_value_error(self):
        """测试从 ValueError 创建错误"""
        exc = ValueError("Invalid value")
        error = ErrorHandler.from_exception(exc)

        assert error.category == ErrorCategory.PARAM_INVALID

    def test_from_exception_type_error(self):
        """测试从 TypeError 创建错误"""
        exc = TypeError("Wrong type")
        error = ErrorHandler.from_exception(exc)

        assert error.category == ErrorCategory.PARAM_TYPE_ERROR

    def test_from_exception_unknown(self):
        """测试从未知异常创建错误"""
        exc = RuntimeError("Something unexpected")
        error = ErrorHandler.from_exception(exc)

        assert error.category == ErrorCategory.UNKNOWN_ERROR
        assert error.cause == exc

    def test_set_language(self):
        """测试设置默认语言"""
        ErrorHandler.set_language("en_US")
        error = ErrorHandler.skill_not_found("test")
        assert error.language == "en_US"

        # 重置为中文
        ErrorHandler.set_language("zh_CN")


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_create_error_result(self):
        """测试创建错误结果字典"""
        error = ErrorHandler.skill_not_found("test")
        result = create_error_result(error)

        assert result["success"] is False
        assert "error" in result
        assert "message" in result

    def test_handle_exception(self):
        """测试处理异常"""
        exc = FileNotFoundError("test.txt")
        result = handle_exception(exc, context={"operation": "read"})

        assert result["success"] is False
        assert "error" in result
        assert result.get("context", {}).get("operation") == "read"


class TestErrorMessages:
    """测试错误消息模板"""

    def test_error_messages_structure(self):
        """测试错误消息模板结构"""
        assert "zh_CN" in ERROR_MESSAGES
        assert "en_US" in ERROR_MESSAGES

    def test_all_categories_have_messages(self):
        """测试所有类别都有中英文消息"""
        categories = [
            ErrorCategory.SKILL_NOT_FOUND,
            ErrorCategory.PARAM_MISSING,
            ErrorCategory.PERMISSION_DENIED,
            ErrorCategory.EXECUTION_TIMEOUT,
        ]

        for category in categories:
            # 中文
            assert category in ERROR_MESSAGES["zh_CN"]
            # 英文
            assert category in ERROR_MESSAGES["en_US"]

    def test_message_templates_have_placeholders(self):
        """测试消息模板包含占位符"""
        # 检查一些关键模板
        zh_msg = ERROR_MESSAGES["zh_CN"][ErrorCategory.SKILL_NOT_FOUND]
        assert "{skill_name}" in zh_msg

        en_msg = ERROR_MESSAGES["en_US"][ErrorCategory.PARAM_MISSING]
        assert "{param_name}" in en_msg


@pytest.mark.parametrize("category,detail_key,detail_value,language", [
    (ErrorCategory.SKILL_NOT_FOUND, "skill_name", "test", "zh_CN"),
    (ErrorCategory.SKILL_NOT_FOUND, "skill_name", "test", "en_US"),
    (ErrorCategory.PARAM_MISSING, "param_name", "file", "zh_CN"),
    (ErrorCategory.PARAM_MISSING, "param_name", "file", "en_US"),
])
def test_error_message_formatting(category, detail_key, detail_value, language):
    """参数化测试错误消息格式化"""
    error = SkillError(
        category=category,
        details={detail_key: detail_value},
        language=language
    )

    assert error.message is not None
    assert len(error.message) > 0
    # 检查占位符被替换
    assert "{" not in error.message


class TestErrorPropagation:
    """测试错误传播"""

    def test_error_with_suggestions(self):
        """测试带建议的错误"""
        error = ErrorHandler.skill_not_found(
            skill_name="test",
            available_skills=["skill1", "skill2", "skill3"]
        )

        error_dict = error.to_dict()
        assert "suggestions" in error_dict
        assert len(error_dict["suggestions"]) > 0

    def test_error_with_context(self):
        """测试带上下文的错误"""
        error = ErrorHandler.execution_failed(
            skill_name="test",
            reason="Script error",
            language="zh_CN"
        )
        error.context["timestamp"] = "2024-01-01"
        error.context["user"] = "test_user"

        error_dict = error.to_dict()
        assert "context" in error_dict
        assert error_dict["context"]["timestamp"] == "2024-01-01"


@pytest.mark.integration
class TestErrorIntegration:
    """集成测试：错误在实际使用中的场景"""

    def test_scheduler_error_response_format(self, sample_scheduler):
        """测试调度器错误响应格式"""
        result = sample_scheduler.run("non-existent-skill", {})

        assert result["success"] is False
        assert "error" in result or "category" in result
        assert "message" in result

    def test_error_in_exception_handling(self):
        """测试异常处理中的错误"""
        try:
            raise FileNotFoundError("test.txt not found")
        except Exception as e:
            result = handle_exception(e)
            assert result["success"] is False
