import json
from typing import Dict, List, Any, Optional, Tuple, Set

from .base import LLMAdapter
from ..prompts import get_prompt_library


def validate_intent_result(result: Any, available_skill_names: Set[str]) -> Tuple[bool, Optional[str]]:
    """
    校验 LLM 返回的意图解析结果格式

    Args:
        result: LLM 返回的结果
        available_skill_names: 可用的技能名称集合

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(result, dict):
        return False, f"Expected dict, got {type(result).__name__}"

    # 检查是否有 error 字段（LLM 调用失败的情况）
    if "error" in result:
        # 有错误时，skills 应该为空列表
        if "skills" in result and result["skills"]:
            return False, "Error response should not contain skills"
        return True, None

    # 检查必需字段
    if "skills" not in result:
        return False, "Missing required field: 'skills'"

    skills = result.get("skills")
    if not isinstance(skills, list):
        return False, f"Field 'skills' must be a list, got {type(skills).__name__}"

    # 校验每个 skill 项
    for i, skill in enumerate(skills):
        if not isinstance(skill, dict):
            return False, f"Skill at index {i} must be a dict, got {type(skill).__name__}"

        # 检查 name 字段
        if "name" not in skill:
            return False, f"Skill at index {i} missing required field: 'name'"

        skill_name = skill["name"]
        if not isinstance(skill_name, str):
            return False, f"Skill name at index {i} must be a string, got {type(skill_name).__name__}"

        # 检查技能名称是否在可用列表中
        if available_skill_names and skill_name not in available_skill_names:
            return False, f"Unknown skill '{skill_name}' at index {i}. Available skills: {', '.join(sorted(available_skill_names))}"

        # 检查 params 字段（可选）
        if "params" in skill:
            params = skill["params"]
            if not isinstance(params, dict):
                return False, f"Skill params at index {i} must be a dict, got {type(params).__name__}"

    return True, None


class OpenAIAdapter(LLMAdapter):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None, use_prompt_templates: bool = True):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
        self.use_prompt_templates = use_prompt_templates
        self.prompt_library = get_prompt_library() if use_prompt_templates else None

    def chat_completion(self, messages: List[Dict], temperature: float = 0.3) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )

            return response.choices[0].message.content

        except ImportError:
            raise ImportError("openai package is required. Install it with: pip install openai")
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

    def parse_intent(self, query: str, skills: list) -> Dict:
        # 获取可用技能名称集合，用于校验
        available_skill_names = {skill.name for skill in skills}

        skills_list = []
        for skill in skills:
            # 获取完整的技能文档
            full_docs = skill.get_full_definition()
            documentation = skill.get_documentation()

            skills_list.append({
                "name": skill.name,
                "description": skill.description,
                "tags": skill.tags,
                "inputs": {name: {"type": inp.type, "description": inp.description}
                          for name, inp in skill.inputs.items()},
                "documentation": documentation,  # Markdown 文档部分
                "full_definition": full_docs   # 完整 skill.md 内容
            })

        # 使用提示词模板库（如果启用）
        if self.use_prompt_templates and self.prompt_library:
            intent_template = self.prompt_library.get_intent_template()
            if intent_template:
                # 使用带完整文档的格式
                system_prompt = intent_template.format_system_with_docs(
                    skills_list=skills_list
                ) if hasattr(intent_template, 'format_system_with_docs') else intent_template.format_system(
                    skills_list=json.dumps(skills_list, ensure_ascii=False, indent=2)
                )
                user_prompt = intent_template.format(user_query=query)

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            else:
                messages = [{"role": "user", "content": self._get_default_prompt_with_docs(query, skills_list)}]
        else:
            # 使用带完整文档的默认提示词
            messages = [{"role": "user", "content": self._get_default_prompt_with_docs(query, skills_list)}]

        try:
            response = self.chat_completion(messages, temperature=0.3)

            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            result = json.loads(response.strip())

            # 转换为统一格式
            if "skills" not in result and "required_skills" in result:
                result["skills"] = result.pop("required_skills")

            # 校验返回格式
            is_valid, error_msg = validate_intent_result(result, available_skill_names)
            if not is_valid:
                return {
                    "intent": "unknown",
                    "skills": [],
                    "error": f"LLM response validation failed: {error_msg}",
                    "raw_response": result
                }

            return result

        except json.JSONDecodeError as e:
            return {
                "intent": "unknown",
                "skills": [],
                "error": f"Failed to parse LLM response as JSON: {e}"
            }
        except Exception as e:
            return {
                "intent": "unknown",
                "skills": [],
                "error": f"LLM call failed: {e}"
            }

    def _get_default_prompt(self, query: str, skills_list: list) -> str:
        """获取默认提示词（向后兼容）"""
        return f"""You are a skill scheduler assistant. Parse the user's request and identify the required skills.

Available skills:
{json.dumps(skills_list, ensure_ascii=False, indent=2)}

User request: {query}

Respond with a JSON object containing:
- intent: core intent (string)
- skills: list of skills needed, each with "name" and "params" (extract from user request if mentioned)
- execution_order: list of step indices

Example response format:
{{
  "intent": "read and process PDF file",
  "skills": [
    {{"name": "pdf-read", "params": {{"file": "./document.pdf"}}}}
  ],
  "execution_order": [0]
}}

Respond only with the JSON, no other text:"""

    def _get_default_prompt_with_docs(self, query: str, skills_list: list) -> str:
        """获取带完整文档的提示词"""
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

        return f"""You are an intelligent skill scheduling assistant. Your task is to understand the user's request and match it with the most appropriate skill(s).

# Available Skills

{all_skills}

# User Request

{query}

# Your Task

1. Analyze the user's request carefully
2. Read the complete documentation for each skill above
3. Match the request to the most appropriate skill based on:
   - The skill's description
   - The skill's documentation (which includes usage examples and when to use)
   - The required inputs
4. Extract parameters from the user's request that match the skill's input requirements

# Response Format

Respond with a JSON object:

```json
{{
  "intent": "brief description of what the user wants to do",
  "reasoning": "explanation of why you selected this skill",
  "skills": [
    {{
      "name": "skill-name",
      "params": {{
        "param1": "value1",
        "param2": "value2"
      }}
    }}
  ]
}}
```

Important:
- Use the EXACT skill name from the list above
- Extract parameters from the user's request that match the skill's input requirements
- If a required parameter is missing from the user's request, set it to null
- Respond only with valid JSON, no other text"""
