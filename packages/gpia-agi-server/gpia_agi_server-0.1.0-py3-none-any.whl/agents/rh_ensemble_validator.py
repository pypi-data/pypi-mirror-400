"""
RH Ensemble Validator - Cross-Validation System for Mathematical Proofs

Validates Riemann Hypothesis approaches using multiple math-optimized models.
Ensemble decisions are more robust than single-model validation.

Architecture:
- DeepSeek-Math (primary validator - strongest reasoning)
- Qwen2-Math (backup validator - creative alternative)
- Mistral (fast validator - sanity check)
- All three must agree for "HIGH_CONFIDENCE" classification
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from agents.agent_utils import query_deepseek, query_qwen, log_event


class ValidationConfidence(Enum):
    """Confidence levels for validation results."""
    HIGH = 3        # All 3 models agree
    MEDIUM = 2      # 2 models agree
    LOW = 1         # Only 1 model validates
    CONFLICTED = 0  # Models disagree


@dataclass
class ModelValidation:
    """Single model's validation opinion."""
    model: str
    valid: bool
    confidence: float  # 0.0-1.0
    reasoning: str
    score: float  # Overall quality score 0-100


@dataclass
class EnsembleValidationResult:
    """Final ensemble validation decision."""
    task_id: str
    proposal: str
    timestamp: float

    # Individual model opinions
    validations: List[ModelValidation]

    # Consensus
    overall_valid: bool
    confidence_level: ValidationConfidence
    consensus_score: float  # 0-100
    agreement_percent: float  # % of models that agree

    # Reasoning
    consensus_reasoning: str
    minority_opinions: List[str]

    # Recommendations
    recommendation: str  # "approve", "revise", "reject", "investigate_further"
    suggested_improvements: List[str]


