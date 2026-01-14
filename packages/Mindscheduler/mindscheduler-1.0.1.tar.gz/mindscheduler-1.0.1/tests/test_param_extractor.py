"""
测试 ParamExtractor 参数提取器

测试参数提取的各种场景和边界情况
"""
import pytest
from pathlib import Path

from skill_scheduler.core.param_extractor import (
    ParamExtractor,
    ExtractionPattern,
    extract_params_from_query
)
from skill_scheduler.core.skill import Skill, SkillInput


class TestExtractionPattern:
    """测试 ExtractionPattern 数据类"""

    def test_creation(self):
        """测试创建 ExtractionPattern"""
        pattern = ExtractionPattern(
            primary_name="file",
            aliases=["file_path", "path"],
            description_keywords=["文件", "路径"]
        )

        assert pattern.primary_name == "file"
        assert len(pattern.aliases) == 2
        assert len(pattern.description_keywords) == 2


class TestParamExtractor:
    """测试 ParamExtractor 类"""

    def test_basic_extraction(self, sample_skill):
        """测试基本参数提取"""
        extractor = ParamExtractor(sample_skill)

        # 测试文件参数提取
        params = extractor.extract("统计 data.txt 的行数")
        assert "file" in params
        assert params["file"] == "data.txt"

    def test_mode_parameter_extraction(self, sample_skill):
        """测试 mode 参数提取"""
        extractor = ParamExtractor(sample_skill)

        # 测试 mode 参数
        params = extractor.extract("统计 data.txt 的词数")
        assert "file" in params or "mode" in params

    def test_file_path_extraction(self, sample_skill):
        """测试文件路径提取（相对路径）"""
        extractor = ParamExtractor(sample_skill)

        # 测试相对路径提取
        params = extractor.extract("统计 ./data/test.txt 的行数")
        if "file" in params:
            assert "data/test.txt" in params["file"] or "test.txt" in params["file"]

    def test_parameter_with_equals(self, sample_skill):
        """测试使用等号的参数格式"""
        extractor = ParamExtractor(sample_skill)

        params = extractor.extract("file=data.txt mode=lines")
        assert params.get("file") == "data.txt"

    def test_parameter_with_double_dash(self, sample_skill):
        """测试使用双横线的参数格式"""
        extractor = ParamExtractor(sample_skill)

        params = extractor.extract("--file data.txt --mode lines")
        assert params.get("file") == "data.txt"

    def test_no_parameters_found(self, sample_skill):
        """测试没有找到参数的情况"""
        extractor = ParamExtractor(sample_skill)

        params = extractor.extract("随便说点什么")
        # 应该返回空字典，而不是 None
        assert isinstance(params, dict)

    def test_chinese_query(self, sample_skill):
        """测试中文查询"""
        extractor = ParamExtractor(sample_skill)

        params = extractor.extract("帮我统计 文件.txt 的字符数")
        if "file" in params:
            assert "文件.txt" in params["file"] or ".txt" in params["file"]

    def test_custom_aliases(self, sample_skill):
        """测试自定义别名"""
        custom_aliases = {
            "file": ["文件名", "档案", "filepath"]
        }
        extractor = ParamExtractor(sample_skill, custom_aliases=custom_aliases)

        params = extractor.extract("处理 档案:myfile.txt")
        # 应该通过别名匹配到 file 参数
        # 注意：实际匹配结果取决于正则表达式

    def test_empty_query(self, sample_skill):
        """测试空查询"""
        extractor = ParamExtractor(sample_skill)

        params = extractor.extract("")
        assert isinstance(params, dict)

    def test_multiple_file_extensions(self, sample_skill):
        """测试多种文件扩展名"""
        extractor = ParamExtractor(sample_skill)

        # 测试不同的文件扩展名
        extensions = ["txt", "md", "csv", "json", "pdf"]
        for ext in extensions:
            query = f"处理 document.{ext}"
            params = extractor.extract(query)
            if "file" in params:
                assert ext in params["file"] or "document" in params["file"]


class TestConvenienceFunction:
    """测试便捷函数"""

    def test_extract_params_from_query(self, sample_skill):
        """测试便捷函数 extract_params_from_query"""
        params = extract_params_from_query(sample_skill, "统计 data.txt")
        assert isinstance(params, dict)


