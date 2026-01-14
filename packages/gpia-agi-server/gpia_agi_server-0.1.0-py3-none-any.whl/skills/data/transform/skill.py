"""
Data Transformation Skill
=========================

Data cleaning, reshaping, and transformation operations including
filtering, mapping, aggregation, and format conversion.
"""

import re
import statistics
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Union

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillDependency,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class DataTransformSkill(Skill):
    """
    Data transformation skill providing:
    - Data cleaning (trim, fill, normalize)
    - Filtering and selection
    - Aggregation and grouping
    - Reshaping (pivot, melt)
    - Type conversion
    """

    OPERATIONS = ["clean", "filter", "aggregate", "reshape", "convert", "derive"]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="data/transform",
            name="Data Transformation",
            description="Data cleaning, reshaping, and transformation operations.",
            version="0.1.0",
            category=SkillCategory.DATA,
            level=SkillLevel.INTERMEDIATE,
            tags=["data-transformation", "cleaning", "etl", "reshaping"],
            dependencies=[
                SkillDependency(
                    skill_id="data/analysis",
                    optional=True,
                    reason="Pre-transformation analysis",
                )
            ],
            estimated_tokens=600,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": self.OPERATIONS,
                    "description": "Type of transformation to perform",
                },
                "data": {
                    "type": "object",
                    "description": "Data to transform",
                },
                "rules": {
                    "type": "array",
                    "description": "Transformation rules (for clean operation)",
                },
                "condition": {
                    "type": "object",
                    "description": "Filter condition (for filter operation)",
                },
                "group_by": {
                    "type": "string",
                    "description": "Column to group by (for aggregate)",
                },
                "aggregations": {
                    "type": "object",
                    "description": "Aggregation functions per column",
                },
            },
            "required": ["operation", "data"],
        }

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        start_time = time.time()

        operation = input_data.get("operation", "clean")
        data = input_data.get("data", {})

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
            if operation == "clean":
                rules = input_data.get("rules", [])
                result = self._clean(parsed, rules)

            elif operation == "filter":
                condition = input_data.get("condition", {})
                result = self._filter(parsed, condition)

            elif operation == "aggregate":
                group_by = input_data.get("group_by")
                aggregations = input_data.get("aggregations", {})
                result = self._aggregate(parsed, group_by, aggregations)

            elif operation == "reshape":
                reshape_type = input_data.get("reshape_type", "pivot")
                options = input_data.get("options", {})
                result = self._reshape(parsed, reshape_type, options)

            elif operation == "convert":
                conversions = input_data.get("conversions", {})
                result = self._convert(parsed, conversions)

            elif operation == "derive":
                expressions = input_data.get("expressions", [])
                result = self._derive(parsed, expressions)

            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error=f"Unknown operation: {operation}",
                    error_code="INVALID_OPERATION",
                    skill_id=self.metadata().id,
                )

            execution_time = int((time.time() - start_time) * 1000)

            return SkillResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                skill_id=self.metadata().id,
                suggestions=self._get_suggestions(operation, result),
                related_skills=["data/analysis", "data/query"],
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="TRANSFORM_ERROR",
                skill_id=self.metadata().id,
            )

    def _parse_data(self, data: Dict) -> Optional[Dict[str, List]]:
        """Parse data into column-oriented format."""
        columns = data.get("columns", [])
        values = data.get("values") or data.get("rows", [])

        if not columns or not values:
            return None

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

    def _to_rows(self, data: Dict[str, List]) -> Dict[str, Any]:
        """Convert column-oriented data back to row format."""
        columns = list(data.keys())
        n_rows = len(next(iter(data.values()), []))

        values = []
        for i in range(n_rows):
            row = [data[col][i] for col in columns]
            values.append(row)

        return {"columns": columns, "values": values}

    def _clean(self, data: Dict[str, List], rules: List[Dict]) -> Dict[str, Any]:
        """Apply cleaning rules to data."""
        result = {col: list(vals) for col, vals in data.items()}
        changes = 0

        for rule in rules:
            col = rule.get("column")
            action = rule.get("action")

            if col not in result:
                continue

            values = result[col]

            if action == "trim":
                for i, v in enumerate(values):
                    if isinstance(v, str):
                        new_val = v.strip()
                        if new_val != v:
                            values[i] = new_val
                            changes += 1

            elif action == "lowercase":
                for i, v in enumerate(values):
                    if isinstance(v, str):
                        new_val = v.lower()
                        if new_val != v:
                            values[i] = new_val
                            changes += 1

            elif action == "uppercase":
                for i, v in enumerate(values):
                    if isinstance(v, str):
                        new_val = v.upper()
                        if new_val != v:
                            values[i] = new_val
                            changes += 1

            elif action == "fill_null":
                fill_value = rule.get("value", "")
                for i, v in enumerate(values):
                    if v is None:
                        values[i] = fill_value
                        changes += 1

            elif action == "replace":
                pattern = rule.get("pattern", "")
                replacement = rule.get("replacement", "")
                for i, v in enumerate(values):
                    if isinstance(v, str) and pattern in v:
                        values[i] = v.replace(pattern, replacement)
                        changes += 1

            elif action == "regex_replace":
                pattern = rule.get("pattern", "")
                replacement = rule.get("replacement", "")
                for i, v in enumerate(values):
                    if isinstance(v, str):
                        new_val = re.sub(pattern, replacement, v)
                        if new_val != v:
                            values[i] = new_val
                            changes += 1

            elif action == "round":
                decimals = rule.get("decimals", 2)
                for i, v in enumerate(values):
                    if isinstance(v, float):
                        values[i] = round(v, decimals)
                        changes += 1

        output = self._to_rows(result)
        output["changes_applied"] = changes

        return output

    def _filter(self, data: Dict[str, List], condition: Dict) -> Dict[str, Any]:
        """Filter rows based on condition."""
        column = condition.get("column")
        operator = condition.get("operator", "eq")
        value = condition.get("value")

        if column not in data:
            return {"error": f"Column not found: {column}"}

        # Build mask
        mask = []
        col_values = data[column]

        ops = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a is not None and a > b,
            "gte": lambda a, b: a is not None and a >= b,
            "lt": lambda a, b: a is not None and a < b,
            "lte": lambda a, b: a is not None and a <= b,
            "contains": lambda a, b: isinstance(a, str) and b in a,
            "startswith": lambda a, b: isinstance(a, str) and a.startswith(b),
            "endswith": lambda a, b: isinstance(a, str) and a.endswith(b),
            "is_null": lambda a, b: a is None,
            "not_null": lambda a, b: a is not None,
            "in": lambda a, b: a in b,
        }

        op_func = ops.get(operator, ops["eq"])

        for v in col_values:
            mask.append(op_func(v, value))

        # Apply mask
        result = {col: [] for col in data}
        for i, keep in enumerate(mask):
            if keep:
                for col in data:
                    result[col].append(data[col][i])

        output = self._to_rows(result)
        output["rows_matched"] = sum(mask)
        output["rows_filtered"] = len(mask) - sum(mask)

        return output

    def _aggregate(
        self,
        data: Dict[str, List],
        group_by: Optional[str],
        aggregations: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Aggregate data with optional grouping."""
        agg_funcs = {
            "sum": sum,
            "mean": lambda x: statistics.mean(x) if x else 0,
            "median": lambda x: statistics.median(x) if x else 0,
            "min": min,
            "max": max,
            "count": len,
            "std": lambda x: statistics.stdev(x) if len(x) > 1 else 0,
            "first": lambda x: x[0] if x else None,
            "last": lambda x: x[-1] if x else None,
        }

        if group_by:
            # Grouped aggregation
            groups = defaultdict(lambda: defaultdict(list))

            group_values = data.get(group_by, [])
            n_rows = len(group_values)

            for i in range(n_rows):
                group_key = group_values[i]
                for col in data:
                    if col != group_by:
                        groups[group_key][col].append(data[col][i])

            # Build result
            result_cols = [group_by]
            for col, aggs in aggregations.items():
                for agg in aggs:
                    result_cols.append(f"{col}_{agg}")

            result_rows = []
            for group_key, group_data in groups.items():
                row = [group_key]
                for col, aggs in aggregations.items():
                    col_values = [v for v in group_data.get(col, []) if v is not None]
                    for agg in aggs:
                        func = agg_funcs.get(agg, len)
                        try:
                            row.append(func(col_values) if col_values else None)
                        except Exception:
                            row.append(None)
                result_rows.append(row)

            return {
                "result": {
                    "columns": result_cols,
                    "values": result_rows,
                },
                "group_count": len(groups),
            }

        else:
            # Global aggregation
            result = {}
            for col, aggs in aggregations.items():
                col_values = [v for v in data.get(col, []) if v is not None]
                for agg in aggs:
                    func = agg_funcs.get(agg, len)
                    try:
                        result[f"{col}_{agg}"] = func(col_values) if col_values else None
                    except Exception:
                        result[f"{col}_{agg}"] = None

            return {"result": result}

    def _reshape(
        self,
        data: Dict[str, List],
        reshape_type: str,
        options: Dict,
    ) -> Dict[str, Any]:
        """Reshape data (pivot, melt, transpose)."""
        if reshape_type == "transpose":
            # Simple transpose
            columns = list(data.keys())
            n_rows = len(next(iter(data.values()), []))

            new_columns = ["field"] + [f"row_{i}" for i in range(n_rows)]
            new_values = []

            for col in columns:
                new_values.append([col] + data[col])

            return {
                "result": {
                    "columns": new_columns,
                    "values": new_values,
                }
            }

        elif reshape_type == "pivot":
            index = options.get("index")
            columns_col = options.get("columns")
            values_col = options.get("values")

            if not all([index, columns_col, values_col]):
                return {"error": "Pivot requires index, columns, and values"}

            # Build pivot table
            pivot = defaultdict(dict)
            unique_cols = set()

            n_rows = len(data.get(index, []))
            for i in range(n_rows):
                idx = data[index][i]
                col = data[columns_col][i]
                val = data[values_col][i]
                pivot[idx][col] = val
                unique_cols.add(col)

            # Convert to output format
            result_cols = [index] + sorted(unique_cols)
            result_rows = []

            for idx, row_data in pivot.items():
                row = [idx] + [row_data.get(c) for c in sorted(unique_cols)]
                result_rows.append(row)

            return {
                "result": {
                    "columns": result_cols,
                    "values": result_rows,
                }
            }

        return {"error": f"Unknown reshape type: {reshape_type}"}

    def _convert(
        self,
        data: Dict[str, List],
        conversions: Dict[str, str],
    ) -> Dict[str, Any]:
        """Convert column types."""
        result = {col: list(vals) for col, vals in data.items()}
        errors = []

        converters = {
            "int": lambda x: int(x) if x is not None else None,
            "float": lambda x: float(x) if x is not None else None,
            "str": lambda x: str(x) if x is not None else None,
            "bool": lambda x: bool(x) if x is not None else None,
        }

        for col, target_type in conversions.items():
            if col not in result:
                errors.append(f"Column not found: {col}")
                continue

            converter = converters.get(target_type)
            if not converter:
                errors.append(f"Unknown type: {target_type}")
                continue

            for i, v in enumerate(result[col]):
                try:
                    result[col][i] = converter(v)
                except (ValueError, TypeError) as e:
                    errors.append(f"Conversion error at {col}[{i}]: {e}")

        output = self._to_rows(result)
        if errors:
            output["errors"] = errors

        return output

    def _derive(
        self,
        data: Dict[str, List],
        expressions: List[Dict],
    ) -> Dict[str, Any]:
        """Derive new columns from expressions."""
        result = {col: list(vals) for col, vals in data.items()}

        for expr in expressions:
            new_col = expr.get("name")
            formula = expr.get("formula")

            if not new_col or not formula:
                continue

            # Simple expression evaluation
            n_rows = len(next(iter(result.values()), []))
            new_values = []

            for i in range(n_rows):
                # Build row context
                row = {col: result[col][i] for col in result}

                try:
                    # Safe eval (only allow basic operations)
                    value = self._safe_eval(formula, row)
                    new_values.append(value)
                except Exception:
                    new_values.append(None)

            result[new_col] = new_values

        return self._to_rows(result)

    def _safe_eval(self, formula: str, context: Dict) -> Any:
        """Safely evaluate simple formulas."""
        # Only allow column references and basic math
        allowed = set(context.keys()) | {"+", "-", "*", "/", "(", ")", " ", ".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}

        # Replace column names with values
        expr = formula
        for col, val in context.items():
            if val is None:
                return None
            expr = expr.replace(col, str(val))

        # Basic validation
        for char in expr:
            if char not in "0123456789.+-*/() ":
                raise ValueError(f"Invalid character in expression: {char}")

        return eval(expr)

    def _get_suggestions(self, operation: str, result: Dict) -> List[str]:
        """Get follow-up suggestions."""
        suggestions = []

        if operation == "clean":
            changes = result.get("changes_applied", 0)
            if changes > 0:
                suggestions.append("Run data/analysis to verify cleaning results")

        elif operation == "filter":
            filtered = result.get("rows_filtered", 0)
            if filtered > 0:
                suggestions.append(f"Filtered {filtered} rows - consider saving original data")

        elif operation == "aggregate":
            suggestions.append("Use data/analysis for statistical validation")

        return suggestions

    def get_prompt(self) -> str:
        return """You are a data transformation expert.

When transforming data:
1. Preserve data integrity - no unintended data loss
2. Handle edge cases (nulls, empty values, type mismatches)
3. Document transformations applied
4. Validate results after transformation
5. Consider reversibility when possible

Common transformations:
- Cleaning: trim, fill nulls, normalize case, remove duplicates
- Filtering: select rows matching conditions
- Aggregation: group and summarize (sum, mean, count)
- Reshaping: pivot, melt, transpose
- Derivation: create new columns from existing ones
"""
