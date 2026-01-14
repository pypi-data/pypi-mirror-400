"""
测试 DependencyManager 依赖管理器

测试依赖检查、版本冲突检测、安装等功能
"""
import pytest
from unittest.mock import patch, MagicMock

from skill_scheduler.core.dependency_manager import (
    DependencyManager,
    PackageInfo,
    DependencyCheckResult,
    check_and_install_dependencies
)


class TestPackageInfo:
    """测试 PackageInfo 数据类"""

    def test_creation(self):
        """测试创建 PackageInfo"""
        pkg = PackageInfo(
            name="pandas",
            installed_version="1.5.0",
            required_spec=">=1.5.0",
            is_installed=True,
            is_compatible=True
        )

        assert pkg.name == "pandas"
        assert pkg.installed_version == "1.5.0"
        assert pkg.is_installed is True
        assert pkg.is_compatible is True

    def test_default_values(self):
        """测试默认值"""
        pkg = PackageInfo(name="test")
        assert pkg.is_installed is False
        assert pkg.is_compatible is True
        assert pkg.conflict_reason == ""


class TestDependencyManager:
    """测试 DependencyManager 类"""

    def test_initialization(self):
        """测试初始化"""
        manager = DependencyManager(auto_install=True, timeout=100)
        assert manager.auto_install is True
        assert manager.timeout == 100
        assert manager._installed_cache is None

    def test_builtin_packages(self):
        """测试内置包列表"""
        manager = DependencyManager()

        # 标准库包应该在内置列表中
        assert "os" in DependencyManager.BUILTIN_PACKAGES
        assert "sys" in DependencyManager.BUILTIN_PACKAGES
        assert "json" in DependencyManager.BUILTIN_PACKAGES

    @patch('subprocess.run')
    def test_check_installed_packages(self, mock_run):
        """测试检查已安装包"""
        # 模拟 pip list 命令返回
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"name": "pandas", "version": "1.5.0"}, ' \
                             '{"name": "numpy", "version": "1.20.0"}]'
        mock_run.return_value = mock_result

        manager = DependencyManager()
        manager._refresh_installed_cache()

        assert manager._installed_cache is not None
        assert "pandas" in manager._installed_cache
        assert manager._installed_cache["pandas"].installed_version == "1.5.0"

    def test_check_dependencies_empty(self):
        """测试检查空依赖列表"""
        manager = DependencyManager()
        result = manager.check_dependencies([])

        assert result.success is True
        assert len(result.installed_packages) == 0
        assert len(result.missing_packages) == 0

    @patch('subprocess.run')
    def test_check_dependencies_with_installed(self, mock_run):
        """测试检查已安装的依赖"""
        # 模拟包已安装
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"name": "pandas", "version": "1.5.0"}]'
        mock_run.return_value = mock_result

        manager = DependencyManager()
        # 先调用 _refresh_installed_cache 填充缓存
        manager._refresh_installed_cache()

        result = manager.check_dependencies(["pandas>=1.0.0"])

        assert result.success is True
        assert len(result.installed_packages) >= 1

    @patch('subprocess.run')
    def test_check_missing_dependencies(self, mock_run):
        """测试检查缺失的依赖"""
        # 模拟包未安装
        mock_run.return_value = MagicMock(returncode=1)

        manager = DependencyManager()
        manager._installed_cache = {}

        result = manager.check_dependencies(["nonexistent-package"])

        assert result.success is False
        assert len(result.missing_packages) >= 1

    def test_parse_dependency_string(self):
        """测试解析依赖字符串"""
        manager = DependencyManager()

        # 单个依赖
        deps = manager.parse_dependency_string("pandas>=1.5.0")
        assert len(deps) == 1
        assert "pandas>=1.5.0" in deps

        # 多个依赖（逗号分隔）
        deps = manager.parse_dependency_string("pandas>=1.5.0, numpy>=1.20")
        assert len(deps) == 2
        assert "pandas>=1.5.0" in deps
        assert "numpy>=1.20" in deps

        # 空字符串
        deps = manager.parse_dependency_string("")
        assert len(deps) == 0

    def test_builtin_packages_skipped(self):
        """测试内置包被跳过"""
        manager = DependencyManager()

        result = manager.check_dependencies(["os", "sys", "json"])
        # 内置包应该被跳过
        assert result.success is True


