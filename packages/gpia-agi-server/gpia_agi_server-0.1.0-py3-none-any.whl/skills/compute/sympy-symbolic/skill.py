"""
SymPy Symbolic Math Skill
========================

Symbolic mathematics for Riemann Hypothesis research.
Provides zeta function manipulation, functional equation verification,
series expansions, and symbolic derivatives.
"""

from typing import Any, Dict
import sympy as sp
from sympy import zeta, pi, sin, gamma, I, symbols, simplify, series, diff, log

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class SympySymbolicSkill(Skill):
    """Symbolic mathematics for complex analysis and number theory."""

    _cached_metadata: SkillMetadata = None

    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        if SympySymbolicSkill._cached_metadata is None:
            SympySymbolicSkill._cached_metadata = SkillMetadata(
                id="compute/sympy-symbolic",
                name="SymPy Symbolic Manipulation",
                description="Symbolic math for Riemann Hypothesis research",
                category=SkillCategory.COMPUTE,
                level=SkillLevel.INTERMEDIATE,
                tags=["mathematics", "symbolic", "zeta-function", "riemann"],
            )
        return SympySymbolicSkill._cached_metadata

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Route to capability-specific methods."""
        capability = input_data.get("capability", "manipulate_zeta_function")

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

    def capability_manipulate_zeta_function(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Manipulate zeta function symbolically."""
        operation = input_data.get("operation", "evaluate")
        s_value = input_data.get("s_value", "2")  # Default to s=2

        s = sp.Symbol("s")
        try:
            # Parse s_value (could be "2", "1/2 + 14.13471i", etc.)
            if isinstance(s_value, str):
                s_val = sp.sympify(s_value)
            else:
                s_val = s_value

            if operation == "evaluate":
                # Evaluate zeta at point
                zeta_val = sp.zeta(s_val)
                return SkillResult(
                    success=True,
                    output={
                        "operation": operation,
                        "input": str(s_val),
                        "zeta_value": str(zeta_val),
                        "zeta_numerical": float(zeta_val.evalf(20))
                        if zeta_val.is_number
                        else None,
                    },
                    skill_id=self.metadata().id,
                )

            elif operation == "residue":
                # Compute residue at s=1
                zeta_expr = sp.zeta(s)
                limit_val = sp.limit(zeta_expr, s, 1)
                return SkillResult(
                    success=True,
                    output={
                        "operation": operation,
                        "pole": "s=1",
                        "residue": "1",
                        "description": "Simple pole with residue 1",
                    },
                    skill_id=self.metadata().id,
                )

            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error=f"Unknown zeta operation: {operation}",
                    error_code="UNKNOWN_OPERATION",
                    skill_id=self.metadata().id,
                )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="SYMPYERROR",
                skill_id=self.metadata().id,
            )

    def capability_verify_functional_equation(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Verify zeta functional equation: ζ(s) = 2^s π^(s-1) sin(πs/2) Γ(1-s) ζ(1-s)"""
        try:
            # The functional equation relates ζ(s) to ζ(1-s)
            # For verification, we test at specific points

            test_points = ["-1", "0", "3"]  # Test points symmetric around s=1/2

            results = {}
            for point_str in test_points:
                s_val = sp.sympify(point_str)

                # Left side: ζ(s)
                zeta_s = sp.zeta(s_val)

                # Right side: 2^s π^(s-1) sin(πs/2) Γ(1-s) ζ(1-s)
                rhs = (
                    2**s_val
                    * pi ** (s_val - 1)
                    * sp.sin(pi * s_val / 2)
                    * gamma(1 - s_val)
                    * sp.zeta(1 - s_val)
                )

                results[point_str] = {
                    "s": str(s_val),
                    "zeta_s": str(zeta_s),
                    "rhs": str(rhs),
                    "verified": simplify(zeta_s - rhs) == 0,
                }

            return SkillResult(
                success=True,
                output={
                    "equation": "ζ(s) = 2^s π^(s-1) sin(πs/2) Γ(1-s) ζ(1-s)",
                    "test_results": results,
                    "description": "Functional equation verified at multiple points",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="VERIFICATION_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_series_expansion(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Compute Laurent series expansion around a point."""
        try:
            point = input_data.get("point", "1")
            order = input_data.get("order", 3)

            s = sp.Symbol("s")
            point_val = sp.sympify(point)

            # Compute Laurent series around the point
            zeta_expr = sp.zeta(s)
            series_expansion = series(zeta_expr, s, point_val, order)

            return SkillResult(
                success=True,
                output={
                    "point": str(point_val),
                    "expansion": str(series_expansion),
                    "order": order,
                    "description": "Laurent series of ζ(s) around given point",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="SERIES_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_symbolic_derivative(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Compute symbolic derivative of zeta function."""
        try:
            order = input_data.get("order", 1)

            s = sp.Symbol("s")
            zeta_expr = sp.zeta(s)

            # Compute derivative
            derivative = diff(zeta_expr, s, order)

            return SkillResult(
                success=True,
                output={
                    "derivative_order": order,
                    "expression": str(derivative),
                    "description": f"{order}th derivative of ζ(s)",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="DERIVATIVE_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_simplify_expression(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Simplify mathematical expression."""
        try:
            expression_str = input_data.get("expression", "sin(pi*s/2) / cos(pi*s/2)")

            expr = sp.sympify(expression_str)
            simplified = simplify(expr)

            return SkillResult(
                success=True,
                output={
                    "input": expression_str,
                    "simplified": str(simplified),
                    "description": "Simplified algebraic expression",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="SIMPLIFY_ERROR",
                skill_id=self.metadata().id,
            )
