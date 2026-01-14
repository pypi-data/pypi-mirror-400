"""
Skill Discovery System
======================

Provides mechanisms for discovering, searching, and recommending skills
based on user intent, context, and task requirements.

Features:
- Intent-based skill matching
- Semantic search over skill descriptions
- Context-aware recommendations
- Skill graph for related skills
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from skills.base import SkillCategory, SkillLevel, SkillMetadata
from skills.registry import SkillRegistry, get_registry
from agents.model_router import query_reasoning

logger = logging.getLogger(__name__)


@dataclass
class SkillMatch:
    """A skill match with relevance information."""
    skill_id: str
    metadata: SkillMetadata
    score: float                      # 0-1 relevance score
    match_reasons: List[str] = field(default_factory=list)
    context_fit: float = 1.0          # How well it fits current context


@dataclass
class IntentAnalysis:
    """Analysis of user intent from query."""
    primary_category: Optional[SkillCategory] = None
    secondary_categories: List[SkillCategory] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    action_verbs: List[str] = field(default_factory=list)
    complexity_hint: SkillLevel = SkillLevel.INTERMEDIATE
    confidence: float = 0.5


class SkillDiscovery:
    """
    Discovers and recommends skills based on user needs.

    Supports:
    - Natural language queries
    - Category browsing
    - Related skill suggestions
    - Context-aware filtering
    """

    # Keywords mapped to categories
    CATEGORY_KEYWORDS = {
        SkillCategory.CODE: [
            "code", "program", "programming", "function", "class", "debug",
            "refactor", "python", "javascript", "typescript", "review",
            "test", "unittest", "api", "algorithm", "syntax"
        ],
        SkillCategory.DATA: [
            "data", "analysis", "analyze", "statistics", "dataset", "csv",
            "json", "transform", "clean", "aggregate", "query", "sql",
            "database", "pandas", "excel", "chart", "visualize"
        ],
        SkillCategory.WRITING: [
            "write", "writing", "draft", "edit", "proofread", "article",
            "blog", "documentation", "email", "content", "copy", "grammar",
            "spelling", "style", "tone"
        ],
        SkillCategory.RESEARCH: [
            "research", "search", "find", "lookup", "investigate", "learn",
            "understand", "explain", "summarize", "source", "reference"
        ],
        SkillCategory.AUTOMATION: [
            "automate", "automation", "workflow", "script", "batch", "task",
            "schedule", "trigger", "pipeline", "ci", "cd", "deploy"
        ],
        SkillCategory.INTEGRATION: [
            "integrate", "integration", "api", "connect", "webhook", "sync",
            "external", "service", "oauth", "authentication"
        ],
        SkillCategory.REASONING: [
            "reason", "logic", "solve", "problem", "decision", "analyze",
            "evaluate", "compare", "pros", "cons", "trade-off"
        ],
        SkillCategory.CREATIVE: [
            "creative", "generate", "idea", "brainstorm", "design", "story",
            "narrative", "innovative", "unique", "original"
        ],
    }

    # Action verbs indicating task type
    ACTION_VERBS = {
        "generate": ["generate", "create", "make", "produce", "build"],
        "analyze": ["analyze", "examine", "inspect", "review", "check"],
        "transform": ["transform", "convert", "change", "modify", "update"],
        "fix": ["fix", "repair", "correct", "debug", "resolve"],
        "improve": ["improve", "enhance", "optimize", "refine", "polish"],
        "explain": ["explain", "describe", "clarify", "document", "teach"],
        "search": ["search", "find", "locate", "discover", "lookup"],
    }

    def __init__(self, registry: Optional[SkillRegistry] = None):
        self.registry = registry or get_registry()
        self._intent_handlers: Dict[str, Callable] = {}

    def discover(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        max_results: int = 5,
    ) -> List[SkillMatch]:
        """
        Discover skills matching a natural language query.

        Args:
            query: Natural language description of need
            context: Optional context (current file, project type, etc.)
            max_results: Maximum number of results

        Returns:
            List of SkillMatch objects, ranked by relevance
        """
        # Analyze intent
        intent = self._analyze_intent(query)

        # Get candidate skills
        candidates = self._get_candidates(intent, context)

        # 1. Initial Keyword Scoring
        matches = []
        for skill_id in candidates:
            score, reasons = self._score_skill(skill_id, query, intent, context)
            # Accept all candidates for potential semantic re-ranking
            metadata = self.registry.get_metadata(skill_id)
            matches.append(SkillMatch(
                skill_id=skill_id,
                metadata=metadata,
                score=score,
                match_reasons=reasons,
            ))

        # Sort by initial score
        matches.sort(key=lambda m: m.score, reverse=True)

        # 2. Semantic Re-ranking (Top 20)
        # Only re-rank if we have matches and the query is "semantic" (long enough)
        if matches and len(query.split()) > 2:
            # Check up to 20 candidates to catch semantic matches that failed keyword search
            top_matches = matches[:20]
            for match in top_matches:
                semantic_score = self._score_semantic(match.skill_id, query)
                if semantic_score > 0:
                    # Blend scores: 30% keyword, 70% semantic (boost semantic weight)
                    match.score = (match.score * 0.3) + (semantic_score * 0.7)
                    match.match_reasons.append(f"Semantic match: {semantic_score:.2f}")
            
            # Re-sort after semantic update
            matches.sort(key=lambda m: m.score, reverse=True)

        return matches[:max_results]

    def recommend_for_task(
        self,
        task_description: str,
        available_context: Dict[str, Any],
    ) -> List[SkillMatch]:
        """
        Recommend skills for a specific task.

        Considers:
        - Task requirements
        - Available context (files, data, etc.)
        - Skill dependencies
        - Resource constraints
        """
        matches = self.discover(task_description, available_context)

        # Filter by what's actually available/loadable
        filtered = []
        for match in matches:
            # Check dependencies
            try:
                deps = self.registry.resolve_dependencies(match.skill_id)
                has_all_deps = True
                for dep_id in deps:
                    if not self.registry.has_skill(dep_id):
                        has_all_deps = False
                        break

                if has_all_deps:
                    filtered.append(match)
            except Exception:
                continue

        return filtered

    def get_related_skills(
        self,
        skill_id: str,
        max_results: int = 3,
    ) -> List[SkillMetadata]:
        """
        Get skills related to a given skill.

        Related skills include:
        - Same category
        - Shared tags
        - Dependency relationships
        - Commonly used together
        """
        if not self.registry.has_skill(skill_id):
            return []

        source = self.registry.get_metadata(skill_id)
        related = []
        scores = {}

        # Search by category
        same_category = self.registry.list_skills(category=source.category)
        for meta in same_category:
            if meta.id != skill_id:
                scores[meta.id] = scores.get(meta.id, 0) + 0.3

        # Search by tags
        if source.tags:
            for tag in source.tags:
                tagged = self.registry.list_skills(tags=[tag])
                for meta in tagged:
                    if meta.id != skill_id:
                        scores[meta.id] = scores.get(meta.id, 0) + 0.2

        # Check dependencies (both directions)
        for meta in self.registry.list_skills():
            if meta.id == skill_id:
                continue

            # Check if this skill depends on target
            for dep in meta.dependencies:
                if dep.skill_id == skill_id:
                    scores[meta.id] = scores.get(meta.id, 0) + 0.4
                    break

            # Check if target depends on this skill
            for dep in source.dependencies:
                if dep.skill_id == meta.id:
                    scores[meta.id] = scores.get(meta.id, 0) + 0.4
                    break

        # Sort by score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        for skill_id in sorted_ids[:max_results]:
            related.append(self.registry.get_metadata(skill_id))

        return related

    def browse_by_category(
        self,
        category: Optional[SkillCategory] = None,
    ) -> Dict[SkillCategory, List[SkillMetadata]]:
        """
        Browse skills organized by category.

        Returns:
            Dict mapping categories to their skills
        """
        if category:
            return {category: self.registry.list_skills(category=category)}

        result = {}
        for cat in SkillCategory:
            skills = self.registry.list_skills(category=cat)
            if skills:
                result[cat] = skills

        return result

    def suggest_for_context(
        self,
        file_extension: Optional[str] = None,
        project_type: Optional[str] = None,
        current_task: Optional[str] = None,
    ) -> List[SkillMetadata]:
        """
        Suggest skills based on current context.

        Args:
            file_extension: Current file extension (e.g., ".py")
            project_type: Project type (e.g., "web", "data-science")
            current_task: What user is currently doing

        Returns:
            List of suggested skills
        """
        suggestions = []
        seen = set()

        # Extension-based suggestions
        extension_skills = {
            ".py": ["code/python", "code/review"],
            ".js": ["code/javascript"],
            ".ts": ["code/typescript"],
            ".md": ["writing/edit", "writing/draft"],
            ".json": ["data/transform"],
            ".csv": ["data/analysis", "data/transform"],
            ".sql": ["data/query"],
        }

        if file_extension:
            skill_ids = extension_skills.get(file_extension, [])
            for skill_id in skill_ids:
                if self.registry.has_skill(skill_id) and skill_id not in seen:
                    suggestions.append(self.registry.get_metadata(skill_id))
                    seen.add(skill_id)

        # Project type suggestions
        project_skills = {
            "web": ["code/javascript", "code/typescript", "writing/docs"],
            "data-science": ["data/analysis", "data/transform", "code/python"],
            "backend": ["code/python", "code/review", "data/query"],
            "documentation": ["writing/draft", "writing/edit"],
        }

        if project_type:
            skill_ids = project_skills.get(project_type, [])
            for skill_id in skill_ids:
                if self.registry.has_skill(skill_id) and skill_id not in seen:
                    suggestions.append(self.registry.get_metadata(skill_id))
                    seen.add(skill_id)

        # Current task suggestions
        if current_task:
            matches = self.discover(current_task, max_results=3)
            for match in matches:
                if match.skill_id not in seen:
                    suggestions.append(match.metadata)
                    seen.add(match.skill_id)

        return suggestions[:5]

    def _analyze_intent(self, query: str) -> IntentAnalysis:
        """Analyze user intent from natural language query."""
        query_lower = query.lower()
        words = re.findall(r'\b\w+\b', query_lower)

        # Find matching categories
        category_scores: Dict[SkillCategory, int] = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in words)
            if score > 0:
                category_scores[category] = score

        # Determine primary category
        primary = None
        secondary = []
        if category_scores:
            sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            primary = sorted_cats[0][0]
            secondary = [cat for cat, _ in sorted_cats[1:3]]

        # Find action verbs
        action_verbs = []
        for action, verbs in self.ACTION_VERBS.items():
            if any(v in words for v in verbs):
                action_verbs.append(action)

        # Extract keywords (non-stopwords)
        stopwords = {"the", "a", "an", "to", "for", "in", "on", "with", "and", "or", "is", "are", "this", "that", "my", "i", "want", "need", "please", "help", "me"}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]

        # Estimate complexity
        complexity_hints = {
            SkillLevel.BASIC: ["simple", "basic", "quick", "easy"],
            SkillLevel.INTERMEDIATE: ["standard", "normal", "typical"],
            SkillLevel.ADVANCED: ["complex", "advanced", "detailed"],
            SkillLevel.EXPERT: ["expert", "comprehensive", "full"],
        }

        complexity = SkillLevel.INTERMEDIATE
        for level, hints in complexity_hints.items():
            if any(h in words for h in hints):
                complexity = level
                break

        # Calculate confidence
        confidence = 0.3
        if primary:
            confidence += 0.3
        if action_verbs:
            confidence += 0.2
        if len(keywords) > 2:
            confidence += 0.2

        return IntentAnalysis(
            primary_category=primary,
            secondary_categories=secondary,
            keywords=keywords[:10],
            action_verbs=action_verbs,
            complexity_hint=complexity,
            confidence=min(1.0, confidence),
        )

    def _get_candidates(
        self,
        intent: IntentAnalysis,
        context: Optional[Dict[str, Any]],
    ) -> Set[str]:
        """Get candidate skill IDs based on intent."""
        candidates = set()

        # From primary category
        if intent.primary_category:
            for meta in self.registry.list_skills(category=intent.primary_category):
                candidates.add(meta.id)

        # From secondary categories
        for cat in intent.secondary_categories:
            for meta in self.registry.list_skills(category=cat):
                candidates.add(meta.id)

        # From keyword search
        for keyword in intent.keywords[:5]:
            for meta in self.registry.search_skills(keyword, limit=3):
                candidates.add(meta.id)

        # If no candidates, get all
        if not candidates:
            for meta in self.registry.list_skills():
                candidates.add(meta.id)

        return candidates

    def _score_skill(
        self,
        skill_id: str,
        query: str,
        intent: IntentAnalysis,
        context: Optional[Dict[str, Any]],
    ) -> Tuple[float, List[str]]:
        """Score a skill's relevance to the query."""
        metadata = self.registry.get_metadata(skill_id)
        score = 0.0
        reasons = []

        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))

        # Category match
        if metadata.category == intent.primary_category:
            score += 0.3
            reasons.append(f"Matches category: {metadata.category.value}")
        elif metadata.category in intent.secondary_categories:
            score += 0.15
            reasons.append(f"Related category: {metadata.category.value}")

        # Name/description match
        name_lower = metadata.name.lower()
        desc_lower = metadata.description.lower()

        for keyword in intent.keywords:
            if keyword in name_lower:
                score += 0.2
                reasons.append(f"Name contains: {keyword}")
            elif keyword in desc_lower:
                score += 0.1
                reasons.append(f"Description contains: {keyword}")

        # Tag match
        for tag in metadata.tags:
            if tag.lower() in query_words:
                score += 0.15
                reasons.append(f"Tag match: {tag}")

        # Skill ID contains query terms
        skill_parts = set(skill_id.lower().split("/"))
        for part in skill_parts:
            if part in query_words:
                score += 0.2
                reasons.append(f"ID match: {part}")

        # Level appropriateness
        if metadata.level == intent.complexity_hint:
            score += 0.1
            reasons.append(f"Complexity match: {metadata.level.value}")

        return min(1.0, score), reasons

    def _score_semantic(self, skill_id: str, query: str) -> float:
        """
        Use a reasoning LLM to score semantic relevance between query and skill.
        Returns a score between 0.0 and 1.0.
        """
        try:
            metadata = self.registry.get_metadata(skill_id)
            prompt = f"""You are an expert assistant responsible for routing tasks.
Your goal is to determine how relevant a specific skill is to a user's request.

Think step-by-step:
1. Analyze the user's core intent. What do they fundamentally want to achieve?
2. Analyze the skill's purpose based on its name, description, and tags. What problem does it solve?
3. Compare the user's intent to the skill's purpose. Does the skill directly help achieve the user's goal?
4. Based on your analysis, provide a numeric relevance score between 0.0 (not relevant) and 1.0 (a perfect match).

User Request: "{query}"

Skill Name: "{metadata.name}"
Skill Description: "{metadata.description}"

After your analysis, output the final numeric score on a new line, by itself, enclosed in <score> tags. For example: <score>0.85</score>
"""
            # Use query_reasoning (DeepSeek-R1) for better analysis
            response = query_reasoning(prompt, max_tokens=250).strip()
            
            # Extract number from <score> tag
            match = re.search(r"<score>(\d\.?\d*)</score>", response)
            if match:
                return float(match.group(1))
            
            # Fallback for just a number
            match = re.search(r"(\d\.?\d+)", response)
            if match:
                return float(match.group(0))

            return 0.0
        except Exception as e:
            logger.warning(f"Semantic scoring failed for {skill_id}: {e}")
            return 0.0



# Convenience functions
_discovery: Optional[SkillDiscovery] = None


def get_discovery() -> SkillDiscovery:
    """Get the global skill discovery instance."""
    global _discovery
    if _discovery is None:
        _discovery = SkillDiscovery()
    return _discovery


def discover_skills(query: str, max_results: int = 5) -> List[SkillMatch]:
    """Discover skills matching a query."""
    return get_discovery().discover(query, max_results=max_results)


def recommend_skills(task: str, context: Dict[str, Any] = None) -> List[SkillMatch]:
    """Recommend skills for a task."""
    return get_discovery().recommend_for_task(task, context or {})