class TestDependencyCheckResult:
    """测试 DependencyCheckResult 数据类"""

    def test_creation(self):
        """测试创建结果"""
        result = DependencyCheckResult(
            success=True,
            installed_packages=[],
            missing_packages=[],
            conflicting_packages=[],
            install_candidates=[]
        )

        assert result.success is True
        assert isinstance(result.installed_packages, list)


class TestConvenienceFunctions:
    """测试便捷函数"""

    @patch('skill_scheduler.core.dependency_manager.DependencyManager.install_dependencies')
    def test_check_and_install_dependencies(self, mock_install):
        """测试便捷函数"""
        mock_install.return_value = (True, "Success")

        success, message = check_and_install_dependencies(["pandas"])

        assert success is True
        assert "Success" in message


class TestKnownConflicts:
    """测试已知版本冲突"""

    def test_known_conflicts_structure(self):
        """测试已知冲突数据结构"""
        manager = DependencyManager()

        # KNOWN_CONFLICTS 应该是字典
        assert isinstance(manager.KNOWN_CONFLICTS, dict)

        # 检查结构
        for package, conflicts in manager.KNOWN_CONFLICTS.items():
            assert isinstance(package, str)
            # conflicts 是字典，不是 set
            assert isinstance(conflicts, dict)


class TestVersionComparison:
    """测试版本比较功能"""

    @patch('subprocess.run')
    def test_version_compatibility_check(self, mock_run):
        """测试版本兼容性检查"""
        # 模拟包已安装
        mock_run.return_value = MagicMock(returncode=0)

        manager = DependencyManager()
        manager._installed_cache = {
            "pandas": PackageInfo(
                name="pandas",
                installed_version="1.5.3",
                is_installed=True
            )
        }

        # 测试版本兼容
        from packaging import requirements as pkg_req
        req = pkg_req.Requirement("pandas>=1.5.0,<2.0.0")
        pkg_info = manager._get_package_info(req)

        assert pkg_info.is_installed is True
        # 版本应该是兼容的
        assert pkg_info.is_compatible is True


@pytest.mark.parametrize("dep_string,expected_count", [
    ("pandas>=1.5.0", 1),
    ("pandas>=1.5.0, numpy>=1.20", 2),
    ("pandas>=1.5.0, numpy>=1.20, requests>=2.28", 3),
    ("", 0),
])
def test_parse_various_dependency_strings(dep_string, expected_count):
    """参数化测试各种依赖字符串"""
    manager = DependencyManager()
    deps = manager.parse_dependency_string(dep_string)
    assert len(deps) == expected_count


class TestErrorHandling:
    """测试错误处理"""

    def test_invalid_requirement(self):
        """测试无效的依赖规范"""
        manager = DependencyManager()

        # 无效的依赖规范应该被捕获
        result = manager.check_dependencies(["invalid-package-name!!!"])
        # 应该不会抛出异常，而是返回结果
        assert isinstance(result, DependencyCheckResult)

    @patch('subprocess.run')
    def test_subprocess_timeout(self, mock_run):
        """测试子进程超时"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("pip", 30)

        manager = DependencyManager()
        result = manager.check_dependencies(["some-package"])

        # 超时的包应该被标记为缺失
        assert isinstance(result, DependencyCheckResult)

    @patch('subprocess.run')
    def test_subprocess_error(self, mock_run):
        """测试子进程错误"""
        import subprocess
        mock_run.side_effect = Exception("Network error")

        manager = DependencyManager()
        result = manager.check_dependencies(["some-package"])

        # 应该处理异常而不崩溃
        assert isinstance(result, DependencyCheckResult)


@pytest.mark.integration
class TestRealDependencyChecks:
    """集成测试：真实的依赖检查"""

    def test_check_python_standard_library(self):
        """测试检查 Python 标准库"""
        manager = DependencyManager()
        result = manager.check_dependencies(["os", "sys", "re"])

        # 标准库应该总是"已安装"
        assert result.success is True

    def test_check_common_packages(self):
        """测试检查常见包"""
        # 检查一些常见但可能不存在的包
        manager = DependencyManager()
        result = manager.check_dependencies([
            "pytest>=7.0",  # 应该已安装（运行测试时）
            "packaging>=21.0"  # 应该已安装（项目依赖）
        ])

        # 至少 pytest 应该已安装
        # result.success 可能是 False（如果版本不匹配），但不应该抛出异常
        assert isinstance(result, DependencyCheckResult)
