"""
依赖管理器 - 处理 Python 包的安装和版本冲突检查

支持版本规范解析、版本冲突检测、自动安装等功能。
"""
import subprocess
import re
import logging
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from packaging import version as pkg_version
from packaging import requirements as pkg_req


logger = logging.getLogger(__name__)


@dataclass
class PackageInfo:
    """包信息"""
    name: str
    installed_version: Optional[str] = None
    required_spec: str = ""
    is_installed: bool = False
    is_compatible: bool = True
    conflict_reason: str = ""


@dataclass
class DependencyCheckResult:
    """依赖检查结果"""
    success: bool
    installed_packages: List[PackageInfo]
    missing_packages: List[str]
    conflicting_packages: List[PackageInfo]
    install_candidates: List[str]


class DependencyManager:
    """
    依赖管理器

    功能：
    - 检查包是否已安装
    - 解析版本规范
    - 检测版本冲突
    - 自动安装缺失的包
    """

    # 内置包列表（不需要安装的标准库）
    BUILTIN_PACKAGES = {
        "os", "sys", "re", "json", "time", "datetime", "pathlib",
        "subprocess", "logging", "typing", "dataclasses", "hashlib",
        "collections", "itertools", "functools", "io", "string",
    }

    # 已知不兼容的包版本对
    KNOWN_CONFLICTS = {
        # 包名: {(min_version, max_version), ...}
        "tensorflow": {
            ("2.0.0", "2.4.0"): "numpy<1.20",
        },
        # 可以添加更多已知冲突
    }

    def __init__(self, auto_install: bool = True, timeout: int = 300):
        """
        初始化依赖管理器

        Args:
            auto_install: 是否自动安装缺失的依赖
            timeout: 安装超时时间（秒）
        """
        self.auto_install = auto_install
        self.timeout = timeout
        self._installed_cache: Optional[Dict[str, PackageInfo]] = None

    def check_dependencies(
        self,
        dependencies: List[str],
        check_conflicts: bool = True
    ) -> DependencyCheckResult:
        """
        检查依赖状态

        Args:
            dependencies: 依赖列表（如 ["pandas>=1.5.0", "numpy"]）
            check_conflicts: 是否检查版本冲突

        Returns:
            DependencyCheckResult 检查结果
        """
        installed_packages = []
        missing_packages = []
        conflicting_packages = []
        install_candidates = []

        # 刷新已安装包缓存
        self._refresh_installed_cache()

        for dep_spec in dependencies:
            try:
                # 解析依赖规范
                req = pkg_req.Requirement(dep_spec)
                package_name = req.name
                package_key = package_name.lower().replace("-", "_")

                # 检查是否为内置包
                if package_key in self.BUILTIN_PACKAGES:
                    logger.debug(f"Skipping builtin package: {package_name}")
                    continue

                # 获取包信息
                pkg_info = self._get_package_info(req)

                if not pkg_info.is_installed:
                    missing_packages.append(dep_spec)
                    if self.auto_install:
                        install_candidates.append(dep_spec)
                elif not pkg_info.is_compatible:
                    conflicting_packages.append(pkg_info)
                    if self.auto_install:
                        # 已安装但不兼容，需要重新安装
                        install_candidates.append(dep_spec)
                else:
                    installed_packages.append(pkg_info)

                # 额外的冲突检查
                if check_conflicts and pkg_info.is_installed:
                    conflicts = self._check_known_conflicts(package_name, pkg_info.installed_version)
                    if conflicts:
                        pkg_info.is_compatible = False
                        pkg_info.conflict_reason = f"Known conflict: {conflicts}"
                        if pkg_info not in conflicting_packages:
                            conflicting_packages.append(pkg_info)

            except pkg_req.InvalidRequirement as e:
                logger.warning(f"Invalid requirement specification: {dep_spec}, error: {e}")
                missing_packages.append(dep_spec)

        success = not missing_packages and not conflicting_packages

        return DependencyCheckResult(
            success=success,
            installed_packages=installed_packages,
            missing_packages=missing_packages,
            conflicting_packages=conflicting_packages,
            install_candidates=install_candidates
        )

    def install_dependencies(self, dependencies: List[str]) -> Tuple[bool, str]:
        """
        安装依赖包

        Args:
            dependencies: 依赖列表

        Returns:
            (success, message) 成功状态和消息
        """
        if not dependencies:
            return True, "No dependencies to install"

        # 先检查依赖状态
        check_result = self.check_dependencies(dependencies, check_conflicts=True)

        # 如果没有需要安装的包
        if not check_result.install_candidates:
            if check_result.conflicting_packages:
                conflicts = ", ".join([
                    f"{p.name} ({p.conflict_reason})"
                    for p in check_result.conflicting_packages
                ])
                return False, f"Version conflicts detected: {conflicts}"
            return True, "All dependencies already installed and compatible"

        # 安装缺失或不兼容的包
        success_count = 0
        failed_packages = []

        for dep_spec in check_result.install_candidates:
            try:
                result = subprocess.run(
                    ["pip", "install", dep_spec],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                if result.returncode == 0:
                    success_count += 1
                    logger.info(f"Successfully installed: {dep_spec}")
                else:
                    failed_packages.append(dep_spec)
                    logger.error(f"Failed to install {dep_spec}: {result.stderr}")

            except subprocess.TimeoutExpired:
                failed_packages.append(dep_spec)
                logger.error(f"Timeout installing: {dep_spec}")
            except Exception as e:
                failed_packages.append(dep_spec)
                logger.error(f"Error installing {dep_spec}: {e}")

        # 清除缓存，以便下次检查时获取最新状态
        self._installed_cache = None

        if failed_packages:
            return False, f"Failed to install: {', '.join(failed_packages)}"

        return True, f"Successfully installed {success_count} package(s)"

    def _refresh_installed_cache(self):
        """刷新已安装包的缓存"""
        self._installed_cache = {}

        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                import json
                packages = json.loads(result.stdout)
                for pkg in packages:
                    name = pkg["name"].lower().replace("-", "_")
                    self._installed_cache[name] = PackageInfo(
                        name=pkg["name"],
                        installed_version=pkg["version"],
                        is_installed=True
                    )
        except Exception as e:
            logger.warning(f"Failed to get installed packages: {e}")

    def _get_package_info(self, req: pkg_req.Requirement) -> PackageInfo:
        """获取包信息"""
        package_name = req.name
        package_key = package_name.lower().replace("-", "_")

        # 检查缓存
        if self._installed_cache and package_key in self._installed_cache:
            pkg_info = self._installed_cache[package_key]
            pkg_info.required_spec = str(req.specifier)
            # 检查版本是否兼容
            if req.specifier and pkg_info.installed_version:
                try:
                    installed_ver = pkg_version.parse(pkg_info.installed_version)
                    pkg_info.is_compatible = installed_ver in req.specifier
                    if not pkg_info.is_compatible:
                        pkg_info.conflict_reason = (
                            f"Required: {req.specifier}, "
                            f"Installed: {pkg_info.installed_version}"
                        )
                except Exception as e:
                    logger.warning(f"Version comparison failed for {package_name}: {e}")
            return pkg_info

        # 未安装
        return PackageInfo(
            name=package_name,
            required_spec=str(req.specifier) if req.specifier else "",
            is_installed=False,
            is_compatible=False
        )

    def _check_known_conflicts(self, package_name: str, installed_version: str) -> Optional[str]:
        """检查已知的版本冲突"""
        package_key = package_name.lower().replace("-", "_")

        if package_key not in self.KNOWN_CONFLICTS:
            return None

        try:
            version = pkg_version.parse(installed_version)
        except Exception:
            return None

        for (min_ver, max_ver), conflict_desc in self.KNOWN_CONFLICTS[package_key]:
            try:
                min_v = pkg_version.parse(min_ver)
                max_v = pkg_version.parse(max_ver)
                if min_v <= version < max_v:
                    return conflict_desc
            except Exception:
                continue

        return None

    def parse_dependency_string(self, dep_string: str) -> List[str]:
        """
        解析依赖字符串为列表

        支持格式：
        - "pandas>=1.5.0, numpy>=1.20"
        - "pandas>=1.5.0"

        Args:
            dep_string: 依赖字符串

        Returns:
            依赖列表
        """
        if not dep_string:
            return []

        # 按逗号分割并清理
        deps = [d.strip() for d in dep_string.split(",")]
        return [d for d in deps if d]


def check_and_install_dependencies(
    dependencies: List[str],
    auto_install: bool = True
) -> Tuple[bool, str]:
    """
    便捷函数：检查并安装依赖

    Args:
        dependencies: 依赖列表
        auto_install: 是否自动安装

    Returns:
        (success, message)
    """
    manager = DependencyManager(auto_install=auto_install)
    return manager.install_dependencies(dependencies)