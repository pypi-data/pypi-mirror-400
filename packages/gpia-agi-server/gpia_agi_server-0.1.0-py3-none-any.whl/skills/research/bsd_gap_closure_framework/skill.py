"""
BSD Gap Closure Framework Skill
===============================

Goal: provide a solutions-provider framework for three practical gaps:
1) Effective descent / point search (bounded, heuristic)
2) Local-to-global bridge via reduction mod p (small primes)
3) Sha estimation from BSD inputs (when provided)

This is not a proof engine; it generates computational evidence + explicit "needs".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, getcontext
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:  # optional but present in this repo
    import sympy  # type: ignore
except Exception:  # pragma: no cover
    sympy = None  # type: ignore

from skills.base import Skill, SkillCategory, SkillContext, SkillLevel, SkillMetadata, SkillResult


Point = Optional[Tuple[Fraction, Fraction]]  # None = point at infinity


@dataclass(frozen=True)
class Curve:
    a: int
    b: int

    def discriminant(self) -> int:
        # Short Weierstrass: y^2 = x^3 + ax + b
        return -16 * (4 * self.a**3 + 27 * self.b**2)


def _int_is_square(n: int) -> bool:
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n


def _divisors_abs(n: int) -> List[int]:
    n = abs(n)
    if n == 0:
        return [0]
    small: List[int] = []
    large: List[int] = []
    r = math.isqrt(n)
    for d in range(1, r + 1):
        if n % d == 0:
            small.append(d)
            if d * d != n:
                large.append(n // d)
    return small + large[::-1]


def _is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if sympy is not None:
        try:
            return bool(sympy.isprime(n))
        except Exception:
            pass
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    step = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += step
        step = 6 - step
    return True


def _factorint(n: int) -> Dict[int, int]:
    if n == 0:
        return {0: 1}
    if sympy is None:
        return {}
    try:
        return {int(p): int(e) for p, e in sympy.factorint(abs(n)).items()}
    except Exception:
        return {}


def _point_key(p: Point) -> Tuple[int, int, int, int]:
    if p is None:
        return (0, 1, 0, 1)
    x, y = p
    return (x.numerator, x.denominator, y.numerator, y.denominator)


def _add_points(curve: Curve, p: Point, q: Point) -> Point:
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and y1 == -y2:
        return None
    if p != q:
        m = (y2 - y1) / (x2 - x1)
    else:
        if y1 == 0:
            return None
        m = (3 * x1 * x1 + curve.a) / (2 * y1)
    x3 = m * m - x1 - x2
    y3 = m * (x1 - x3) - y1
    return (x3, y3)


def _mul_point(curve: Curve, p: Point, n: int) -> Point:
    if n < 0:
        raise ValueError("negative scalar not supported")
    acc: Point = None
    addend = p
    k = n
    while k:
        if k & 1:
            acc = _add_points(curve, acc, addend)
        addend = _add_points(curve, addend, addend)
        k >>= 1
    return acc


def _small_order(curve: Curve, p: Point, max_n: int) -> Optional[int]:
    if p is None:
        return 1
    acc: Point = None
    for n in range(1, max_n + 1):
        acc = _add_points(curve, acc, p)
        if acc is None:
            return n
    return None


def _find_rational_2_torsion(curve: Curve) -> List[Point]:
    # Points with y=0 correspond to rational roots of x^3 + ax + b.
    roots: set[int] = set()

    # Rational root theorem: any rational root is an integer divisor of b (since leading coeff is 1).
    # Special-case b=0: every integer divides 0; the polynomial factors as x(x^2 + a).
    if curve.b == 0:
        roots.add(0)
        if _int_is_square(-curve.a):
            t = math.isqrt(-curve.a)
            roots.add(t)
            roots.add(-t)
    else:
        for d in _divisors_abs(curve.b):
            for s in (-1, 1):
                r = s * d
                if r * r * r + curve.a * r + curve.b == 0:
                    roots.add(r)

    return [(Fraction(r), Fraction(0)) for r in sorted(roots)]


def _search_integral_points(curve: Curve, x_bound: int) -> List[Point]:
    points: List[Point] = []
    seen: set[Tuple[int, int, int, int]] = set()
    for x in range(-x_bound, x_bound + 1):
        rhs = x * x * x + curve.a * x + curve.b
        if rhs < 0 or not _int_is_square(rhs):
            continue
        y = math.isqrt(rhs)
        for yy in {y, -y}:
            p = (Fraction(x), Fraction(yy))
            k = _point_key(p)
            if k not in seen:
                seen.add(k)
                points.append(p)
    return points


def _search_rational_points_uv(curve: Curve, u_bound: int, v_bound: int) -> List[Point]:
    # Search points of the form x = u/v^2, y = w/v^3 with bounded (u, v).
    points: List[Point] = []
    seen: set[Tuple[int, int, int, int]] = set()
    for v in range(1, v_bound + 1):
        v2 = v * v
        v3 = v2 * v
        v4 = v2 * v2
        v6 = v3 * v3
        for u in range(-u_bound, u_bound + 1):
            rhs = u * u * u + curve.a * u * v4 + curve.b * v6
            if rhs < 0 or not _int_is_square(rhs):
                continue
            w = math.isqrt(rhs)
            x = Fraction(u, v2)
            for ww in {w, -w}:
                y = Fraction(ww, v3)
                p = (x, y)
                k = _point_key(p)
                if k not in seen:
                    seen.add(k)
                    points.append(p)
    return points


def _legendre_symbol(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else int(ls)


def _count_points_mod_p(curve: Curve, p: int) -> int:
    # Naive O(p) count for small primes only.
    a = curve.a % p
    b = curve.b % p
    count = 1  # point at infinity
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            count += 1
            continue
        ls = _legendre_symbol(rhs, p)
        if ls == 1:
            count += 2
    return count


def _reduce_point_mod_p(p: Point, prime: int) -> Optional[Tuple[int, int]]:
    if p is None:
        return None
    x, y = p
    if x.denominator % prime == 0 or y.denominator % prime == 0:
        return None
    inv_x = pow(x.denominator % prime, prime - 2, prime)
    inv_y = pow(y.denominator % prime, prime - 2, prime)
    xr = (x.numerator % prime) * inv_x % prime
    yr = (y.numerator % prime) * inv_y % prime
    return (xr, yr)


def _decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            return Decimal(value.strip())
        return None
    except Exception:
        return None


def _estimate_sha(sha_inputs: Dict[str, Any]) -> Dict[str, Any]:
    # Expected inputs:
    #   l_star = L^{(r)}(E,1)/r!  (as Decimal-ish)
    #   period = Ω_E
    #   regulator = Reg(E)
    #   tamagawa_product = Π c_p
    #   torsion_order = |E(Q)_tors|
    getcontext().prec = 60
    tol = _decimal(sha_inputs.get("tolerance")) or Decimal("1e-6")

    required = ["rank", "l_star", "period", "regulator", "tamagawa_product", "torsion_order"]
    missing = [k for k in required if sha_inputs.get(k) in (None, "")]
    if missing:
        return {"ok": False, "missing": missing}

    rank = int(sha_inputs["rank"])
    l_star = _decimal(sha_inputs["l_star"])
    period = _decimal(sha_inputs["period"])
    regulator = _decimal(sha_inputs["regulator"])
    tamagawa_product = _decimal(sha_inputs["tamagawa_product"])
    torsion_order = Decimal(int(sha_inputs["torsion_order"]))

    if None in (l_star, period, regulator, tamagawa_product):
        return {"ok": False, "missing": ["l_star/period/regulator/tamagawa_product parse failure"]}

    if period == 0 or regulator == 0 or tamagawa_product == 0:
        return {"ok": False, "error": "period/regulator/tamagawa_product must be non-zero"}

    sha_est = (l_star * torsion_order * torsion_order) / (period * regulator * tamagawa_product)
    sha_round = sha_est.to_integral_value(rounding=ROUND_HALF_UP)
    diff = abs(sha_est - sha_round)
    ok_round = diff <= tol
    rounded_int = int(sha_round) if ok_round else None
    rounded_square = bool(rounded_int is not None and _int_is_square(rounded_int))

    return {
        "ok": True,
        "rank": rank,
        "sha_estimate": str(sha_est),
        "rounded": rounded_int,
        "rounding_diff": str(diff),
        "rounded_is_square": rounded_square,
        "note": "This is a BSD-predicted |Sha| from provided inputs, not a proof.",
    }


def _ensure_report_path(repo_root: Path, requested: Optional[str]) -> Path:
    if requested:
        p = Path(requested)
        return p if p.is_absolute() else (repo_root / p)
    out_dir = repo_root / "data" / "bsd_gap_closure_framework"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return out_dir / f"gap_closure_report_{ts}.md"


class BSDGapClosureFrameworkSkill(Skill):
    _cached_metadata: SkillMetadata = None

    GAP_DEFS = {
        "effective_descent": {
            "title": "Search Engine Gap: Effective Descent (bounded)",
            "needs": [
                "2-descent/4-descent backend (e.g., mwrank/Sage) for guaranteed progress",
                "Height/regulator computations for independence tests",
            ],
        },
        "local_global_bridge": {
            "title": "Bridge Gap: Q → F_p compatibility (local data)",
            "needs": [
                "SEA/Schoof point counting for cryptographic-size primes",
                "Efficient reduction + local invariants pipeline (c_p, a_p, conductor)",
            ],
        },
        "sha_ghost": {
            "title": "Ghost Gap: |Sha| measurement/estimation",
            "needs": [
                "L-series leading coefficient computation (analytic continuation) backend",
                "Selmer-group / Euler-system / Iwasawa-theoretic bounds tooling",
            ],
        },
    }

    def metadata(self) -> SkillMetadata:
        if BSDGapClosureFrameworkSkill._cached_metadata is None:
            BSDGapClosureFrameworkSkill._cached_metadata = SkillMetadata(
                id="research/bsd_gap_closure_framework",
                name="BSD Gap Closure Framework",
                description="Solutions-provider framework for descent, Q→Fp bridge, and Sha estimation",
                category=SkillCategory.RESEARCH,
                level=SkillLevel.ADVANCED,
                tags=["bsd", "elliptic-curves", "descent", "sha", "local-global", "cryptography"],
            )
        return BSDGapClosureFrameworkSkill._cached_metadata

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "run")
        handler = getattr(self, f"capability_{capability}", None)
        if handler is None:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )
        return handler(input_data, context)

    def capability_explain(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            output={
                "gaps": {k: v["title"] for k, v in self.GAP_DEFS.items()},
                "notes": [
                    "Pure-Python evidence generator; not a proof engine.",
                    "Short Weierstrass only: y^2 = x^3 + a x + b (a,b integers).",
                    "For large primes and full BSD invariants, external backends are required.",
                ],
            },
            skill_id=self.metadata().id,
        )

    def capability_providers(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            output={
                "effective_descent": ["rational_2_torsion", "integral_point_search", "u/v^2 rational search", "small torsion order check"],
                "local_global_bridge": ["small-prime point counting (naive)", "reduce found Q-points mod p"],
                "sha_ghost": ["BSD |Sha| estimator from provided inputs (l_star, Ω, Reg, Πc_p, torsion)"],
            },
            skill_id=self.metadata().id,
        )

    def capability_run(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        repo_root = Path(__file__).resolve().parents[3]
        curve_raw = input_data.get("curve") or {}
        curve: Optional[Curve] = None
        needs: List[Dict[str, Any]] = []

        if curve_raw:
            try:
                curve = Curve(a=int(curve_raw["a"]), b=int(curve_raw["b"]))
            except Exception:
                return SkillResult(
                    success=False,
                    output=None,
                    error="Invalid curve; expected {'a': int, 'b': int} for y^2 = x^3 + a x + b",
                    skill_id=self.metadata().id,
                )
        else:
            needs.append(
                {
                    "type": "file/inputs",
                    "id": "curve",
                    "description": "Provide short Weierstrass curve coefficients: curve={a:int,b:int}",
                    "priority": 1,
                }
            )

        search = input_data.get("search") or {}
        x_bound = int(search.get("x_bound", 200))
        u_bound = int(search.get("u_bound", 200))
        v_bound = int(search.get("v_bound", 30))
        torsion_order_max = int(search.get("torsion_order_max", 24))

        primes_raw = input_data.get("primes") or []
        primes: List[int] = []
        for p in primes_raw:
            try:
                primes.append(int(p))
            except Exception:
                continue

        max_naive_prime = int(input_data.get("max_naive_prime", 20000))
        sha_inputs = input_data.get("sha_inputs") or {}

        results: Dict[str, Any] = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "curve": curve_raw or None,
            "gaps": {},
            "needs": [],
        }

        found_points: List[Point] = []

        # --- Gap 1: Effective descent (bounded)
        gap1: Dict[str, Any] = {"status": "skipped"}
        if curve is not None:
            disc = curve.discriminant()
            tors2 = _find_rational_2_torsion(curve)
            integral_pts = _search_integral_points(curve, x_bound=x_bound)
            rational_pts = _search_rational_points_uv(curve, u_bound=u_bound, v_bound=v_bound)
            found_points = list({ _point_key(p): p for p in (tors2 + integral_pts + rational_pts) }.values())

            point_summaries = []
            for p in sorted(found_points, key=_point_key):
                ord_guess = _small_order(curve, p, max_n=torsion_order_max)
                point_summaries.append(
                    {
                        "x": str(p[0]) if p else None,
                        "y": str(p[1]) if p else None,
                        "small_order": ord_guess,
                    }
                )

            gap1 = {
                "status": "ok",
                "discriminant": disc,
                "rational_2_torsion_points": [{"x": str(p[0]), "y": "0"} for p in tors2],
                "points_found": point_summaries,
                "search_params": {
                    "x_bound": x_bound,
                    "u_bound": u_bound,
                    "v_bound": v_bound,
                    "torsion_order_max": torsion_order_max,
                },
                "notes": [
                    "Point search is bounded/heuristic; absence of points is not evidence of rank 0.",
                    "Small-order detection is a quick filter; it does not prove torsion structure.",
                ],
            }
        results["gaps"]["effective_descent"] = gap1

        # --- Gap 2: Local/global bridge via reduction mod p
        gap2: Dict[str, Any] = {"status": "skipped"}
        if curve is not None and primes:
            prime_reports: List[Dict[str, Any]] = []
            reduced_points_by_p: Dict[int, List[Dict[str, Any]]] = {}

            for p in primes:
                if not _is_prime(p):
                    prime_reports.append({"p": p, "status": "skipped", "reason": "not prime"})
                    continue
                if p <= 3:
                    prime_reports.append({"p": p, "status": "skipped", "reason": "p<=3 unsupported in naive reducer"})
                    continue
                disc_mod = curve.discriminant() % p
                if disc_mod == 0:
                    prime_reports.append({"p": p, "status": "bad_reduction", "discriminant_mod_p": 0})
                    continue
                if p > max_naive_prime:
                    needs.append(
                        {
                            "type": "capability",
                            "id": "sea_point_counting",
                            "description": f"Need SEA/Schoof implementation to count #E(F_p) for large p={p}",
                            "priority": 2,
                        }
                    )
                    prime_reports.append({"p": p, "status": "skipped", "reason": f"p>{max_naive_prime} (naive count too slow)"})
                    continue

                n_fp = _count_points_mod_p(curve, p)
                a_p = p + 1 - n_fp
                factors = _factorint(n_fp)
                prime_reports.append(
                    {
                        "p": p,
                        "status": "good_reduction",
                        "#E(F_p)": n_fp,
                        "a_p": a_p,
                        "factorization": factors or None,
                    }
                )

                if found_points:
                    reduced: List[Dict[str, Any]] = []
                    for pt in found_points:
                        rp = _reduce_point_mod_p(pt, p)
                        if rp is None:
                            continue
                        reduced.append({"x": rp[0], "y": rp[1]})
                    reduced_points_by_p[p] = reduced

            if reduced_points_by_p:
                for p, pts in reduced_points_by_p.items():
                    prime_reports.append({"p": p, "reduced_Q_points": pts})

            gap2 = {
                "status": "ok",
                "max_naive_prime": max_naive_prime,
                "primes": prime_reports,
                "notes": [
                    "Naive point counting is O(p); suitable only for small primes.",
                    "For cryptographic primes, integrate SEA/Schoof backends (not shipped here).",
                ],
            }
        elif primes and curve is not None:
            gap2 = {"status": "no_primes", "reason": "Provide primes=[...] to run local checks"}
        results["gaps"]["local_global_bridge"] = gap2

        # --- Gap 3: Sha estimator
        gap3: Dict[str, Any] = {"status": "skipped"}
        if sha_inputs:
            est = _estimate_sha(sha_inputs)
            if not est.get("ok"):
                needs.append(
                    {
                        "type": "knowledge",
                        "id": "bsd_inputs",
                        "description": f"Need BSD inputs for Sha estimate: missing={est.get('missing')}",
                        "priority": 2,
                    }
                )
                gap3 = {"status": "missing_inputs", "details": est}
            else:
                gap3 = {"status": "ok", "estimate": est}
        else:
            gap3 = {"status": "no_inputs", "reason": "Provide sha_inputs={...} to estimate |Sha|"}
        results["gaps"]["sha_ghost"] = gap3

        # Needs summary
        results["needs"] = needs

        # Optionally write report
        artifacts: Dict[str, Any] = {}
        if bool(input_data.get("write_report", False)):
            report_path = _ensure_report_path(repo_root, input_data.get("report_path"))
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_md = self._render_report(results)
            report_path.write_text(report_md, encoding="utf-8")
            artifacts["report_path"] = str(report_path)

        return SkillResult(
            success=True,
            output=results,
            artifacts=artifacts,
            skill_id=self.metadata().id,
        )

    def _render_report(self, results: Dict[str, Any]) -> str:
        curve = results.get("curve")
        ts = results.get("timestamp_utc")
        gaps = results.get("gaps", {})
        needs = results.get("needs", [])

        def _json_block(obj: Any) -> str:
            return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"

        parts = [
            "# BSD Gap Closure Framework Report",
            "",
            f"- Generated: {ts}",
            f"- Curve: {curve if curve else '(none)'}",
            "",
            "## Gap 1 — Effective Descent (bounded search)",
            _json_block(gaps.get("effective_descent", {})),
            "",
            "## Gap 2 — Q → F_p bridge (small primes)",
            _json_block(gaps.get("local_global_bridge", {})),
            "",
            "## Gap 3 — |Sha| (BSD-predicted estimate)",
            _json_block(gaps.get("sha_ghost", {})),
            "",
            "## Needs / Next Steps",
            _json_block(needs),
            "",
            "## Notes",
            "- This report is computational/operational scaffolding; it does not constitute a mathematical proof.",
        ]
        return "\n".join(parts) + "\n"
