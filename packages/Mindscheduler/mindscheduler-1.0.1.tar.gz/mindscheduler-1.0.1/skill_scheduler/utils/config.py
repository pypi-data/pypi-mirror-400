import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
import yaml


class Config:
    def __init__(
        self,
        config_path: Optional[str] = None,
        skills_dir: Optional[str] = None,
        enable_llm: bool = False,
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-3.5-turbo",
        llm_base_url: Optional[str] = None,
        **kwargs
    ):
        # 路径配置
        self.skills_dir = skills_dir or self._find_skills_dir()

        # LLM 配置
        self.enable_llm = enable_llm or os.getenv("SKILLSCHEDULER_ENABLE_LLM", "").lower() in ("true", "1", "yes")
        self.llm_provider = "openai"
        self.llm_api_key = llm_api_key or os.getenv("SKILLSCHEDULER_LLM_API_KEY")
        self.llm_model = llm_model or os.getenv("SKILLSCHEDULER_LLM_MODEL", "gpt-3.5-turbo")
        self.llm_base_url = llm_base_url or os.getenv("SKILLSCHEDULER_LLM_BASE_URL")
        self.llm_temperature = 0.3

        # 执行器配置（支持通过 kwargs 覆盖）
        self.executor_timeout = kwargs.get('executor_timeout', 30)
        self.executor_max_memory_mb = kwargs.get('executor_max_memory_mb', 512)
        self.executor_work_dir = kwargs.get('executor_work_dir', "./temp")
        self.auto_install_deps = kwargs.get('auto_install_deps', True)

        # 匹配器配置（支持通过 kwargs 覆盖）
        self.matcher_threshold = kwargs.get('matcher_threshold', 0.5)
        self.matcher_enable_embedding = kwargs.get('matcher_enable_embedding', False)

        # 日志配置（支持通过 kwargs 覆盖）
        self.log_level = kwargs.get('log_level', "INFO")
        self.log_file = kwargs.get('log_file', None)

        # 数据库路径（支持通过 kwargs 覆盖）
        self.db_path = kwargs.get('db_path', "./data/skillscheduler.db")

        # 从配置文件加载
        if config_path:
            self._load_from_file(config_path)

        # 从环境变量加载（覆盖）
        self._load_from_env()

    def _find_skills_dir(self) -> str:
        """自动查找 skills 目录"""
        # 1. 检查当前目录下的 skills/
        if Path("./skills").exists():
            return "./skills"

        # 2. 检查项目根目录下的 skills/
        current_path = Path.cwd()
        for parent in [current_path] + list(current_path.parents):
            skills_path = parent / "skills"
            if skills_path.exists() and (skills_path / "skill.yaml").exists():
                return str(skills_path)

        # 3. 默认返回 ./skills
        return "./skills"

    def _load_from_file(self, path: str):
        config_file = Path(path)
        if not config_file.exists():
            return

        with open(config_file, 'r') as f:
            data = yaml.safe_load(f) or {}

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _load_from_env(self):
        self.llm_api_key = os.getenv("SKILLSCHEDULER_LLM_API_KEY", self.llm_api_key)
        self.llm_model = os.getenv("SKILLSCHEDULER_LLM_MODEL", self.llm_model)
        self.llm_base_url = os.getenv("SKILLSCHEDULER_LLM_BASE_URL", self.llm_base_url)
        self.skills_dir = os.getenv("SKILLSCHEDULER_SKILLS_DIR", self.skills_dir)
        self.log_level = os.getenv("SKILLSCHEDULER_LOG_LEVEL", self.log_level)

        auto_install_env = os.getenv("SKILLSCHEDULER_AUTO_INSTALL_DEPS")
        if auto_install_env is not None:
            self.auto_install_deps = auto_install_env.lower() in ("true", "1", "yes")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skills_dir": self.skills_dir,
            "enable_llm": self.enable_llm,
            "llm_model": self.llm_model,
            "llm_base_url": self.llm_base_url,
            "executor_timeout": self.executor_timeout,
            "auto_install_deps": self.auto_install_deps,
            "matcher_threshold": self.matcher_threshold,
            "log_level": self.log_level,
        }

    @property
    def use_llm_matching(self) -> bool:
        """是否使用 LLM 匹配（需要 API key）"""
        return self.enable_llm and self.llm_api_key is not None