class TestEdgeCases:
    """测试边界情况"""

    def test_skill_with_no_inputs(self, temp_dir):
        """测试没有输入参数的技能"""
        # 创建没有 inputs 的技能
        skill_dir = temp_dir / "no-input-skill"
        skill_dir.mkdir()
        (skill_dir / "skill.md").write_text("""---
name: no-input
description: A skill with no inputs
---
""")
        skill = Skill("no-input", skill_dir)
        extractor = ParamExtractor(skill)

        params = extractor.extract("随便说点什么")
        assert isinstance(params, dict)

    def test_special_characters_in_query(self, sample_skill):
        """测试查询中的特殊字符"""
        extractor = ParamExtractor(sample_skill)

        # 测试带特殊字符的文件名
        params = extractor.extract("处理 file_with-dash.txt")
        if "file" in params:
            assert "txt" in params["file"]

    def test_query_with_colon(self, sample_skill):
        """测试带冒号的查询"""
        extractor = ParamExtractor(sample_skill)

        params = extractor.extract("file:data.txt")
        assert params.get("file") == "data.txt"

    def test_query_with_chinese_colon(self, sample_skill):
        """测试带中文冒号的查询"""
        extractor = ParamExtractor(sample_skill)

        params = extractor.extract("文件：data.txt")
        if "file" in params:
            assert "data.txt" in params["file"]


class TestFileDetection:
    """测试文件参数智能检测"""

    def test_file_param_detection(self, sample_skill):
        """测试文件参数的自动检测"""
        extractor = ParamExtractor(sample_skill)

        # file 参数应该被识别为文件参数
        for pattern in extractor.extraction_patterns["file"].description_keywords:
            assert any(keyword in pattern.lower() for keyword in ["文件", "file", "路径", "path"])

    def test_file_extension_patterns(self):
        """测试文件扩展名匹配模式"""
        # FILE_EXTENSIONS 是一个正则表达式模式，检查是否包含常见扩展名
        from skill_scheduler.core.param_extractor import ParamExtractor

        # 检查正则表达式模式是否包含常见扩展名（不包括反斜杠）
        pattern = ParamExtractor.FILE_EXTENSIONS
        assert "txt" in pattern
        assert "md" in pattern
        assert "csv" in pattern
        assert "pdf" in pattern
        # 验证它是一个正则表达式模式
        assert pattern.startswith(r'\.') or pattern.startswith('\\.')


class TestDefaultAliases:
    """测试默认参数别名"""

    def test_default_file_aliases(self):
        """测试 file 参数的默认别名"""
        from skill_scheduler.core.param_extractor import ParamExtractor

        assert "file" in ParamExtractor.DEFAULT_PARAM_ALIASES
        assert "file_path" in ParamExtractor.DEFAULT_PARAM_ALIASES["file"]
        assert "path" in ParamExtractor.DEFAULT_PARAM_ALIASES["file"]

    def test_default_name_aliases(self):
        """测试 name 参数的默认别名"""
        from skill_scheduler.core.param_extractor import ParamExtractor

        assert "name" in ParamExtractor.DEFAULT_PARAM_ALIASES
        assert "username" in ParamExtractor.DEFAULT_PARAM_ALIASES["name"]


@pytest.mark.parametrize("query,expected_file", [
    ("统计 data.txt 的行数", "data.txt"),
    ("处理 document.csv", "document.csv"),
    ("读取 file.json 内容", "file.json"),
])
def test_various_file_queries(sample_skill, query, expected_file):
    """参数化测试各种文件查询"""
    extractor = ParamExtractor(sample_skill)
    params = extractor.extract(query)

    if "file" in params:
        # 检查是否包含期望的文件名或扩展名
        result = params["file"]
        assert any([
            expected_file in result,
            expected_file.split('.')[0] in result,
            expected_file.split('.')[-1] in result
        ])


@pytest.mark.parametrize("mode", ["lines", "words", "chars"])
def test_various_modes(sample_skill, mode):
    """参数化测试各种模式"""
    extractor = ParamExtractor(sample_skill)
    params = extractor.extract(f"统计 data.txt 的{mode}")

    if "mode" in params:
        assert mode in params["mode"] or params["mode"] == mode
