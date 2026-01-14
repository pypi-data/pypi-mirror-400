"""
Content Drafting Skill
======================

Generate well-structured content drafts including articles, documentation,
emails, and creative writing with customizable tone and format.
"""

import time
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class DraftSkill(Skill):
    """
    Content drafting skill providing:
    - Article and blog post generation
    - Email drafting
    - Documentation writing
    - Creative content generation
    - Template-based content
    """

    CONTENT_TYPES = [
        "article",
        "email",
        "documentation",
        "summary",
        "proposal",
        "report",
        "creative",
    ]

    TONES = [
        "professional",
        "casual",
        "educational",
        "persuasive",
        "technical",
        "friendly",
        "formal",
    ]

    LENGTHS = {
        "short": (100, 300),
        "medium": (300, 800),
        "long": (800, 2000),
        "very_long": (2000, 5000),
    }

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="writing/draft",
            name="Content Drafting",
            description="Generate well-structured content drafts with customizable tone and format.",
            version="0.1.0",
            category=SkillCategory.WRITING,
            level=SkillLevel.BASIC,
            tags=["writing", "drafting", "content-generation", "documentation"],
            estimated_tokens=600,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content_type": {
                    "type": "string",
                    "enum": self.CONTENT_TYPES,
                    "description": "Type of content to generate",
                },
                "topic": {
                    "type": "string",
                    "description": "Main topic or subject",
                },
                "purpose": {
                    "type": "string",
                    "description": "Purpose of the content",
                },
                "audience": {
                    "type": "string",
                    "description": "Target audience",
                },
                "tone": {
                    "type": "string",
                    "enum": self.TONES,
                    "default": "professional",
                },
                "length": {
                    "type": "string",
                    "enum": list(self.LENGTHS.keys()),
                    "default": "medium",
                },
                "outline": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional outline or key points",
                },
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key points to include",
                },
                "context": {
                    "type": "string",
                    "description": "Additional context",
                },
                "template": {
                    "type": "string",
                    "description": "Template name to use",
                },
            },
            "required": ["content_type"],
        }

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        start_time = time.time()

        content_type = input_data.get("content_type", "article")
        topic = input_data.get("topic", "")
        purpose = input_data.get("purpose", "")
        audience = input_data.get("audience", "general")
        tone = input_data.get("tone", "professional")
        length = input_data.get("length", "medium")
        outline = input_data.get("outline", [])
        key_points = input_data.get("key_points", [])
        additional_context = input_data.get("context", "")

        try:
            # Generate draft based on content type
            if content_type == "article":
                result = self._draft_article(
                    topic, audience, tone, length, outline, key_points
                )
            elif content_type == "email":
                result = self._draft_email(
                    purpose, tone, key_points, additional_context
                )
            elif content_type == "documentation":
                result = self._draft_documentation(
                    topic, audience, outline, key_points
                )
            elif content_type == "summary":
                result = self._draft_summary(
                    additional_context, length, key_points
                )
            elif content_type == "proposal":
                result = self._draft_proposal(
                    topic, purpose, audience, key_points
                )
            elif content_type == "report":
                result = self._draft_report(
                    topic, purpose, outline, key_points
                )
            elif content_type == "creative":
                result = self._draft_creative(
                    topic, tone, length, additional_context
                )
            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error=f"Unknown content type: {content_type}",
                    error_code="INVALID_TYPE",
                    skill_id=self.metadata().id,
                )

            execution_time = int((time.time() - start_time) * 1000)

            return SkillResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                skill_id=self.metadata().id,
                suggestions=self._get_suggestions(content_type),
                related_skills=["writing/edit", "writing/docs"],
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="DRAFT_ERROR",
                skill_id=self.metadata().id,
            )

    def _draft_article(
        self,
        topic: str,
        audience: str,
        tone: str,
        length: str,
        outline: List[str],
        key_points: List[str],
    ) -> Dict[str, Any]:
        """Generate article structure and guidance."""
        word_range = self.LENGTHS.get(length, (300, 800))

        structure = {
            "title": self._generate_title(topic, tone),
            "meta_description": f"Learn about {topic} - a comprehensive guide for {audience}.",
            "structure": {
                "introduction": {
                    "purpose": "Hook the reader and introduce the topic",
                    "suggested_length": "1-2 paragraphs",
                    "elements": ["hook", "context", "thesis"],
                },
                "body": self._generate_body_structure(outline, key_points),
                "conclusion": {
                    "purpose": "Summarize and provide call-to-action",
                    "suggested_length": "1-2 paragraphs",
                    "elements": ["summary", "takeaways", "cta"],
                },
            },
            "guidelines": self._get_tone_guidelines(tone),
            "target_word_count": f"{word_range[0]}-{word_range[1]}",
            "reading_time": f"{word_range[1] // 200}-{word_range[1] // 150} min",
        }

        return {"draft": structure, "content_type": "article"}

    def _draft_email(
        self,
        purpose: str,
        tone: str,
        key_points: List[str],
        context: str,
    ) -> Dict[str, Any]:
        """Generate email structure."""
        templates = {
            "follow_up": {
                "subject_template": "Following Up on {topic}",
                "opening": "Thank you for {context}. I wanted to follow up on...",
                "structure": ["gratitude", "recap", "next_steps", "closing"],
            },
            "introduction": {
                "subject_template": "Introduction: {topic}",
                "opening": "I hope this email finds you well. My name is...",
                "structure": ["intro", "purpose", "value_prop", "cta"],
            },
            "request": {
                "subject_template": "Request: {topic}",
                "opening": "I'm reaching out to request...",
                "structure": ["context", "request", "justification", "timeline"],
            },
            "update": {
                "subject_template": "Update: {topic}",
                "opening": "I wanted to provide you with an update on...",
                "structure": ["summary", "details", "next_steps", "questions"],
            },
        }

        template = templates.get(purpose, templates["follow_up"])

        structure = {
            "subject_suggestion": template["subject_template"],
            "structure": {
                "greeting": self._get_greeting(tone),
                "opening": template["opening"],
                "body_sections": template["structure"],
                "key_points_to_include": key_points,
                "closing": self._get_closing(tone),
                "signature": "[Your name]",
            },
            "guidelines": self._get_tone_guidelines(tone),
            "tips": [
                "Keep subject line under 50 characters",
                "Front-load important information",
                "Use short paragraphs (2-3 sentences)",
                "Include clear call-to-action",
            ],
        }

        return {"draft": structure, "content_type": "email"}

    def _draft_documentation(
        self,
        topic: str,
        audience: str,
        outline: List[str],
        key_points: List[str],
    ) -> Dict[str, Any]:
        """Generate technical documentation structure."""
        sections = []

        # Standard doc sections
        if not outline:
            outline = ["Overview", "Getting Started", "Usage", "API Reference", "Examples", "Troubleshooting"]

        for section in outline:
            sections.append({
                "heading": section,
                "subsections": self._suggest_subsections(section),
                "content_hints": self._get_doc_hints(section),
            })

        structure = {
            "title": f"{topic} Documentation",
            "overview": {
                "description": f"Documentation for {topic}",
                "audience": audience,
                "prerequisites": [],
            },
            "sections": sections,
            "key_concepts": key_points,
            "formatting_guidelines": {
                "use_markdown": True,
                "code_blocks": "Use fenced code blocks with language hints",
                "links": "Use relative links for internal references",
                "images": "Include alt text for accessibility",
            },
        }

        return {"draft": structure, "content_type": "documentation"}

    def _draft_summary(
        self,
        content: str,
        length: str,
        key_points: List[str],
    ) -> Dict[str, Any]:
        """Generate summary structure."""
        word_range = self.LENGTHS.get(length, (100, 300))

        structure = {
            "format": "summary",
            "guidelines": {
                "target_length": f"{word_range[0]}-{word_range[1]} words",
                "structure": [
                    "Main thesis/finding",
                    "Key supporting points",
                    "Implications/conclusions",
                ],
                "style": [
                    "Use active voice",
                    "Avoid jargon unless necessary",
                    "Be specific, not vague",
                ],
            },
            "key_points_to_capture": key_points,
            "original_content_provided": bool(content),
        }

        return {"draft": structure, "content_type": "summary"}

    def _draft_proposal(
        self,
        topic: str,
        purpose: str,
        audience: str,
        key_points: List[str],
    ) -> Dict[str, Any]:
        """Generate proposal structure."""
        structure = {
            "title": f"Proposal: {topic}",
            "sections": [
                {
                    "heading": "Executive Summary",
                    "content_hints": "Brief overview of the proposal and key benefits",
                    "length": "1 paragraph",
                },
                {
                    "heading": "Problem Statement",
                    "content_hints": "Define the problem or opportunity being addressed",
                    "length": "1-2 paragraphs",
                },
                {
                    "heading": "Proposed Solution",
                    "content_hints": "Detailed description of the proposed approach",
                    "length": "2-3 paragraphs",
                },
                {
                    "heading": "Benefits",
                    "content_hints": "List of expected benefits and outcomes",
                    "length": "Bullet points",
                },
                {
                    "heading": "Timeline",
                    "content_hints": "Project phases and milestones",
                    "length": "Table or list",
                },
                {
                    "heading": "Budget/Resources",
                    "content_hints": "Cost breakdown and resource requirements",
                    "length": "Table",
                },
                {
                    "heading": "Next Steps",
                    "content_hints": "Immediate actions and decision points",
                    "length": "Numbered list",
                },
            ],
            "key_points_to_address": key_points,
            "audience_considerations": f"Tailored for {audience}",
        }

        return {"draft": structure, "content_type": "proposal"}

    def _draft_report(
        self,
        topic: str,
        purpose: str,
        outline: List[str],
        key_points: List[str],
    ) -> Dict[str, Any]:
        """Generate report structure."""
        sections = outline or [
            "Executive Summary",
            "Introduction",
            "Methodology",
            "Findings",
            "Analysis",
            "Recommendations",
            "Conclusion",
        ]

        structure = {
            "title": f"Report: {topic}",
            "purpose": purpose,
            "sections": [
                {"heading": s, "content_hints": self._get_report_hints(s)}
                for s in sections
            ],
            "key_findings_to_include": key_points,
            "formatting": {
                "use_headings": True,
                "include_toc": True,
                "page_numbers": True,
                "appendices": "For detailed data",
            },
        }

        return {"draft": structure, "content_type": "report"}

    def _draft_creative(
        self,
        topic: str,
        tone: str,
        length: str,
        context: str,
    ) -> Dict[str, Any]:
        """Generate creative writing guidance."""
        word_range = self.LENGTHS.get(length, (300, 800))

        structure = {
            "topic": topic,
            "tone": tone,
            "guidelines": {
                "target_length": f"{word_range[0]}-{word_range[1]} words",
                "elements": [
                    "Engaging opening hook",
                    "Vivid descriptions",
                    "Strong voice",
                    "Satisfying conclusion",
                ],
                "techniques": [
                    "Show, don't tell",
                    "Use sensory details",
                    "Vary sentence structure",
                    "Create rhythm with word choice",
                ],
            },
            "context": context,
            "prompts": [
                f"What makes {topic} unique or interesting?",
                f"What emotion should the reader feel?",
                f"What's the central message or theme?",
            ],
        }

        return {"draft": structure, "content_type": "creative"}

    # Helper methods

    def _generate_title(self, topic: str, tone: str) -> str:
        """Generate title suggestions."""
        templates = {
            "educational": f"Understanding {topic}: A Complete Guide",
            "professional": f"{topic}: Best Practices and Insights",
            "casual": f"Everything You Need to Know About {topic}",
            "persuasive": f"Why {topic} Matters More Than Ever",
            "technical": f"{topic}: Technical Deep Dive",
        }
        return templates.get(tone, f"Guide to {topic}")

    def _generate_body_structure(
        self,
        outline: List[str],
        key_points: List[str],
    ) -> List[Dict]:
        """Generate body section structure."""
        if outline:
            return [
                {
                    "heading": section,
                    "purpose": f"Cover {section.lower()}",
                    "suggested_length": "2-3 paragraphs",
                }
                for section in outline
            ]

        # Default structure
        return [
            {"heading": "Background", "purpose": "Provide context"},
            {"heading": "Main Discussion", "purpose": "Core content"},
            {"heading": "Key Takeaways", "purpose": "Summarize insights"},
        ]

    def _get_tone_guidelines(self, tone: str) -> List[str]:
        """Get writing guidelines for a specific tone."""
        guidelines = {
            "professional": [
                "Use formal language",
                "Avoid contractions",
                "Be concise and direct",
                "Support claims with evidence",
            ],
            "casual": [
                "Use conversational language",
                "Contractions are fine",
                "Address reader directly",
                "Include relatable examples",
            ],
            "educational": [
                "Define technical terms",
                "Use examples liberally",
                "Build from simple to complex",
                "Include practical applications",
            ],
            "persuasive": [
                "Lead with benefits",
                "Address objections",
                "Use social proof",
                "Include clear call-to-action",
            ],
            "technical": [
                "Be precise and accurate",
                "Use appropriate terminology",
                "Include code examples where relevant",
                "Document assumptions",
            ],
        }
        return guidelines.get(tone, guidelines["professional"])

    def _get_greeting(self, tone: str) -> str:
        """Get appropriate greeting for tone."""
        greetings = {
            "formal": "Dear [Name],",
            "professional": "Hello [Name],",
            "casual": "Hi [Name],",
            "friendly": "Hey [Name]!",
        }
        return greetings.get(tone, "Hello,")

    def _get_closing(self, tone: str) -> str:
        """Get appropriate closing for tone."""
        closings = {
            "formal": "Sincerely,",
            "professional": "Best regards,",
            "casual": "Thanks,",
            "friendly": "Cheers,",
        }
        return closings.get(tone, "Best,")

    def _suggest_subsections(self, section: str) -> List[str]:
        """Suggest subsections for documentation."""
        suggestions = {
            "Overview": ["Introduction", "Key Features", "Use Cases"],
            "Getting Started": ["Prerequisites", "Installation", "Quick Start"],
            "Usage": ["Basic Usage", "Advanced Options", "Configuration"],
            "API Reference": ["Methods", "Parameters", "Return Values"],
            "Examples": ["Basic Example", "Advanced Example", "Real-world Use Case"],
            "Troubleshooting": ["Common Issues", "FAQ", "Getting Help"],
        }
        return suggestions.get(section, [])

    def _get_doc_hints(self, section: str) -> str:
        """Get content hints for documentation sections."""
        hints = {
            "Overview": "Explain what this is and why it matters",
            "Getting Started": "Help users get up and running quickly",
            "Usage": "Show how to use the main features",
            "API Reference": "Document all public interfaces",
            "Examples": "Provide practical, runnable examples",
            "Troubleshooting": "Address common problems and solutions",
        }
        return hints.get(section, "Provide relevant content")

    def _get_report_hints(self, section: str) -> str:
        """Get content hints for report sections."""
        hints = {
            "Executive Summary": "1-page overview for decision makers",
            "Introduction": "Context, objectives, and scope",
            "Methodology": "How the work was conducted",
            "Findings": "Present the data and results",
            "Analysis": "Interpret what the findings mean",
            "Recommendations": "Actionable next steps",
            "Conclusion": "Summary and final thoughts",
        }
        return hints.get(section, "")

    def _get_suggestions(self, content_type: str) -> List[str]:
        """Get follow-up suggestions."""
        return [
            f"Use 'writing/edit' to refine the {content_type}",
            "Review for consistency with brand voice",
        ]

    def get_prompt(self) -> str:
        return """You are a professional content writer.

When drafting content:
1. Understand the audience and purpose
2. Create a clear structure before writing
3. Use appropriate tone and style
4. Include compelling hooks and transitions
5. End with clear calls-to-action when appropriate

For different content types:
- Articles: Educate and engage
- Emails: Be concise and action-oriented
- Documentation: Be clear and comprehensive
- Proposals: Be persuasive and well-organized
"""
