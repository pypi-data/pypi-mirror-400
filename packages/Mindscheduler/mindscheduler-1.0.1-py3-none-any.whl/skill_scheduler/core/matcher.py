import re
import logging
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher

from .skill import Skill, SkillManager


logger = logging.getLogger(__name__)


class RuleMatcher:
    def __init__(self, threshold: float = 0.3, enable_embedding: bool = False):
        self.threshold = threshold
        self.enable_embedding = enable_embedding
        self._model = None

        if self.enable_embedding:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                logger.warning("sentence-transformers not installed, using keyword matching")
                self.enable_embedding = False

    def match(self, query: str, skills: List[Skill]) -> Tuple[Optional[Skill], float]:
        if not skills:
            return None, 0.0

        query_lower = query.lower()

        if self.enable_embedding and self._model:
            return self._semantic_match(query, skills)

        return self._keyword_match(query_lower, skills)

    def _keyword_match(self, query: str, skills: List[Skill]) -> Tuple[Optional[Skill], float]:
        best_skill = None
        best_score = 0.0

        for skill in skills:
            score = self._calculate_score(query, skill)
            if score > best_score and score >= self.threshold:
                best_score = score
                best_skill = skill

        return best_skill, best_score

    def _semantic_match(self, query: str, skills: List[Skill]) -> Tuple[Optional[Skill], float]:
        if not self._model:
            return self._keyword_match(query.lower(), skills)

        query_embedding = self._model.encode(query)

        best_skill = None
        best_score = 0.0

        for skill in skills:
            text = (skill.title or "") + " " + skill.description + " " + " ".join(skill.tags)
            skill_embedding = self._model.encode(text)

            from numpy import dot
            from numpy.linalg import norm
            similarity = dot(query_embedding, skill_embedding) / (norm(query_embedding) * norm(skill_embedding))

            if similarity > best_score and similarity >= self.threshold:
                best_score = similarity
                best_skill = skill

        return best_skill, best_score

    def _calculate_score(self, query: str, skill: Skill) -> float:
        score = 0.0

        skill_name = skill.name.lower()
        if skill_name in query:
            score += 0.8  # 增加精确匹配的权重
        else:
            # 如果精确匹配失败，尝试匹配 skill name 的各个部分（处理 hyphen）
            name_parts = skill_name.replace('-', ' ').replace('_', ' ').split()
            for part in name_parts:
                if part in query.split():
                    score += 0.4

        for tag in skill.tags:
            if tag.lower() in query:
                score += 0.3

        # 同时匹配 title 和 description
        title_lower = skill.title.lower() if skill.title else ""
        description_lower = skill.description.lower()
        combined_text = title_lower + " " + description_lower

        # 对于中文文本，使用字符级别的序列匹配
        # 检测是否包含中文字符
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in query)

        if has_chinese:
            # 中文文本：直接使用序列匹配（字符级）
            ratio = SequenceMatcher(None, query, combined_text).ratio()

            # 关键词匹配加分（针对特定功能）
            keyword_boost = 0.0
            if "按行" in query and "line-print" in skill.tags:
                keyword_boost += 0.3  # 按行打印匹配
            if "批量" in query and "batch" in skill.tags:
                keyword_boost += 0.3  # 批量处理匹配
            if "逐行" in query and "line-print" in skill.tags:
                keyword_boost += 0.3  # 逐行打印匹配

            score += ratio * 0.5 + keyword_boost  # 降低序列匹配权重，增加关键词权重
        else:
            # 英文文本：使用词匹配
            description_words = combined_text.split()
            query_words = set(query.split())

            matches = sum(1 for word in query_words if word in description_words)
            if matches > 0:
                score += min(matches * 0.1, 0.5)

            # 使用序列匹配作为补充
            ratio = SequenceMatcher(None, query, combined_text).ratio()
            score += ratio * 0.3

        return min(score, 1.0)

    def match_all(self, query: str, skills: List[Skill], top_k: int = 5) -> List[Tuple[Skill, float]]:
        if self.enable_embedding and self._model:
            return self._semantic_match_all(query, skills, top_k)
        else:
            return self._keyword_match_all(query, skills, top_k)

    def _keyword_match_all(self, query: str, skills: List[Skill], top_k: int) -> List[Tuple[Skill, float]]:
        query_lower = query.lower()
        results = []

        for skill in skills:
            score = self._calculate_score(query_lower, skill)
            results.append((skill, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _semantic_match_all(self, query: str, skills: List[Skill], top_k: int) -> List[Tuple[Skill, float]]:
        if not self._model:
            return self._keyword_match_all(query.lower(), skills, top_k)

        query_embedding = self._model.encode(query)
        results = []

        for skill in skills:
            text = (skill.title or "") + " " + skill.description + " " + " ".join(skill.tags)
            skill_embedding = self._model.encode(text)

            from numpy import dot
            from numpy.linalg import norm
            similarity = dot(query_embedding, skill_embedding) / (norm(query_embedding) * norm(skill_embedding))

            results.append((skill, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
