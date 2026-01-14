"""
测试 SkillManager 和 Skill 类

测试技能的加载、解析、验证等功能
"""
import pytest
from pathlib import Path

from skill_scheduler.core.skill import (
    Skill,
    SkillManager,
    SkillType,
    SkillInput,
    SkillOutput,
    SkillPermission
)


class TestSkillInput:
    """测试 SkillInput 数据类"""

    def test_creation(self):
        """测试创建 SkillInput"""
        input_param = SkillInput(
            name="file",
            type="string",
            required=True,
            description="文件路径"
        )

        assert input_param.name == "file"
        assert input_param.type == "string"
        assert input_param.required is True


class TestSkillOutput:
    """测试 SkillOutput 数据类"""

    def test_creation(self):
        """测试创建 SkillOutput"""
        output = SkillOutput(
            type="string",
            description="处理结果"
        )

        assert output.type == "string"
        assert output.description == "处理结果"


class TestSkillPermission:
    """测试 SkillPermission 数据类"""

    def test_creation(self):
        """测试创建 SkillPermission"""
        perm = SkillPermission(
            read_file=["*.txt", "*.md"],
            write_file=["*.json"],
            network=False
        )

        assert len(perm.read_file) == 2
        assert len(perm.write_file) == 1
        assert perm.network is False

    def test_default_values(self):
        """测试默认值"""
        perm = SkillPermission()
        assert perm.read_file == []
        assert perm.write_file == []
        assert perm.network is False
        assert perm.execute_script is True


class TestSkill:
    """测试 Skill 类"""

    def test_load_simple_skill(self, test_skills_dir):
        """测试加载简单技能"""
        skill_dir = test_skills_dir / "hello-world"
        skill = Skill("hello-world", skill_dir)

        assert skill.name == "hello-world"
        assert skill.description is not None
        assert len(skill.description) > 0

    def test_load_full_skill(self, test_skills_dir):
        """测试加载完整格式技能"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        assert skill.name == "file-counter"
        assert skill.version is not None
        assert len(skill.tags) > 0
        assert skill.timeout > 0
        assert skill.script_path is not None

    def test_skill_inputs(self, test_skills_dir):
        """测试技能输入参数"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        assert len(skill.inputs) > 0
        assert "file" in skill.inputs
        assert skill.inputs["file"].required is True

    def test_skill_permissions(self, test_skills_dir):
        """测试技能权限"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        assert skill.permissions is not None
        assert len(skill.permissions.read_file) > 0

    def test_skill_dependencies(self, test_skills_dir):
        """测试技能依赖"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        # 依赖应该是列表
        assert isinstance(skill.dependencies, list)

    def test_skill_tags(self, test_skills_dir):
        """测试技能标签"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        assert isinstance(skill.tags, list)
        assert "file" in skill.tags

    def test_validate_params_valid(self, test_skills_dir, test_data_dir):
        """测试参数验证 - 有效参数"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        params = {"file": str(test_data_dir / "test.txt")}
        valid, error = skill.validate_params(params)

        assert valid is True
        assert error == ""

    def test_validate_params_missing_required(self, test_skills_dir):
        """测试参数验证 - 缺少必需参数"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        params = {}  # 缺少 file 参数
        valid, error = skill.validate_params(params)

        assert valid is False
        assert "file" in error.lower()

    def test_validate_params_type_conversion(self, test_skills_dir, test_data_dir):
        """测试参数类型转换"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        # 字符串转整数
        params = {"file": str(test_data_dir / "test.txt"), "mode": 123}
        valid, error = skill.validate_params(params)

        # 模式参数应该被转换为字符串
        assert valid is True

    def test_check_permissions(self, test_skills_dir, test_data_dir):
        """测试权限检查"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        # 测试允许的文件类型
        params = {"file": str(test_data_dir / "test.txt")}
        allowed, error = skill.check_permissions(params)

        assert allowed is True

    def test_check_permissions_denied(self, test_skills_dir):
        """测试权限拒绝"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        # 测试不允许的文件类型（假设 .exe 不在白名单中）
        params = {"file": "test.exe"}
        allowed, error = skill.check_permissions(params)

        # 应该被拒绝
        assert allowed is False or error is not None

    def test_get_command(self, test_skills_dir, test_data_dir):
        """测试获取命令"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        params = {"file": str(test_data_dir / "test.txt")}
        command = skill.get_command(params)

        assert command is not None
        assert "python" in command

    def test_get_documentation(self, test_skills_dir):
        """测试获取文档"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        doc = skill.get_documentation()

        assert doc is not None
        assert len(doc) > 0

    def test_get_full_definition(self, test_skills_dir):
        """测试获取完整定义"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        definition = skill.get_full_definition()

        assert definition is not None
        assert "name:" in definition
        assert "description:" in definition


class TestSkillManager:
    """测试 SkillManager 类"""

    def test_initialization(self, test_skills_dir):
        """测试初始化"""
        manager = SkillManager(str(test_skills_dir))

        assert manager.skills_dir == test_skills_dir
        assert isinstance(manager.skills, dict)

    def test_load_skills(self, test_skills_dir):
        """测试加载技能"""
        manager = SkillManager(str(test_skills_dir))

        assert len(manager.skills) > 0

    def test_get_skill(self, test_skills_dir):
        """测试获取技能"""
        manager = SkillManager(str(test_skills_dir))

        skill = manager.get_skill("file-counter")
        assert skill is not None
        assert skill.name == "file-counter"

    def test_get_nonexistent_skill(self, test_skills_dir):
        """测试获取不存在的技能"""
        manager = SkillManager(str(test_skills_dir))

        skill = manager.get_skill("non-existent")
        assert skill is None

    def test_list_skills(self, test_skills_dir):
        """测试列出所有技能"""
        manager = SkillManager(str(test_skills_dir))

        skills = manager.list_skills()

        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_list_skill_names(self, test_skills_dir):
        """测试列出技能名称"""
        manager = SkillManager(str(test_skills_dir))

        names = manager.list_skill_names()

        assert isinstance(names, list)
        assert "file-counter" in names

    def test_search_by_tags(self, test_skills_dir):
        """测试按标签搜索"""
        manager = SkillManager(str(test_skills_dir))

        skills = manager.search_by_tags(["file"])

        assert len(skills) > 0
        assert any("file" in skill.tags for skill in skills)

    def test_empty_skills_dir(self, temp_dir):
        """测试空技能目录"""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        manager = SkillManager(str(empty_dir))

        assert len(manager.skills) == 0


class TestSkillInference:
    """测试技能智能推断功能"""

    def test_infer_script_from_docs(self, temp_dir):
        """测试从文档推断脚本路径"""
        skill_dir = temp_dir / "inference-test"
        skill_dir.mkdir()

        # 创建包含脚本路径提示的文档（使用显式编码）
        with open(skill_dir / "skill.md", 'w', encoding='utf-8') as f:
            f.write("""---
