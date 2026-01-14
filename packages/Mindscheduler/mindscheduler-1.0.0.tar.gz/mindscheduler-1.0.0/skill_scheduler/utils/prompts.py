"""
LLM 提示词模板库

为智能技能调度提供高质量的提示词模板
"""
import json
from typing import Dict, List, Any, Optional


class PromptTemplate:
    """提示词模板基类"""

    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        """格式化模板"""
        return self.template.format(**kwargs)

    def format_system(self, **kwargs) -> str:
        """格式化为系统消息"""
        return self.format(**kwargs)


class IntentTemplate(PromptTemplate):
    """意图解析提示词模板"""

    def format_system(self, skills_list: str) -> str:
        """格式化系统提示词"""
        return self.template.format(skills_list=skills_list)

    def format_system_with_docs(self, skills_list: list) -> str:
        """格式化系统提示词（带完整文档）"""
        # 构建技能列表，包含完整文档
        skills_text = []
        for skill in skills_list:
            skills_text.append(f"""
## Skill: {skill['name']}

**Description**: {skill['description']}

**Tags**: {', '.join(skill.get('tags', []))}

**Inputs**:
{json.dumps(skill.get('inputs', {}), ensure_ascii=False, indent=2)}

**Documentation**:
{skill.get('documentation', 'No documentation available')}

---
""")

        all_skills = "\n".join(skills_text)
        return self.template.format(skills_list=all_skills)

    def format(self, user_query: str) -> str:
        """格式化用户消息"""
        return f"用户请求：{user_query}\n\n请分析用户请求并返回 JSON 格式的响应。"


class PromptLibrary:
    """提示词库"""

    def __init__(self):
        self.templates = {
            "intent": self._get_intent_template(),
            "parameter_extraction": self._get_parameter_extraction_template(),
        }

    def get_intent_template(self) -> IntentTemplate:
        """获取意图解析模板"""
        return IntentTemplate(self.templates["intent"])

    def get_parameter_extraction_template(self) -> PromptTemplate:
        """获取参数提取模板"""
        return PromptTemplate(self.templates["parameter_extraction"])

    def _get_intent_template(self) -> str:
        """智能意图解析提示词（支持完整文档）"""
        return """你是一个智能技能调度助手。你的任务是分析用户的请求，并根据可用的技能文档，确定需要调用哪些技能。

# 可用技能列表（包含完整文档）：
{skills_list}

# 任务说明：
1. **仔细阅读**每个技能的完整文档，包括：
   - 技能描述 (Description)
   - 使用场景 (When to Use This Skill)
   - 输入参数说明 (Input Parameters)
   - 使用示例 (Usage Examples)
   - 实现说明 (Implementation Notes)

2. **分析用户请求**的核心意图和需求

3. **匹配最合适的技能**，依据：
   - 技能描述是否匹配
   - "When to Use This Skill" 部分是否涵盖当前场景
   - 输入参数是否可以从用户请求中提取

4. **提取参数**：
   - 从用户请求中仔细提取参数值
   - 保持文件路径的完整性（包括 ./ 或 ../ 等前缀）
   - 如果缺少可选参数，不包含该参数（使用默认值）

# 返回格式：
请严格按照以下 JSON 格式返回：

```json
{{
  "intent": "用户意图的简要描述",
  "skills": [
    {{
      "name": "技能名称",
      "params": {{
        "参数名": "参数值"
      }}
    }}
  ],
  "reasoning": "选择这些技能的理由（引用文档中的相关说明）"
}}
```

# 重要规则：
- **技能名称** 必须严格从可用技能列表中选择
- **参数提取**：仔细从用户请求中提取，参考技能的 Input Parameters 表格
- **推理过程**：在 reasoning 中说明为什么选择该技能（可以引用文档中的 When to Use 或 Usage Examples）
- **示例参考**：如果用户请求与 Usage Examples 中的示例类似，使用示例中的参数格式

# 示例：

用户：extract text from PDF file ./data/document.pdf
```json
{{
  "intent": "从 PDF 文件中提取文本",
  "skills": [
    {{
      "name": "pdf-read",
      "params": {{
        "file": "./data/document.pdf"
      }}
    }}
  ],
  "reasoning": "用户请求提取 PDF 文本，根据 pdf-read 技能文档中的 'When to Use This Skill'，当用户提到 'extract text from PDF' 时应触发此技能"
}}
```

用户：按行读取PDF ./data/test.pdf
```json
{{
  "intent": "逐行读取并打印 PDF 内容",
  "skills": [
    {{
      "name": "pdf-line-print",
      "params": {{
        "file_path": "./data/test.pdf"
      }}
    }}
  ],
  "reasoning": "用户使用 '按行读取' 关键词，根据 pdf-line-print 文档中的 When to Use 部分，当用户提到 '按行读取pdf' 时应触发此技能"
}}
```

现在请分析用户的请求并返回 JSON。只返回 JSON，不要有任何其他文字。"""

    def _get_parameter_extraction_template(self) -> str:
        """参数提取提示词"""
        return """从用户请求中提取技能参数。

技能信息：
{skill_info}

用户请求：{user_query}

请提取以下参数的值：
{required_params}

返回 JSON 格式：
```json
{{
  "params": {{
    "参数名": "提取的值"
  }}
}}
```"""


# 全局提示词库实例
_prompt_library: Optional[PromptLibrary] = None


def get_prompt_library() -> PromptLibrary:
    """获取提示词库实例（单例模式）"""
    global _prompt_library
    if _prompt_library is None:
        _prompt_library = PromptLibrary()
    return _prompt_library


def reset_prompt_library():
    """重置提示词库（主要用于测试）"""
    global _prompt_library
    _prompt_library = None
