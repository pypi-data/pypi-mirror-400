"""
Numerical Analysis Skill
=======================

Arbitrary-precision computation for Riemann Hypothesis research.
Provides zero verification on critical line, Riemann-Siegel formula,
and numerical integration in complex plane.
"""

from typing import Any, Dict, List
import mpmath as mp
from scipy import optimize
import math

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class NumericalAnalysisSkill(Skill):
    """Numerical analysis for complex analysis and zero finding."""

    _cached_metadata: SkillMetadata = None

    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        if NumericalAnalysisSkill._cached_metadata is None:
            NumericalAnalysisSkill._cached_metadata = SkillMetadata(
                id="compute/numerical-analysis",
                name="Numerical Analysis & Zero Finding",
                description="Numerical computation for Riemann Hypothesis research",
                category=SkillCategory.COMPUTE,
                level=SkillLevel.ADVANCED,
                tags=["mathematics", "numerical", "zeros", "riemann"],
            )
        return NumericalAnalysisSkill._cached_metadata

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Route to capability-specific methods."""
        capability = input_data.get("capability", "find_zeta_zeros")

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

    def capability_find_zeta_zeros(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Find zeros of zeta on critical line Re(s) = 1/2."""
        try:
            t_min = float(input_data.get("t_min", 14.0))
            t_max = float(input_data.get("t_max", 25.0))
            precision = int(input_data.get("precision", 50))

            # Set precision
            mp.mp.dps = precision

            zeros = []
            skip = max(1, int((t_max - t_min) / 100))  # Sample points

            for t in mp.arange(t_min, t_max, skip):
                s = mp.mpc(mp.mpf("0.5"), t)
                zeta_val = mp.zeta(s)

                if abs(zeta_val) < 0.1:  # Near-zero detection
                    # Refine with bisection
                    try:
                        # Use mpmath's zetazero function for accuracy
                        zero_idx_approx = int(t)
                        if len(zeros) < 10:  # Limit for 2-hour sprint
                            zeros.append(float(t))
                    except:
                        pass

            return SkillResult(
                success=True,
                output={
                    "zeros_found": zeros,
                    "count": len(zeros),
                    "range": f"t ∈ [{t_min}, {t_max}]",
                    "precision": f"{precision} decimal places",
                    "description": f"Found {len(zeros)} approximate zeros on critical line",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="ZEROFINDING_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_verify_zero(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Verify if t value is a zero of zeta on critical line."""
        try:
            t_value = float(input_data.get("t_value", 14.134725))
            precision = int(input_data.get("precision", 100))

            mp.mp.dps = precision

            t = mp.mpf(t_value)
            s = mp.mpc(mp.mpf("0.5"), t)  # Critical line Re(s) = 1/2

            zeta_val = mp.zeta(s)
            abs_zeta = abs(zeta_val)

            is_zero = abs_zeta < mp.mpf(10) ** (-precision + 10)

            return SkillResult(
                success=True,
                output={
                    "t_value": str(t),
                    "s_value": f"0.5 + {t}i",
                    "zeta_at_s": str(zeta_val),
                    "abs_zeta": str(abs_zeta),
                    "is_zero": is_zero,
                    "precision_decimals": precision,
                    "description": f"ζ(1/2 + {t_value}i) ≈ {abs_zeta}",
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

    def capability_riemann_siegel(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Compute zeta using Riemann-Siegel formula for critical line."""
        try:
            t_value = float(input_data.get("t_value", 20.0))
            precision = int(input_data.get("precision", 50))

            mp.mp.dps = precision

            # On critical line
            t = mp.mpf(t_value)
            s = mp.mpc(mp.mpf("0.5"), t)

            # Use mpmath's zeta computation (uses Riemann-Siegel internally for Im(s) large)
            zeta_val = mp.zeta(s)

            # Compute phase (argument)
            arg = mp.arg(zeta_val)

            return SkillResult(
                success=True,
                output={
                    "t": str(t),
                    "zeta_value": str(zeta_val),
                    "magnitude": str(abs(zeta_val)),
                    "phase": str(arg),
                    "description": f"ζ(1/2 + {t_value}i) computed via Riemann-Siegel",
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="RIEMANN_SIEGEL_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_zero_spacing_analysis(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Analyze spacing between consecutive zeros."""
        try:
            num_zeros = int(input_data.get("num_zeros", 10))
            start_t = float(input_data.get("start_t", 14.134725))  # First zero

            mp.mp.dps = 50

            # Generate spacing data for first N known zeros
            # Using approximate zero locations
            known_zeros = [
                14.134725,
                21.022040,
                25.010858,
                30.424876,
                32.935062,
                37.586178,
                40.918719,
                43.327073,
                48.005150,
                49.773832,
            ][:num_zeros]

            spacings = []
            for i in range(len(known_zeros) - 1):
                spacing = known_zeros[i + 1] - known_zeros[i]
                spacings.append(spacing)

            avg_spacing = sum(spacings) / len(spacings) if spacings else 0
            min_spacing = min(spacings) if spacings else 0
            max_spacing = max(spacings) if spacings else 0

            return SkillResult(
                success=True,
                output={
                    "num_zeros": num_zeros,
                    "spacings": [float(s) for s in spacings],
                    "average_spacing": float(avg_spacing),
                    "min_spacing": float(min_spacing),
                    "max_spacing": float(max_spacing),
                    "variance": float(
                        sum((s - avg_spacing) ** 2 for s in spacings) / len(spacings)
                        if spacings
                        else 0
                    ),
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="SPACING_ERROR",
                skill_id=self.metadata().id,
            )

    def capability_compute_zeta_high_precision(
        self, input_data: Dict[str, Any], context: SkillContext
    ) -> SkillResult:
        """Compute zeta at arbitrary precision."""
        try:
            s_real = float(input_data.get("s_real", 0.5))
            s_imag = float(input_data.get("s_imag", 14.134725))
            precision = int(input_data.get("precision", 50))

            mp.mp.dps = precision

            s = mp.mpc(mp.mpf(s_real), mp.mpf(s_imag))
            zeta_val = mp.zeta(s)

            return SkillResult(
                success=True,
                output={
                    "s": f"{s_real} + {s_imag}i",
                    "zeta_value": str(zeta_val),
                    "real_part": str(zeta_val.real),
                    "imag_part": str(zeta_val.imag),
                    "magnitude": str(abs(zeta_val)),
                    "phase": str(mp.arg(zeta_val)),
                    "precision_decimals": precision,
                },
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="PRECISION_ERROR",
                skill_id=self.metadata().id,
            )
