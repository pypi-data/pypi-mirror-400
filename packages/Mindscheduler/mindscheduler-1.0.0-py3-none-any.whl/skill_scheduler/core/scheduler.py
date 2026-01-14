import logging
from typing import Dict, Any, Optional
from pathlib import Path

import hashlib
import json
import time
from ..utils.config import Config
from .skill import SkillManager, Skill
from .executor import Executor
from .matcher import RuleMatcher
from .param_extractor import ParamExtractor
from .exceptions import ErrorHandler, create_error_result, handle_exception


class Logger:
    def __init__(self, name: str = "SkillScheduler", level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)


class SkillScheduler:
    def __init__(
        self,
        config: Optional[Config] = None,
        skills_dir: Optional[str] = None,
        enable_llm: bool = False,
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-3.5-turbo",
        metrics_registry=None,
        **kwargs
    ):
        # 支持 Config 对象或直接传参
        if config is None:
            config = Config(
                skills_dir=skills_dir,
                enable_llm=enable_llm,
                llm_api_key=llm_api_key,
                llm_model=llm_model,
                **kwargs
            )

        self.config = config
        self.logger = Logger(level=config.log_level, log_file=config.log_file)

        self.skill_manager = SkillManager(config.skills_dir)
        self.executor = Executor(
            timeout=config.executor_timeout,
            max_memory_mb=config.executor_max_memory_mb,
            work_dir=config.executor_work_dir,
            auto_install_deps=config.auto_install_deps,
            metrics_registry=metrics_registry
        )
        self.matcher = RuleMatcher(
            threshold=config.matcher_threshold,
            enable_embedding=config.matcher_enable_embedding
        )

        self.llm_adapter = None
        self._decision_cache = {}  # LLM decision cache: query_hash -> result
        self.metrics_registry = metrics_registry

        if config.enable_llm:
            self._init_llm()

    def _init_llm(self):
        try:
            from ..llm.base import LLMAdapter
            if self.config.llm_provider == "openai":
                from ..llm.openai import OpenAIAdapter
                self.llm_adapter = OpenAIAdapter(
                    api_key=self.config.llm_api_key,
                    model=self.config.llm_model
                )
            else:
                self.logger.warning(f"Unknown LLM provider: {self.config.llm_provider}")
        except ImportError as e:
            self.logger.error(f"Failed to initialize LLM: {e}")

    def run(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行指定技能

        Args:
            skill_name: 技能名称
            params: 参数字典

        Returns:
            执行结果字典
        """
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            # 使用结构化错误
            error = ErrorHandler.skill_not_found(
                skill_name=skill_name,
                available_skills=self.skill_manager.list_skill_names()
            )
            return error.to_dict()

        self.logger.info(f"Running skill: {skill_name} with params: {params}")

        start_time = time.time()

        try:
            # 执行技能
            output, success = self.executor.execute(skill, params)

            if success:
                self.logger.info(f"Skill '{skill_name}' completed successfully")
                result = {
                    "success": True,
                    "skill": skill_name,
                    "output": output
                }
            else:
                self.logger.error(f"Skill '{skill_name}' failed: {output}")
                error = ErrorHandler.execution_failed(
                    skill_name=skill_name,
                    reason=output
                )
                result = error.to_dict()

            # 记录执行时间
            execution_time = time.time() - start_time
            result["execution_time"] = execution_time

            return result

        except Exception as e:
            self.logger.exception(f"Unexpected error executing skill '{skill_name}'")
            return handle_exception(e, context={"skill_name": skill_name})

    def ask(self, query: str, auto_execute: bool = True) -> Dict[str, Any]:
        """
        智能匹配并执行技能

        Args:
            query: 用户请求，如 "读取 PDF 文件 ./data/document.pdf"
            auto_execute: 是否自动执行（True）或只返回匹配结果（False）

        Returns:
            执行结果或匹配结果
        """
        self.logger.info(f"Processing query: {query}")

        # 根据配置选择匹配方式
        if self.config.use_llm_matching:
            return self._dispatch_with_llm(query, auto_execute)
        else:
            return self._dispatch_with_matcher(query, auto_execute)

    def _dispatch_with_llm(self, query: str, auto_execute: bool = True) -> Dict[str, Any]:
        """使用 LLM 智能匹配技能"""
        # Check cache first
        query_hash = hashlib.md5(query.encode()).hexdigest()
        if query_hash in self._decision_cache:
            self.logger.info(f"Using cached decision for query: {query}")
            cached = self._decision_cache[query_hash]
            if auto_execute:
                return self._execute_llm_result(cached, query)
            else:
                return {"matched": True, "result": cached, "query": query}

        try:
            result = self.llm_adapter.parse_intent(query, self.skill_manager.list_skills())

            self.logger.info(f"LLM returned: {result}")

            if not result.get("skills"):
                self.logger.info("LLM found no skills, falling back to matcher")
                return self._dispatch_with_matcher(query, auto_execute)

            # Cache the result
            self._decision_cache[query_hash] = result

            if auto_execute:
                return self._execute_llm_result(result, query)
            else:
                return {"matched": True, "result": result, "query": query}

        except Exception as e:
            self.logger.warning(f"LLM dispatch failed: {e}, falling back to matcher")
            return self._dispatch_with_matcher(query, auto_execute)

    def _execute_llm_result(self, llm_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """执行 LLM 返回的结果"""
        skills_list = llm_result.get("skills", [])

        if not skills_list:
            return {
                "success": False,
                "error": "no_skills_from_llm",
                "message": "LLM returned no skills",
                "query": query
            }

        results = []
        for skill_info in skills_list:
            skill_name = skill_info.get("name")
            params = skill_info.get("params", {})

            # 从 query 中补充参数
            skill = self.skill_manager.get_skill(skill_name)
            if skill:
                extracted_params = self._extract_params(query, skill)
                params = {**extracted_params, **params}

            result = self.run(skill_name, params)
            results.append(result)

            if not result.get("success"):
                return {
                    "success": False,
                    "error": "skill_execution_failed",
                    "skill": skill_name,
                    "message": result.get("message", "Execution failed")
                }

        return {
            "success": True,
            "results": results,
            "query": query
        }

    def _dispatch_with_matcher(self, query: str, auto_execute: bool = True) -> Dict[str, Any]:
        """使用规则匹配技能"""
        skills = self.skill_manager.list_skills()
        skill, score = self.matcher.match(query, skills)

        if not skill:
            return {
                "success": False,
                "error": "no_match",
                "message": "No matching skill found",
                "query": query,
                "matched_skill": None,
                "suggestions": ["Try rephrasing your query", "Use list_skills() to see available skills"]
            }

        params = self._extract_params(query, skill)

        if not auto_execute:
            return {
                "matched": True,
                "skill": skill.name,
                "params": params,
                "query": query,
                "score": score
            }

        return self.run(skill.name, params)

    def _extract_params(self, query: str, skill: Skill) -> Dict[str, Any]:
        """
        从查询中提取技能参数

        使用独立的 ParamExtractor 类进行参数提取，支持多种格式和别名匹配。

        Args:
            query: 自然语言查询字符串
            skill: 技能对象

        Returns:
            提取的参数字典
        """
        extractor = ParamExtractor(skill)
        return extractor.extract(query)

    def list_skills(self) -> list:
        return [{"name": s.name, "description": s.description} for s in self.skill_manager.list_skills()]

    def list_skill_names(self) -> list:
        return self.skill_manager.list_skill_names()

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            return None

        return {
            "schema_version": skill.schema_version,
            "name": skill.name,
            "title": skill.title,
            "description": skill.description,
            "version": skill.config.get("version", "unknown"),
            "author": skill.author,
            "homepage": skill.homepage,
            "license": skill.license,
            "type": skill.type.value,
            "tags": skill.tags,
            "inputs": {name: {"type": inp.type, "required": inp.required, "description": inp.description}
                      for name, inp in skill.inputs.items()},
            "output": {"type": skill.output.type, "description": skill.output.description} if skill.output else None,
            "permissions": {
                "read_file": skill.permissions.read_file if skill.permissions else [],
                "write_file": skill.permissions.write_file if skill.permissions else [],
                "network": skill.permissions.network if skill.permissions else False,
                "execute_script": skill.permissions.execute_script if skill.permissions else True
            },
            "dependencies": skill.dependencies,
            "timeout": skill.timeout
        }
