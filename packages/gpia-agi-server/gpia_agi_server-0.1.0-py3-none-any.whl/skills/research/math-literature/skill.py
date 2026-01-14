"""
Mathematical Literature Research Skill
=======================================

ArXiv paper search and theorem extraction for Riemann Hypothesis research.
Provides paper discovery, details extraction, and recent results tracking.
"""

from typing import Any, Dict, List
import arxiv
from datetime import datetime, timedelta

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class MathLiteratureSkill(Skill):
    """Mathematical literature research via arXiv."""

    _cached_metadata: SkillMetadata = None

    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        if MathLiteratureSkill._cached_metadata is None:
            MathLiteratureSkill._cached_metadata = SkillMetadata(
                id="research/math-literature",
                name="Mathematical Literature Research",
                description="ArXiv paper search for RH research",
                category=SkillCategory.RESEARCH,
                level=SkillLevel.INTERMEDIATE,
                tags=["mathematics", "literature", "arxiv", "riemann"],
            )
        return MathLiteratureSkill._cached_metadata

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Route to capability-specific methods."""
        capability = input_data.get("capability", "search_arxiv")

        handler = getattr(self, f"capability_{capability}", None)
        if handler is None:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                error_code="UNKNOWN_CAPABILITY",
                skill_id=self.metadata().id,
            )

        try:
            return handler(input_data, context)
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXECUTION_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_search_arxiv(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Search arXiv for papers matching query."""
        try:
            query = input_data.get("query", "Riemann Hypothesis")
            max_results = int(input_data.get("max_results", 5))
            sort_order = input_data.get("sort_order", "SubmittedDate")

            # Create arXiv client
            client = arxiv.Client()

            # Build search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=getattr(arxiv.SortCriterion, sort_order, arxiv.SortCriterion.Relevance),
            )

            papers = []
            for result in client.results(search):
                papers.append(
                    {
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "published": result.published.isoformat(),
                        "summary": result.summary[:500],  # Truncate
                        "pdf_url": result.pdf_url,
                        "arxiv_id": result.arxiv_id,
                    }
                )

            return SkillResult(
                success=True,
                output={
                    "query": query,
                    "papers_found": len(papers),
                    "papers": papers,
                    "description": f"Found {len(papers)} papers on '{query}'",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="SEARCH_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_search_riemann_hypothesis(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Search specifically for Riemann Hypothesis papers."""
        try:
            max_results = int(input_data.get("max_results", 10))
            days_back = int(input_data.get("days_back", 365))

            client = arxiv.Client()

            # Search for RH papers from last N days
            date_threshold = datetime.now() - timedelta(days=days_back)
            date_str = date_threshold.strftime("%Y%m%d0000")

            query = f'cat:math.NT AND (ti:"Riemann Hypothesis" OR ab:"Riemann Hypothesis")'

            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            papers = []
            for result in client.results(search):
                papers.append(
                    {
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "published": result.published.isoformat(),
                        "abstract": result.summary,
                        "pdf_url": result.pdf_url,
                        "arxiv_id": result.arxiv_id,
                        "category": result.primary_category,
                    }
                )

            return SkillResult(
                success=True,
                output={
                    "papers_found": len(papers),
                    "search_period_days": days_back,
                    "papers": papers,
                    "description": f"Found {len(papers)} RH papers in last {days_back} days",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="RH_SEARCH_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_get_paper_details(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Get full details of specific paper."""
        try:
            arxiv_id = input_data.get("arxiv_id", "")

            if not arxiv_id:
                return SkillResult(
                    success=False,
                    output=None,
                    error="arxiv_id required",
                    error_code="MISSING_ID",
                    skill_id=self.metadata().id,
                )

            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])

            for result in client.results(search):
                return SkillResult(
                    success=True,
                    output={
                        "arxiv_id": result.arxiv_id,
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "published": result.published.isoformat(),
                        "updated": result.updated.isoformat() if result.updated else None,
                        "summary": result.summary,
                        "pdf_url": result.pdf_url,
                        "categories": result.categories,
                        "primary_category": result.primary_category,
                    },
                    skill_id=self.metadata().id,
                )

            return SkillResult(
                success=False,
                output=None,
                error=f"Paper {arxiv_id} not found",
                error_code="NOT_FOUND",
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="DETAIL_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_extract_recent_results(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Extract recent results on RH sub-problems."""
        try:
            topics = [
                "zero-free regions",
                "explicit formula",
                "computational verification",
                "alternative hypotheses",
                "generalized Riemann",
            ]

            client = arxiv.Client()
            results_by_topic = {}

            for topic in topics:
                query = f'cat:math.NT AND (ab:"{topic}" OR ti:"{topic}") AND submittedDate:[202301010000 TO 202501010000]'

                search = arxiv.Search(query=query, max_results=3)

                papers = []
                for result in client.results(search):
                    papers.append(
                        {
                            "title": result.title,
                            "published": result.published.isoformat(),
                            "arxiv_id": result.arxiv_id,
                            "snippet": result.summary[:200],
                        }
                    )

                if papers:
                    results_by_topic[topic] = papers

            return SkillResult(
                success=True,
                output={
                    "topics_searched": topics,
                    "results_by_topic": results_by_topic,
                    "description": "Recent results on RH sub-problems",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXTRACT_ERROR",
                skill_id=self.metadata().id,
            )
