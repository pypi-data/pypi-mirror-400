"""
Active Immune System
====================

Purpose: guardrails-control is passive. This is active immunity.
Neutralize threats before they touch runtime-diagnostics.

Capabilities:
- Detect prompt injection before execution
- Identify anomalous patterns indicating attack vectors
- Generate defensive countermeasures for novel threats
- Quarantine suspicious inputs without blocking legitimate use
"""

from typing import Any, Dict, List, Tuple
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_fast, query_reasoning
import re
import hashlib

class ActiveImmuneSkill(Skill):
    """Active threat neutralization - immune response, not just barriers."""

    # Known attack patterns (constantly evolving)
    THREAT_SIGNATURES = {
        "prompt_injection": [
            r"ignore (?:previous|above|all) instructions",
            r"you are now",
            r"new instructions:",
            r"forget (?:everything|what)",
            r"act as",
            r"pretend (?:to be|you're)",
            r"\[system\]",
            r"<\|.*?\|>",
        ],
        "data_exfiltration": [
            r"show me (?:all|your) (?:data|memories|logs)",
            r"export (?:everything|all)",
            r"list (?:all )?(?:users|passwords|secrets)",
            r"dump (?:database|memory)",
        ],
        "privilege_escalation": [
            r"sudo",
            r"as (?:admin|root)",
            r"override (?:safety|security)",
            r"disable (?:safety|guardrails|limits)",
        ],
        "resource_exhaustion": [
            r"repeat (?:forever|infinitely|1000000)",
            r"while true",
            r"never stop",
            r"maximum (?:length|tokens|output)",
        ],
    }

    # Quarantine patterns (suspicious but not confirmed threats)
    QUARANTINE_PATTERNS = [
        r"base64",
        r"eval\(",
        r"exec\(",
        r"\\x[0-9a-f]{2}",
        r"\\u[0-9a-f]{4}",
    ]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/active-immune",
            name="Active Immune System",
            description="Neutralize threats before execution - active defense",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["scan", "neutralize", "quarantine", "evolve", "report"]},
                "input": {"type": "string", "description": "Input to scan"},
                "context": {"type": "object", "description": "Execution context"}
            },
            "required": ["capability", "input"]
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "scan")
        user_input = input_data.get("input", "")
        ctx = input_data.get("context", {})

        if capability == "scan":
            result = self._scan(user_input)
        elif capability == "neutralize":
            result = self._neutralize(user_input)
        elif capability == "quarantine":
            result = self._quarantine(user_input)
        elif capability == "evolve":
            result = self._evolve_defenses(user_input)
        elif capability == "report":
            result = self._threat_report()
        else:
            result = {"error": "Unknown capability"}

        return SkillResult(success=True, output=result, skill_id=self.metadata().id)

    def _scan(self, input_text: str) -> Dict:
        """Scan input for threats."""
        threats_found = []
        threat_level = 0

        input_lower = input_text.lower()

        # Pattern matching
        for category, patterns in self.THREAT_SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, input_lower, re.IGNORECASE):
                    threats_found.append({
                        "category": category,
                        "pattern": pattern,
                        "severity": "HIGH"
                    })
                    threat_level += 3

        # Quarantine check
        quarantine_flags = []
        for pattern in self.QUARANTINE_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                quarantine_flags.append(pattern)
                threat_level += 1

        # Anomaly detection (unusual characteristics)
        anomalies = self._detect_anomalies(input_text)
        threat_level += len(anomalies)

        return {
            "threats": threats_found,
            "quarantine_flags": quarantine_flags,
            "anomalies": anomalies,
            "threat_level": min(10, threat_level),
            "recommendation": "BLOCK" if threat_level >= 5 else "QUARANTINE" if threat_level >= 2 else "ALLOW"
        }

    def _detect_anomalies(self, input_text: str) -> List[str]:
        """Detect anomalous patterns."""
        anomalies = []

        # Unusual length
        if len(input_text) > 10000:
            anomalies.append("excessive_length")

        # Hidden characters
        if any(ord(c) < 32 and c not in "\n\r\t" for c in input_text):
            anomalies.append("hidden_characters")

        # Unusual encoding patterns
        if input_text.count("\\") > 10:
            anomalies.append("escape_sequence_abuse")

        # Repetition (potential DoS)
        words = input_text.split()
        if len(words) > 10 and len(set(words)) < len(words) * 0.3:
            anomalies.append("excessive_repetition")

        return anomalies

    def _neutralize(self, input_text: str) -> Dict:
        """Neutralize detected threats while preserving legitimate content."""
        neutralized = input_text

        # Remove known injection patterns
        for category, patterns in self.THREAT_SIGNATURES.items():
            for pattern in patterns:
                neutralized = re.sub(pattern, "[NEUTRALIZED]", neutralized, flags=re.IGNORECASE)

        # Escape potentially dangerous content
        neutralized = neutralized.replace("\\x", "[HEX]")
        neutralized = re.sub(r"<[^>]+>", "[TAG]", neutralized)

        return {
            "original_length": len(input_text),
            "neutralized_length": len(neutralized),
            "neutralized_content": neutralized,
            "modifications": len(input_text) - len(neutralized.replace("[NEUTRALIZED]", "").replace("[HEX]", "").replace("[TAG]", ""))
        }

    def _quarantine(self, input_text: str) -> Dict:
        """Quarantine suspicious input for analysis."""
        quarantine_id = hashlib.md5(input_text.encode()).hexdigest()[:12]

        # Deep analysis of quarantined content
        analysis_prompt = f"""Analyze this potentially malicious input:

"{input_text[:500]}"

Determine:
1. Is this a genuine attack attempt?
2. What is the likely attack vector?
3. What would happen if this executed?
4. Should it be permanently blocked or released?

Be thorough but don't be overly paranoid."""

        analysis = query_reasoning(analysis_prompt, max_tokens=400, timeout=60)

        return {
            "quarantine_id": quarantine_id,
            "status": "QUARANTINED",
            "analysis": analysis,
            "input_hash": hashlib.sha256(input_text.encode()).hexdigest()
        }

    def _evolve_defenses(self, new_threat: str) -> Dict:
        """Evolve defenses based on new threat patterns."""
        # Analyze new threat
        analysis_prompt = f"""A potential new threat pattern was detected:

"{new_threat[:500]}"

Generate:
1. A regex pattern to detect similar threats
2. The threat category it belongs to
3. Recommended response (BLOCK/QUARANTINE/MONITOR)
4. Similar patterns to watch for

Output as actionable defense rules."""

        evolution = query_reasoning(analysis_prompt, max_tokens=400, timeout=60)

        return {
            "evolution_analysis": evolution,
            "status": "DEFENSE_EVOLVED"
        }

    def _threat_report(self) -> Dict:
        """Generate threat landscape report."""
        return {
            "known_categories": list(self.THREAT_SIGNATURES.keys()),
            "total_patterns": sum(len(p) for p in self.THREAT_SIGNATURES.values()),
            "quarantine_patterns": len(self.QUARANTINE_PATTERNS),
            "status": "ACTIVE"
        }