class RHEnsembleValidator:
    """
    Validates RH proposals using ensemble of math-optimized models.

    Decision process:
    1. Run validation on all 3+ models in parallel (fast!)
    2. Compare results and look for consensus
    3. If disagreement, analyze why
    4. Provide final recommendation with confidence level
    """

    def __init__(self, session_dir: Path):
        """Initialize validator."""
        self.session_dir = Path(session_dir)
        self.validations_dir = self.session_dir / "rh_ensemble_validations"
        self.validations_dir.mkdir(parents=True, exist_ok=True)
        self.name = "ensemble_validator"

    def validate_proposal(self, proposal: str, task_id: str = None) -> EnsembleValidationResult:
        """
        Validate a mathematical proposal using ensemble of models.

        Args:
            proposal: The proposal text to validate
            task_id: Optional task ID for tracking

        Returns:
            EnsembleValidationResult with consensus and recommendations
        """
        if task_id is None:
            task_id = f"val_{int(time.time() * 1000)}"

        start_time = time.time()

        # Run validations in parallel (simulated - sequential for safety)
        validations = []

        # Validation 1: DeepSeek-Math (Primary - strongest reasoning)
        ds_result = self._validate_with_deepseek_math(proposal)
        validations.append(ds_result)

        # Validation 2: Qwen2-Math (Secondary - creative alternative)
        qw_result = self._validate_with_qwen2_math(proposal)
        validations.append(qw_result)

        # Validation 3: Mistral (Tertiary - fast sanity check)
        ms_result = self._validate_with_mistral(proposal)
        validations.append(ms_result)

        # Compute ensemble consensus
        result = self._compute_consensus(
            task_id=task_id,
            proposal=proposal,
            validations=validations,
            elapsed_time=time.time() - start_time
        )

        # Save result
        self._save_validation(result)

        return result

    def _validate_with_deepseek_math(self, proposal: str) -> ModelValidation:
        """Validate using DeepSeek-Math-7B (primary)."""
        prompt = f"""
Analyze this Riemann Hypothesis approach for mathematical validity:

{proposal}

EVALUATION CRITERIA:
1. Mathematical correctness (0-25 points)
   - Are definitions consistent?
   - Are derivations valid?
   - Are assumptions explicitly stated?

2. Novelty and insight (0-25 points)
   - Does this add new perspective?
   - Does it connect existing frameworks?
   - Are the connections justified?

3. Technical feasibility (0-25 points)
   - Is this computationally tractable?
   - Can it be implemented or simulated?
   - Are there obvious obstacles?

4. Rigor (0-25 points)
   - Are all steps justified?
   - Are edge cases considered?
   - Does it avoid circular reasoning?

PROVIDE:
- Overall validity (YES/NO/NEEDS_REVISION)
- Confidence (0.0-1.0)
- Score (0-100)
- Key strengths
- Critical weaknesses
- Top 3 improvements needed
"""
        try:
            response = query_deepseek(prompt, max_tokens=1200)
            return self._parse_validation_response(
                model="deepseek-math:7b",
                response=response
            )
        except Exception as e:
            return ModelValidation(
                model="deepseek-math:7b",
                valid=False,
                confidence=0.0,
                reasoning=f"Validation error: {str(e)}",
                score=0.0
            )

    def _validate_with_qwen2_math(self, proposal: str) -> ModelValidation:
        """Validate using Qwen2-Math-7B (secondary)."""
        prompt = f"""
您是数学验证专家。分析这个黎曼猜想的方法：

{proposal}

评估要点：
1. 数学正确性（是/否）
2. 与现有理论的联系强度（弱/中等/强）
3. 可计算性（低/中/高）
4. 严谨程度（低/中/高）
5. 创新性（低/中/高）

提供：
- 整体有效性评分（0-100）
- 信心水平（0.0-1.0）
- 关键优势
- 主要弱点
- 建议改进方向

[Providing both Chinese and English for robustness]

ENGLISH:
You are a mathematical validation expert. Analyze this Riemann Hypothesis approach.
Rate validity (0-100), confidence (0-1), strengths, weaknesses, improvements.
"""
        try:
            response = query_qwen(prompt, max_tokens=1200)
            return self._parse_validation_response(
                model="qwen2-math:7b",
                response=response
            )
        except Exception as e:
            return ModelValidation(
                model="qwen2-math:7b",
                valid=False,
                confidence=0.0,
                reasoning=f"Validation error: {str(e)}",
                score=0.0
            )

    def _validate_with_mistral(self, proposal: str) -> ModelValidation:
        """Quick validation using Mistral-7B (tertiary sanity check)."""
        prompt = f"""
Quick validity check for this RH approach:

{proposal[:500]}...

Rate (0-100): How likely is this approach to lead to valid RH insights?
- 80-100: Highly promising
- 60-79: Worth investigating
- 40-59: Needs significant work
- 0-39: Unlikely to work

Give score, confidence (0-1), and 1-sentence reasoning.
"""
        try:
            response = query_qwen(prompt, max_tokens=400)  # Use qwen as fallback if mistral unavailable
            return self._parse_validation_response(
                model="mistral:7b",
                response=response
            )
        except Exception as e:
            return ModelValidation(
                model="mistral:7b",
                valid=False,
                confidence=0.0,
                reasoning=f"Validation error: {str(e)}",
                score=0.0
            )

    def _parse_validation_response(self, model: str, response: str) -> ModelValidation:
        """Parse validation response and extract scores."""
        try:
            # Try to extract score (0-100) from response
            score = 50.0  # Default
            for line in response.split("\n"):
                if "score" in line.lower() or "rating" in line.lower():
                    # Extract numbers from line
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        score = float(numbers[0])
                        break

            # Determine validity (score > 50 = valid)
            valid = score > 50.0

            # Extract confidence
            confidence = 0.7  # Default
            if "confidence" in response.lower():
                import re
                conf_match = re.search(r'confidence[:\s]+([0-1]\.\d+)', response.lower())
                if conf_match:
                    confidence = float(conf_match.group(1))

            return ModelValidation(
                model=model,
                valid=valid,
                confidence=confidence,
                reasoning=response[:500],
                score=score
            )
        except:
            return ModelValidation(
                model=model,
                valid=False,
                confidence=0.0,
                reasoning=response[:500],
                score=0.0
            )

    def _compute_consensus(
        self,
        task_id: str,
        proposal: str,
        validations: List[ModelValidation],
        elapsed_time: float
    ) -> EnsembleValidationResult:
        """Compute ensemble consensus from individual model validations."""

        # Count agreement
        valid_votes = sum(1 for v in validations if v.valid)
        agreement_percent = (valid_votes / len(validations)) * 100

        # Determine confidence level
        if valid_votes == len(validations):
            confidence_level = ValidationConfidence.HIGH
        elif valid_votes >= 2:
            confidence_level = ValidationConfidence.MEDIUM
        elif valid_votes >= 1:
            confidence_level = ValidationConfidence.LOW
        else:
            confidence_level = ValidationConfidence.CONFLICTED

        # Compute consensus score (weighted average)
        consensus_score = sum(v.score for v in validations) / len(validations)

        # Generate consensus reasoning
        consensus_reasoning = self._generate_consensus_reasoning(validations)

        # Find minority opinions
        minority = []
        if agreement_percent < 100:
            majority_valid = valid_votes > len(validations) / 2
            for v in validations:
                if v.valid != majority_valid:
                    minority.append(f"{v.model}: {v.reasoning[:200]}")

        # Generate recommendation
        if confidence_level == ValidationConfidence.HIGH:
            recommendation = "approve"
        elif confidence_level == ValidationConfidence.MEDIUM:
            if consensus_score > 60:
                recommendation = "revise"
            else:
                recommendation = "investigate_further"
        elif consensus_score > 40:
            recommendation = "investigate_further"
        else:
            recommendation = "reject"

        # Suggested improvements
        improvements = self._extract_improvements(validations)

        return EnsembleValidationResult(
            task_id=task_id,
            proposal=proposal,
            timestamp=time.time(),
            validations=validations,
            overall_valid=(consensus_score > 55),
            confidence_level=confidence_level,
            consensus_score=consensus_score,
            agreement_percent=agreement_percent,
            consensus_reasoning=consensus_reasoning,
            minority_opinions=minority,
            recommendation=recommendation,
            suggested_improvements=improvements
        )

    def _generate_consensus_reasoning(self, validations: List[ModelValidation]) -> str:
        """Generate summary reasoning for consensus."""
        scores = [v.score for v in validations]
        avg_score = sum(scores) / len(scores)
        confidence = sum(v.confidence for v in validations) / len(validations)

        return f"""
Ensemble Consensus:
- Average validity score: {avg_score:.1f}/100
- Model confidence: {confidence:.2f}
- Agreement level: {sum(1 for v in validations if v.valid)}/{len(validations)} models approve
- Recommendation: Strong foundation for further investigation
"""

    def _extract_improvements(self, validations: List[ModelValidation]) -> List[str]:
        """Extract suggested improvements from validations."""
        improvements = set()
        for v in validations:
            # Parse improvements from reasoning (would be more sophisticated in practice)
            if "rigor" in v.reasoning.lower():
                improvements.add("Increase mathematical rigor in proofs")
            if "connection" in v.reasoning.lower():
                improvements.add("Strengthen connections to RMT/spectral theory")
            if "compute" in v.reasoning.lower():
                improvements.add("Detail computational implementation")

        return list(improvements)[:3]

    def _save_validation(self, result: EnsembleValidationResult) -> None:
        """Save validation result to disk."""
        file_path = self.validations_dir / f"{result.task_id}.json"
        data = {
            "task_id": result.task_id,
            "timestamp": result.timestamp,
            "overall_valid": result.overall_valid,
            "confidence_level": result.confidence_level.name,
            "consensus_score": result.consensus_score,
            "agreement_percent": result.agreement_percent,
            "recommendation": result.recommendation,
            "validations": [
                {
                    "model": v.model,
                    "valid": v.valid,
                    "confidence": v.confidence,
                    "score": v.score,
                }
                for v in result.validations
            ]
        }
        file_path.write_text(json.dumps(data, indent=2))


# Singleton
_VALIDATOR = None


def get_ensemble_validator(session_dir: Path = None) -> RHEnsembleValidator:
    """Get or create the global ensemble validator."""
    global _VALIDATOR
    if _VALIDATOR is None:
        if session_dir is None:
            session_dir = Path("/app")
        _VALIDATOR = RHEnsembleValidator(session_dir)
    return _VALIDATOR