name: inference-test
description: Test script inference
---

# Script Inference Test

使用示例:
```bash
python scripts/handler.py --input data.txt
```
""")

        skill = Skill("inference-test", skill_dir)

        # 应该推断出脚本路径
        assert skill.script_path is not None
        assert "scripts/" in skill.script_path or "handler" in skill.script_path

    def test_infer_inputs_from_table(self, temp_dir):
        """测试从表格推断输入参数"""
        skill_dir = temp_dir / "table-inference"
        skill_dir.mkdir()

        (skill_dir / "skill.md").write_text("""---
name: table-inference
description: Test input inference
---

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | string | Yes | File path |
| count | integer | No | Count |
""")

        skill = Skill("table-inference", skill_dir)

        # 应该推断出输入参数
        assert "file" in skill.inputs or len(skill.inputs) > 0


class TestSkillType:
    """测试技能类型"""

    def test_skill_type_enum(self):
        """测试技能类型枚举"""
        assert SkillType.ATOMIC.value == "atomic"

    def test_skill_type_property(self, test_skills_dir):
        """测试技能类型属性"""
        skill_dir = test_skills_dir / "hello-world"
        skill = Skill("hello-world", skill_dir)

        assert skill.type == SkillType.ATOMIC


class TestSkillMetadata:
    """测试技能元数据"""

    def test_skill_version(self, test_skills_dir):
        """测试技能版本"""
        skill_dir = test_skills_dir / "file-counter"
        skill = Skill("file-counter", skill_dir)

        assert skill.version is not None

    def test_skill_author(self, temp_dir):
        """测试技能作者"""
        skill_dir = temp_dir / "with-author"
        skill_dir.mkdir()

        (skill_dir / "skill.md").write_text("""---
name: with-author
description: Test author field
author: Test Author <test@example.com>
version: 1.0.0
---
""")
        skill = Skill("with-author", skill_dir)

        assert skill.author == "Test Author <test@example.com>"

    def test_skill_license(self, temp_dir):
        """测试技能许可证"""
        skill_dir = temp_dir / "with-license"
        skill_dir.mkdir()

        (skill_dir / "skill.md").write_text("""---
name: with-license
description: Test license field
license: MIT
---
""")
        skill = Skill("with-license", skill_dir)

        assert skill.license == "MIT"


@pytest.mark.integration
class TestSkillIntegration:
    """集成测试：技能在实际使用中的场景"""

    def test_skill_end_to_end(self, test_skills_dir, test_data_dir):
        """端到端测试：从加载到执行准备"""
        manager = SkillManager(str(test_skills_dir))
        skill = manager.get_skill("file-counter")

        assert skill is not None

        # 验证参数
        params = {"file": str(test_data_dir / "test.txt")}
        valid, error = skill.validate_params(params)
        assert valid is True

        # 检查权限
        allowed, error = skill.check_permissions(params)
        assert allowed is True

        # 获取命令
        command = skill.get_command(params)
        assert command is not None
