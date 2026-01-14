"""
测试 SkillScheduler 调度器

测试 run() 和 ask() 方法以及相关功能
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from skill_scheduler import SkillScheduler


class TestSkillSchedulerInit:
    """测试调度器初始化"""

    def test_initialization_with_skills_dir(self, test_skills_dir):
        """测试使用技能目录初始化"""
        scheduler = SkillScheduler(skills_dir=str(test_skills_dir))

        assert scheduler.skill_manager is not None
        assert scheduler.executor is not None
        assert scheduler.matcher is not None

    def test_initialization_with_config(self, test_skills_dir):
        """测试使用配置对象初始化"""
        from skill_scheduler.utils.config import Config

        config = Config(
            skills_dir=str(test_skills_dir),
            enable_llm=False
        )
        scheduler = SkillScheduler(config=config)

        assert scheduler.config == config

    def test_initialization_with_llm_disabled(self, test_skills_dir):
        """测试禁用 LLM 的初始化"""
        scheduler = SkillScheduler(
            skills_dir=str(test_skills_dir),
            enable_llm=False
        )

        assert scheduler.llm_adapter is None

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_initialization_with_llm_enabled(self, test_skills_dir):
        """测试启用 LLM 的初始化"""
        try:
            scheduler = SkillScheduler(
                skills_dir=str(test_skills_dir),
                enable_llm=True,
                llm_api_key="test-key"
            )

            # LLM 适配器应该被初始化
            # 但可能会因为导入失败而失败
            assert scheduler.config.enable_llm is True
        except ImportError:
            # 如果 OpenAI 库未安装，这是预期的
            pass


class TestSchedulerRun:
    """测试 run() 方法"""

    def test_run_nonexistent_skill(self, sample_scheduler):
        """测试运行不存在的技能"""
        result = sample_scheduler.run("non-existent", {})

        assert result["success"] is False
        assert "error" in result or "category" in result
        assert "message" in result

    def test_run_hello_world_skill(self, sample_scheduler):
        """测试运行 hello-world 技能"""
        result = sample_scheduler.run("hello-world", {})

        assert result["success"] is True
        assert "output" in result

    def test_run_file_counter_skill(self, sample_scheduler, test_data_dir):
        """测试运行 file-counter 技能"""
        result = sample_scheduler.run("file-counter", {
            "file": str(test_data_dir / "test.txt")
        })

        assert result["success"] is True
        assert "output" in result

    def test_run_with_missing_param(self, sample_scheduler):
        """测试运行时缺少必需参数"""
        result = sample_scheduler.run("file-counter", {})

        assert result["success"] is False
        assert "message" in result

    def test_run_execution_time_recorded(self, sample_scheduler):
        """测试记录执行时间"""
        result = sample_scheduler.run("hello-world", {})

        assert "execution_time" in result
        assert result["execution_time"] >= 0


class TestSchedulerAsk:
    """测试 ask() 方法"""

    def test_ask_simple_query(self, sample_scheduler):
        """测试简单查询"""
        result = sample_scheduler.ask("打印问候")

        # ask 可能返回成功或失败（取决于匹配情况）
        # 检查响应结构是否正确
        assert "success" in result
        # 如果成功，应该有输出
        if result["success"]:
            assert "output" in result or "skill" in result
        # 如果失败，应该有错误信息
        else:
            assert "error" in result or "message" in result

    def test_ask_with_file_reference(self, sample_scheduler, test_data_dir):
        """测试带文件引用的查询"""
        result = sample_scheduler.ask(
            f"统计 {test_data_dir / 'test.txt'} 的行数"
        )

        # 检查响应结构
        assert "success" in result

    def test_ask_no_match(self, sample_scheduler):
        """测试没有匹配的查询"""
        result = sample_scheduler.ask("做一些完全不相关的事情")

        # 应该返回错误或建议
        assert result.get("success") is False

    def test_ask_with_auto_execute_false(self, sample_scheduler):
        """测试禁用自动执行"""
        result = sample_scheduler.ask("打印问候", auto_execute=False)

        # 应该返回匹配结果而不是执行结果
        # 检查响应包含必要字段
        assert "success" in result or "matched" in result or "skill" in result


class TestSchedulerListSkills:
    """测试列出技能功能"""

    def test_list_skills(self, sample_scheduler):
        """测试列出所有技能"""
        skills = sample_scheduler.list_skills()

        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_list_skill_names(self, sample_scheduler):
        """测试列出技能名称"""
        names = sample_scheduler.list_skill_names()

        assert isinstance(names, list)
        assert "hello-world" in names

    def test_get_skill_info(self, sample_scheduler):
        """测试获取技能信息"""
        info = sample_scheduler.get_skill_info("file-counter")

        assert info is not None
        assert info["name"] == "file-counter"
        assert "description" in info
        assert "inputs" in info

    def test_get_skill_info_nonexistent(self, sample_scheduler):
        """测试获取不存在技能的信息"""
        info = sample_scheduler.get_skill_info("non-existent")

        assert info is None


class TestSchedulerLLM:
    """测试 LLM 相关功能"""

    def test_llm_disabled_by_default(self, test_skills_dir):
        """测试默认禁用 LLM"""
        scheduler = SkillScheduler(skills_dir=str(test_skills_dir))

        assert scheduler.config.enable_llm is False

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_llm_enabled_with_api_key(self, test_skills_dir):
        """测试使用 API Key 启用 LLM"""
        scheduler = SkillScheduler(
            skills_dir=str(test_skills_dir),
            enable_llm=True,
            llm_api_key="test-key"
        )

        assert scheduler.config.enable_llm is True


class TestSchedulerConfig:
    """测试调度器配置"""

    def test_config_properties(self, sample_scheduler):
        """测试配置属性"""
        assert sample_scheduler.config is not None
        assert hasattr(sample_scheduler.config, 'skills_dir')
        assert hasattr(sample_scheduler.config, 'executor_timeout')

    def test_custom_config(self, temp_dir):
        """测试自定义配置"""
        from skill_scheduler.utils.config import Config

        config = Config(
            skills_dir=str(temp_dir),
            executor_timeout=60,
            matcher_threshold=0.8
        )
        scheduler = SkillScheduler(config=config)

        assert scheduler.config.executor_timeout == 60
        assert scheduler.config.matcher_threshold == 0.8


@pytest.mark.integration
class TestSchedulerIntegration:
    """集成测试：调度器完整流程"""

    def test_full_workflow(self, sample_scheduler, test_data_dir):
        """测试完整工作流程"""
        # 1. 列出技能
        skills = sample_scheduler.list_skills()
        assert len(skills) > 0

        # 2. 获取技能信息
        if skills:
            info = sample_scheduler.get_skill_info(skills[0]["name"])
            assert info is not None

        # 3. 运行技能
        result = sample_scheduler.run("hello-world", {})
        assert result["success"] is True

    def test_error_recovery(self, sample_scheduler):
        """测试错误恢复"""
        # 运行不存在的技能
        result1 = sample_scheduler.run("non-existent", {})
        assert result1["success"] is False

        # 运行存在的技能应该正常工作
        result2 = sample_scheduler.run("hello-world", {})
        assert result2["success"] is True

    def test_consecutive_executions(self, sample_scheduler):
        """测试连续执行"""
        for _ in range(3):
            result = sample_scheduler.run("hello-world", {})
            assert result["success"] is True


class TestSchedulerMetrics:
    """测试调度器监控"""

    def test_scheduler_with_metrics(self, test_skills_dir):
        """测试带监控的调度器"""
        from skill_scheduler.observability.metrics import InMemoryMetricsCallback, get_registry

        # 创建监控注册中心
        metrics = InMemoryMetricsCallback()
        registry = get_registry()
        registry.register(metrics)

        # 创建带监控的调度器
        scheduler = SkillScheduler(
            skills_dir=str(test_skills_dir),
            metrics_registry=registry
        )

        # 执行技能
        result = scheduler.run("hello-world", {})

        # 检查监控记录
        assert metrics.get_total_count() > 0


@pytest.mark.parametrize("skill_name,params,should_succeed", [
    ("hello-world", {}, True),
    ("file-counter", {}, False),  # 缺少参数
])
def test_various_skills(sample_scheduler, skill_name, params, should_succeed):
    """参数化测试各种技能"""
    result = sample_scheduler.run(skill_name, params)

    assert result["success"] == should_succeed
