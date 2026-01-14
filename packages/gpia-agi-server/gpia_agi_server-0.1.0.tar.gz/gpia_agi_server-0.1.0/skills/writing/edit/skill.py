"""
Content Editing Skill
=====================

Professional editing and refinement including grammar, clarity,
style consistency, and structural improvements.
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillDependency,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class EditSkill(Skill):
    """
    Content editing skill providing:
    - Grammar and spelling correction
    - Style consistency
    - Clarity improvements
    - Structural suggestions
    - Readability analysis
    """

    EDIT_TYPES = [
        "grammar",
        "spelling",
        "style",
        "clarity",
        "structure",
        "conciseness",
        "all",
    ]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="writing/edit",
            name="Content Editing",
            description="Professional editing including grammar, clarity, style consistency, and structural improvements.",
            version="0.1.0",
            category=SkillCategory.WRITING,
            level=SkillLevel.INTERMEDIATE,
            tags=["editing", "proofreading", "grammar", "style", "clarity"],
            dependencies=[
                SkillDependency(
                    skill_id="writing/draft",
                    optional=True,
                    reason="Often follows drafting",
                )
            ],
            estimated_tokens=500,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to edit",
                },
                "edit_types": {
                    "type": "array",
                    "items": {"type": "string", "enum": self.EDIT_TYPES},
                    "default": ["all"],
                },
                "style_guide": {
                    "type": "string",
                    "description": "Style guide to follow (e.g., active_voice, ap_style)",
                },
                "target_audience": {
                    "type": "string",
                    "description": "Target audience for readability",
                },
                "preserve_tone": {
                    "type": "boolean",
                    "default": True,
                },
            },
            "required": ["text"],
        }

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        start_time = time.time()

        text = input_data.get("text", "")
        edit_types = input_data.get("edit_types", ["all"])
        style_guide = input_data.get("style_guide", "")
        target_audience = input_data.get("target_audience", "general")

        if "all" in edit_types:
            edit_types = self.EDIT_TYPES[:-1]

        if not text.strip():
            return SkillResult(
                success=False,
                output=None,
                error="No text provided",
                error_code="EMPTY_INPUT",
                skill_id=self.metadata().id,
            )

        try:
            all_changes = []
            edited_text = text

            # Apply edits in order
            if "grammar" in edit_types:
                edited_text, changes = self._check_grammar(edited_text)
                all_changes.extend(changes)

            if "spelling" in edit_types:
                edited_text, changes = self._check_spelling(edited_text)
                all_changes.extend(changes)

            if "style" in edit_types:
                edited_text, changes = self._check_style(edited_text, style_guide)
                all_changes.extend(changes)

            if "clarity" in edit_types:
                edited_text, changes = self._check_clarity(edited_text)
                all_changes.extend(changes)

            if "conciseness" in edit_types:
                edited_text, changes = self._check_conciseness(edited_text)
                all_changes.extend(changes)

            if "structure" in edit_types:
                structure_suggestions = self._analyze_structure(text)
            else:
                structure_suggestions = []

            # Calculate metrics
            readability = self._calculate_readability(edited_text)

            execution_time = int((time.time() - start_time) * 1000)

            return SkillResult(
                success=True,
                output={
                    "edited_text": edited_text,
                    "changes": all_changes,
                    "change_count": len(all_changes),
                    "structure_suggestions": structure_suggestions,
                    "readability": readability,
                    "improvement_summary": self._summarize_improvements(all_changes),
                },
                execution_time_ms=execution_time,
                skill_id=self.metadata().id,
                suggestions=self._get_suggestions(all_changes),
                related_skills=["writing/draft"],
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EDIT_ERROR",
                skill_id=self.metadata().id,
            )

    def _check_grammar(self, text: str) -> Tuple[str, List[Dict]]:
        """Check and fix common grammar issues."""
        changes = []
        edited = text

        # Common grammar patterns
        patterns = [
            # Their/They're/There
            (r"\btheir\s+(going|coming|doing|making|being)\b",
             lambda m: f"they're {m.group(1)}",
             "grammar", "their → they're (contraction)"),

            # Your/You're
            (r"\byour\s+(going|coming|doing|making|being|right|wrong)\b",
             lambda m: f"you're {m.group(1)}",
             "grammar", "your → you're (contraction)"),

            # Its/It's
            (r"\bits\s+(not|a|an|the|going|coming)\b",
             lambda m: f"it's {m.group(1)}",
             "grammar", "its → it's (contraction)"),

            # Subject-verb agreement
            (r"\b(he|she|it)\s+don't\b",
             lambda m: f"{m.group(1)} doesn't",
             "grammar", "Subject-verb agreement"),

            # Double negatives
            (r"\bdon't\s+got\s+no\b",
             lambda m: "don't have any",
             "grammar", "Double negative"),

            # Comma before 'and' in compound sentences
            (r"(\w+)\s+and\s+(he|she|they|we|it)\s+(was|were|is|are)",
             lambda m: f"{m.group(1)}, and {m.group(2)} {m.group(3)}",
             "grammar", "Added comma before conjunction"),
        ]

        for pattern, replacement, change_type, explanation in patterns:
            matches = list(re.finditer(pattern, edited, re.IGNORECASE))
            for match in reversed(matches):  # Reverse to maintain positions
                original = match.group(0)
                if callable(replacement):
                    new_text = replacement(match)
                else:
                    new_text = replacement

                if original.lower() != new_text.lower():
                    edited = edited[:match.start()] + new_text + edited[match.end():]
                    changes.append({
                        "type": change_type,
                        "original": original,
                        "corrected": new_text,
                        "explanation": explanation,
                    })

        return edited, changes

    def _check_spelling(self, text: str) -> Tuple[str, List[Dict]]:
        """Check and fix common spelling issues."""
        changes = []
        edited = text

        # Common misspellings
        misspellings = {
            r"\bdefinately\b": ("definitely", "Common misspelling"),
            r"\boccured\b": ("occurred", "Double 'c'"),
            r"\brecieve\b": ("receive", "i before e"),
            r"\bseperately\b": ("separately", "Correct spelling"),
            r"\buntill\b": ("until", "Single 'l'"),
            r"\bweird\b": ("weird", "Exception to i before e"),
            r"\bwhich ever\b": ("whichever", "One word"),
            r"\balot\b": ("a lot", "Two words"),
            r"\bnoone\b": ("no one", "Two words"),
            r"\bwether\b": ("whether", "Missing 'h'"),
            r"\bteh\b": ("the", "Typo"),
            r"\badn\b": ("and", "Typo"),
            r"\bdont\b": ("don't", "Missing apostrophe"),
            r"\bwont\b": ("won't", "Missing apostrophe"),
            r"\bcant\b": ("can't", "Missing apostrophe"),
            r"\bcouldnt\b": ("couldn't", "Missing apostrophe"),
            r"\bwouldnt\b": ("wouldn't", "Missing apostrophe"),
            r"\bshouldnt\b": ("shouldn't", "Missing apostrophe"),
        }

        for pattern, (correction, explanation) in misspellings.items():
            matches = list(re.finditer(pattern, edited, re.IGNORECASE))
            for match in reversed(matches):
                original = match.group(0)
                # Preserve case
                if original.isupper():
                    new_text = correction.upper()
                elif original[0].isupper():
                    new_text = correction.capitalize()
                else:
                    new_text = correction

                edited = edited[:match.start()] + new_text + edited[match.end():]
                changes.append({
                    "type": "spelling",
                    "original": original,
                    "corrected": new_text,
                    "explanation": explanation,
                })

        return edited, changes

    def _check_style(self, text: str, style_guide: str) -> Tuple[str, List[Dict]]:
        """Check and improve style based on guide."""
        changes = []
        edited = text

        # Active voice conversion
        if style_guide == "active_voice" or not style_guide:
            passive_patterns = [
                (r"was (\w+ed) by",
                 "Passive voice - consider active construction",
                 "style"),
                (r"were (\w+ed) by",
                 "Passive voice - consider active construction",
                 "style"),
                (r"is being (\w+ed)",
                 "Passive voice - consider active construction",
                 "style"),
            ]

            for pattern, explanation, change_type in passive_patterns:
                matches = list(re.finditer(pattern, edited))
                for match in matches:
                    changes.append({
                        "type": change_type,
                        "original": match.group(0),
                        "corrected": "[Consider rewriting in active voice]",
                        "explanation": explanation,
                        "suggestion_only": True,
                    })

        # Weak words
        weak_words = [
            (r"\bvery\s+(\w+)", "Consider stronger word", "style"),
            (r"\breally\s+(\w+)", "Consider stronger word", "style"),
            (r"\bjust\s+", "'Just' often unnecessary", "style"),
            (r"\bactually\s+", "'Actually' often unnecessary", "style"),
            (r"\bbasically\s+", "'Basically' often unnecessary", "style"),
        ]

        for pattern, explanation, change_type in weak_words:
            matches = list(re.finditer(pattern, edited, re.IGNORECASE))
            for match in matches:
                changes.append({
                    "type": change_type,
                    "original": match.group(0),
                    "explanation": explanation,
                    "suggestion_only": True,
                })

        return edited, changes

    def _check_clarity(self, text: str) -> Tuple[str, List[Dict]]:
        """Check for clarity issues."""
        changes = []
        edited = text

        # Ambiguous pronouns
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            pronoun_count = len(re.findall(r'\b(it|this|that|they|them)\b', sentence, re.IGNORECASE))
            if pronoun_count > 2:
                changes.append({
                    "type": "clarity",
                    "original": sentence.strip()[:50] + "...",
                    "explanation": "Multiple pronouns may cause ambiguity",
                    "suggestion_only": True,
                })

        # Long sentences
        for sentence in sentences:
            words = len(sentence.split())
            if words > 35:
                changes.append({
                    "type": "clarity",
                    "original": sentence.strip()[:50] + "...",
                    "explanation": f"Sentence has {words} words - consider breaking up",
                    "suggestion_only": True,
                })

        # Jargon/complexity warnings
        complex_phrases = [
            r"utilize",  # use
            r"implement",  # do/make
            r"facilitate",  # help
            r"leverage",  # use
            r"synergy",
            r"paradigm",
        ]

        for phrase in complex_phrases:
            if re.search(rf'\b{phrase}\b', text, re.IGNORECASE):
                changes.append({
                    "type": "clarity",
                    "original": phrase,
                    "explanation": "Consider simpler alternative",
                    "suggestion_only": True,
                })

        return edited, changes

    def _check_conciseness(self, text: str) -> Tuple[str, List[Dict]]:
        """Check for wordiness and redundancy."""
        changes = []
        edited = text

        # Wordy phrases
        wordy_phrases = {
            r"\bat this point in time\b": "now",
            r"\bdue to the fact that\b": "because",
            r"\bin order to\b": "to",
            r"\bin the event that\b": "if",
            r"\bfor the purpose of\b": "to",
            r"\bin spite of the fact that\b": "although",
            r"\bwith regard to\b": "about",
            r"\bin the near future\b": "soon",
            r"\bat the present time\b": "now",
            r"\bhas the ability to\b": "can",
            r"\bis able to\b": "can",
            r"\bmake a decision\b": "decide",
            r"\btake into consideration\b": "consider",
        }

        for pattern, replacement in wordy_phrases.items():
            matches = list(re.finditer(pattern, edited, re.IGNORECASE))
            for match in reversed(matches):
                original = match.group(0)
                edited = edited[:match.start()] + replacement + edited[match.end():]
                changes.append({
                    "type": "conciseness",
                    "original": original,
                    "corrected": replacement,
                    "explanation": "Wordy phrase simplified",
                })

        # Redundant phrases
        redundancies = [
            r"\bcompletely finished\b",
            r"\bpast history\b",
            r"\bfuture plans\b",
            r"\bfinal outcome\b",
            r"\bfree gift\b",
            r"\bpersonal opinion\b",
            r"\bunexpected surprise\b",
        ]

        for pattern in redundancies:
            if re.search(pattern, text, re.IGNORECASE):
                changes.append({
                    "type": "conciseness",
                    "original": pattern.replace(r"\b", "").replace("\\", ""),
                    "explanation": "Redundant phrase",
                    "suggestion_only": True,
                })

        return edited, changes

    def _analyze_structure(self, text: str) -> List[Dict]:
        """Analyze and suggest structural improvements."""
        suggestions = []

        paragraphs = text.split("\n\n")

        # Check paragraph length
        for i, para in enumerate(paragraphs):
            sentences = re.split(r'[.!?]', para)
            if len(sentences) > 6:
                suggestions.append({
                    "type": "structure",
                    "location": f"Paragraph {i + 1}",
                    "suggestion": "Consider breaking into smaller paragraphs",
                })

        # Check for transitions
        transition_words = ["however", "therefore", "furthermore", "moreover", "consequently", "additionally"]
        has_transitions = any(word in text.lower() for word in transition_words)

        if len(paragraphs) > 2 and not has_transitions:
            suggestions.append({
                "type": "structure",
                "suggestion": "Consider adding transition words between paragraphs",
            })

        # Check introduction/conclusion
        if len(paragraphs) > 3:
            first_para = paragraphs[0].lower()
            last_para = paragraphs[-1].lower()

            if not any(word in first_para for word in ["this", "will", "explore", "discuss", "explain"]):
                suggestions.append({
                    "type": "structure",
                    "location": "Introduction",
                    "suggestion": "Consider adding a clearer thesis or purpose statement",
                })

            if not any(word in last_para for word in ["conclusion", "summary", "in short", "overall"]):
                suggestions.append({
                    "type": "structure",
                    "location": "Conclusion",
                    "suggestion": "Consider adding a summarizing conclusion",
                })

        return suggestions

    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """Calculate readability metrics."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = text.split()
        word_count = len(words)
        sentence_count = len(sentences)

        if sentence_count == 0:
            return {"error": "No complete sentences found"}

        # Average sentence length
        avg_sentence_length = word_count / sentence_count

        # Syllable estimation (simple heuristic)
        def count_syllables(word):
            word = word.lower()
            if len(word) <= 3:
                return 1
            vowels = "aeiouy"
            count = 0
            prev_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_vowel:
                    count += 1
                prev_vowel = is_vowel
            if word.endswith("e"):
                count -= 1
            return max(1, count)

        syllable_count = sum(count_syllables(word) for word in words)
        avg_syllables = syllable_count / word_count if word_count > 0 else 0

        # Flesch Reading Ease (simplified)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        flesch_score = max(0, min(100, flesch_score))

        # Grade level mapping
        if flesch_score >= 90:
            grade_level = "5th grade"
            difficulty = "Very Easy"
        elif flesch_score >= 70:
            grade_level = "8th grade"
            difficulty = "Easy"
        elif flesch_score >= 50:
            grade_level = "10th-12th grade"
            difficulty = "Moderate"
        elif flesch_score >= 30:
            grade_level = "College"
            difficulty = "Difficult"
        else:
            grade_level = "Graduate"
            difficulty = "Very Difficult"

        return {
            "flesch_score": round(flesch_score, 1),
            "difficulty": difficulty,
            "grade_level": grade_level,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "word_count": word_count,
            "sentence_count": sentence_count,
        }

    def _summarize_improvements(self, changes: List[Dict]) -> str:
        """Summarize the improvements made."""
        if not changes:
            return "No changes needed - text looks good!"

        by_type = {}
        for change in changes:
            t = change.get("type", "other")
            by_type[t] = by_type.get(t, 0) + 1

        parts = [f"{count} {type_name}" for type_name, count in by_type.items()]
        return f"Made {len(changes)} improvements: {', '.join(parts)}"

    def _get_suggestions(self, changes: List[Dict]) -> List[str]:
        """Get follow-up suggestions."""
        suggestions = []

        change_types = set(c.get("type") for c in changes)

        if "grammar" in change_types:
            suggestions.append("Review grammar changes for context appropriateness")

        if "style" in change_types:
            suggestions.append("Style suggestions are contextual - apply judgment")

        if len(changes) > 10:
            suggestions.append("Many changes suggested - consider reviewing in sections")

        return suggestions

    def get_prompt(self) -> str:
        return """You are a professional editor.

When editing text:
1. Preserve the author's voice and intent
2. Fix errors without over-editing
3. Improve clarity while maintaining meaning
4. Follow style guide if provided
5. Explain changes to help authors learn

Priority order:
1. Factual accuracy
2. Grammar and spelling
3. Clarity and flow
4. Style and tone
5. Conciseness
"""
