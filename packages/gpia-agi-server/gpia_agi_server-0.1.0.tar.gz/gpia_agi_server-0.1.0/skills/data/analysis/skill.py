"""
Data Analysis Skill
===================

Exploratory data analysis, statistical summaries, pattern detection,
and insight generation from structured data.
"""

import statistics
import time
from collections import Counter
from typing import Any, Dict, List, Optional, Union

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class DataAnalysisSkill(Skill):
    """
    Data analysis skill providing:
    - Descriptive statistics
    - Correlation analysis
    - Distribution analysis
    - Outlier detection
    - Pattern identification
    """

    TASK_TYPES = ["describe", "correlate", "distribution", "outliers", "patterns"]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="data/analysis",
            name="Data Analysis",
            description="Exploratory data analysis, statistical summaries, pattern detection, and insight generation.",
            version="0.1.0",
            category=SkillCategory.DATA,
            level=SkillLevel.INTERMEDIATE,
            tags=["data-analysis", "statistics", "exploration", "insights"],
            requires_tools=["pandas", "numpy"],
            estimated_tokens=700,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "enum": self.TASK_TYPES,
                    "description": "Type of analysis to perform",
                },
                "data": {
                    "type": "object",
                    "description": "Data to analyze",
                    "properties": {
                        "columns": {"type": "array", "items": {"type": "string"}},
                        "values": {"type": "array"},
                        "sample": {"type": "array"},
                    },
                },
                "columns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific columns to analyze",
                },
                "options": {
                    "type": "object",
                    "description": "Analysis options",
                },
            },
            "required": ["task", "data"],
        }

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        start_time = time.time()

        task = input_data.get("task", "describe")
        data = input_data.get("data", {})
        columns = input_data.get("columns")
        options = input_data.get("options", {})

        # Parse data
        parsed = self._parse_data(data)
        if not parsed:
            return SkillResult(
                success=False,
                output=None,
                error="Could not parse data format",
                error_code="PARSE_ERROR",
                skill_id=self.metadata().id,
            )

        try:
            if task == "describe":
                result = self._describe(parsed, columns)
            elif task == "correlate":
                result = self._correlate(parsed, columns)
            elif task == "distribution":
                result = self._distribution(parsed, columns, options)
            elif task == "outliers":
                result = self._detect_outliers(parsed, columns, options)
            elif task == "patterns":
                result = self._find_patterns(parsed, columns)
            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error=f"Unknown task: {task}",
                    error_code="INVALID_TASK",
                    skill_id=self.metadata().id,
                )

            execution_time = int((time.time() - start_time) * 1000)

            return SkillResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                skill_id=self.metadata().id,
                suggestions=self._get_suggestions(task, result),
                related_skills=["data/transform", "data/query"],
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="ANALYSIS_ERROR",
                skill_id=self.metadata().id,
            )

    def _parse_data(self, data: Dict) -> Optional[Dict[str, List]]:
        """Parse various data formats into column dict."""
        columns = data.get("columns", [])
        values = data.get("values") or data.get("sample") or data.get("rows", [])

        if not columns or not values:
            return None

        # Convert to column-oriented dict
        result = {col: [] for col in columns}

        for row in values:
            if isinstance(row, (list, tuple)):
                for i, val in enumerate(row):
                    if i < len(columns):
                        result[columns[i]].append(val)
            elif isinstance(row, dict):
                for col in columns:
                    result[col].append(row.get(col))

        return result

    def _describe(
        self,
        data: Dict[str, List],
        columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate descriptive statistics."""
        cols = columns or list(data.keys())
        summary = {
            "row_count": len(next(iter(data.values()), [])),
            "column_count": len(cols),
            "columns": {},
        }
        insights = []

        for col in cols:
            if col not in data:
                continue

            values = [v for v in data[col] if v is not None]

            if not values:
                summary["columns"][col] = {"all_null": True}
                continue

            # Determine type
            if all(isinstance(v, (int, float)) for v in values):
                summary["columns"][col] = self._numeric_stats(values)
            else:
                summary["columns"][col] = self._categorical_stats(values)

        # Generate insights
        insights.extend(self._generate_insights(summary, data))

        return {
            "summary": summary,
            "insights": insights,
        }

    def _numeric_stats(self, values: List[Union[int, float]]) -> Dict[str, Any]:
        """Calculate statistics for numeric data."""
        clean = [float(v) for v in values if v is not None]

        if not clean:
            return {"type": "numeric", "count": 0}

        stats = {
            "type": "numeric",
            "count": len(clean),
            "min": min(clean),
            "max": max(clean),
            "mean": round(statistics.mean(clean), 2),
            "median": round(statistics.median(clean), 2),
        }

        if len(clean) > 1:
            stats["std"] = round(statistics.stdev(clean), 2)
            stats["variance"] = round(statistics.variance(clean), 2)

        # Quartiles
        sorted_vals = sorted(clean)
        n = len(sorted_vals)
        stats["q1"] = sorted_vals[n // 4]
        stats["q3"] = sorted_vals[(3 * n) // 4]
        stats["iqr"] = stats["q3"] - stats["q1"]

        return stats

    def _categorical_stats(self, values: List) -> Dict[str, Any]:
        """Calculate statistics for categorical data."""
        counter = Counter(values)
        total = len(values)

        top_values = counter.most_common(5)

        return {
            "type": "categorical",
            "count": total,
            "unique": len(counter),
            "top_values": [
                {"value": v, "count": c, "percentage": round(c / total * 100, 1)}
                for v, c in top_values
            ],
            "mode": top_values[0][0] if top_values else None,
        }

    def _correlate(
        self,
        data: Dict[str, List],
        columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Calculate correlations between numeric columns."""
        # Get numeric columns
        numeric_cols = []
        for col, values in data.items():
            if columns and col not in columns:
                continue
            if values and all(isinstance(v, (int, float)) for v in values if v is not None):
                numeric_cols.append(col)

        if len(numeric_cols) < 2:
            return {
                "error": "Need at least 2 numeric columns for correlation",
                "numeric_columns_found": numeric_cols,
            }

        correlations = {}
        interpretations = []

        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i + 1:]:
                r = self._pearson_correlation(data[col1], data[col2])
                key = f"{col1}__{col2}"
                correlations[key] = round(r, 3)

                # Interpret
                if abs(r) > 0.8:
                    strength = "strong"
                elif abs(r) > 0.5:
                    strength = "moderate"
                elif abs(r) > 0.3:
                    strength = "weak"
                else:
                    strength = "negligible"

                direction = "positive" if r > 0 else "negative"

                if abs(r) > 0.3:
                    interpretations.append(
                        f"{col1} and {col2}: {strength} {direction} correlation (r={r:.2f})"
                    )

        return {
            "correlations": correlations,
            "interpretations": interpretations,
        }

    def _pearson_correlation(self, x: List, y: List) -> float:
        """Calculate Pearson correlation coefficient."""
        # Clean paired data
        pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
        if len(pairs) < 2:
            return 0.0

        x_clean, y_clean = zip(*pairs)

        n = len(x_clean)
        sum_x = sum(x_clean)
        sum_y = sum(y_clean)
        sum_xy = sum(a * b for a, b in pairs)
        sum_x2 = sum(a * a for a in x_clean)
        sum_y2 = sum(b * b for b in y_clean)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)) ** 0.5

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _distribution(
        self,
        data: Dict[str, List],
        columns: Optional[List[str]] = None,
        options: Dict = None,
    ) -> Dict[str, Any]:
        """Analyze data distributions."""
        options = options or {}
        bins = options.get("bins", 10)
        cols = columns or list(data.keys())

        distributions = {}

        for col in cols:
            if col not in data:
                continue

            values = [v for v in data[col] if v is not None]

            if not values:
                continue

            if all(isinstance(v, (int, float)) for v in values):
                distributions[col] = self._numeric_distribution(values, bins)
            else:
                distributions[col] = self._categorical_distribution(values)

        return {"distributions": distributions}

    def _numeric_distribution(self, values: List, bins: int) -> Dict:
        """Analyze numeric distribution."""
        min_val, max_val = min(values), max(values)
        bin_width = (max_val - min_val) / bins if max_val != min_val else 1

        histogram = [0] * bins
        for v in values:
            idx = min(int((v - min_val) / bin_width), bins - 1)
            histogram[idx] += 1

        # Detect skewness
        mean = statistics.mean(values)
        median = statistics.median(values)
        skew_direction = "right" if mean > median else "left" if mean < median else "symmetric"

        return {
            "type": "numeric",
            "histogram": histogram,
            "bin_edges": [min_val + i * bin_width for i in range(bins + 1)],
            "skewness": skew_direction,
            "kurtosis_hint": "normal" if 0.8 < statistics.stdev(values) / (max_val - min_val) < 0.3 else "unknown",
        }

    def _categorical_distribution(self, values: List) -> Dict:
        """Analyze categorical distribution."""
        counter = Counter(values)
        total = len(values)

        return {
            "type": "categorical",
            "value_counts": dict(counter),
            "percentages": {k: round(v / total * 100, 1) for k, v in counter.items()},
            "entropy": self._entropy(list(counter.values())),
        }

    def _entropy(self, counts: List[int]) -> float:
        """Calculate entropy of distribution."""
        import math
        total = sum(counts)
        if total == 0:
            return 0.0
        probs = [c / total for c in counts if c > 0]
        return -sum(p * math.log2(p) for p in probs)

    def _detect_outliers(
        self,
        data: Dict[str, List],
        columns: Optional[List[str]] = None,
        options: Dict = None,
    ) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        options = options or {}
        threshold = options.get("threshold", 1.5)  # IQR multiplier
        cols = columns or list(data.keys())

        outliers = {}

        for col in cols:
            if col not in data:
                continue

            values = [v for v in data[col] if v is not None and isinstance(v, (int, float))]

            if len(values) < 4:
                continue

            sorted_vals = sorted(values)
            n = len(sorted_vals)
            q1 = sorted_vals[n // 4]
            q3 = sorted_vals[(3 * n) // 4]
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            col_outliers = []
            for i, v in enumerate(data[col]):
                if v is not None and isinstance(v, (int, float)):
                    if v < lower_bound or v > upper_bound:
                        col_outliers.append({
                            "index": i,
                            "value": v,
                            "type": "low" if v < lower_bound else "high",
                        })

            if col_outliers:
                outliers[col] = {
                    "count": len(col_outliers),
                    "percentage": round(len(col_outliers) / len(values) * 100, 1),
                    "bounds": {"lower": lower_bound, "upper": upper_bound},
                    "outliers": col_outliers[:10],  # Limit to 10
                }

        return {
            "outliers": outliers,
            "method": f"IQR with threshold {threshold}",
        }

    def _find_patterns(
        self,
        data: Dict[str, List],
        columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Find patterns in the data."""
        patterns = []
        cols = columns or list(data.keys())

        # Missing value patterns
        for col in cols:
            if col not in data:
                continue
            nulls = sum(1 for v in data[col] if v is None)
            if nulls > 0:
                patterns.append({
                    "type": "missing_values",
                    "column": col,
                    "count": nulls,
                    "percentage": round(nulls / len(data[col]) * 100, 1),
                })

        # Constant columns
        for col in cols:
            if col not in data:
                continue
            unique = len(set(v for v in data[col] if v is not None))
            if unique == 1:
                patterns.append({
                    "type": "constant_column",
                    "column": col,
                    "value": data[col][0],
                })

        # Monotonic trends
        for col in cols:
            if col not in data:
                continue
            values = [v for v in data[col] if v is not None and isinstance(v, (int, float))]
            if len(values) > 2:
                if all(a <= b for a, b in zip(values, values[1:])):
                    patterns.append({
                        "type": "monotonic_increasing",
                        "column": col,
                    })
                elif all(a >= b for a, b in zip(values, values[1:])):
                    patterns.append({
                        "type": "monotonic_decreasing",
                        "column": col,
                    })

        return {
            "patterns": patterns,
            "pattern_count": len(patterns),
        }

    def _generate_insights(
        self,
        summary: Dict,
        data: Dict[str, List],
    ) -> List[str]:
        """Generate human-readable insights."""
        insights = []

        col_stats = summary.get("columns", {})

        for col, stats in col_stats.items():
            if stats.get("type") == "numeric":
                # High variance
                if stats.get("std", 0) > stats.get("mean", 1) * 0.5:
                    insights.append(f"{col} shows high variability (std > 50% of mean)")

                # Skewed distribution
                if stats.get("mean", 0) > stats.get("median", 0) * 1.2:
                    insights.append(f"{col} may be right-skewed (mean > median)")

            elif stats.get("type") == "categorical":
                # Dominant category
                top = stats.get("top_values", [])
                if top and top[0].get("percentage", 0) > 80:
                    insights.append(
                        f"{col} is dominated by '{top[0]['value']}' ({top[0]['percentage']}%)"
                    )

        return insights[:5]  # Limit insights

    def _get_suggestions(self, task: str, result: Dict) -> List[str]:
        """Get follow-up suggestions."""
        suggestions = []

        if task == "describe":
            suggestions.append("Run 'correlate' to find relationships between columns")
            suggestions.append("Use 'outliers' to identify anomalies")

        elif task == "correlate":
            if result.get("correlations"):
                suggestions.append("Investigate strong correlations for causality")

        elif task == "outliers":
            if result.get("outliers"):
                suggestions.append("Review outliers before removing - they may be valid")

        return suggestions

    def get_prompt(self) -> str:
        return """You are a data analysis expert.

When analyzing data:
1. Start with descriptive statistics to understand distributions
2. Look for patterns, trends, and anomalies
3. Consider data quality issues (missing values, outliers)
4. Provide actionable insights, not just numbers
5. Recommend follow-up analyses when appropriate

Be precise with statistical terminology and explain findings clearly.
"""
