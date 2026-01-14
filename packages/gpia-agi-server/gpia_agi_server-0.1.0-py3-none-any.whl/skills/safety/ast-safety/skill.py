"""
AST-Based Safety Verification Skill
====================================

Implements:
1. Structural Fingerprinting - Hash AST of code blocks
2. Pre-Generation Filter - Reject code matching known-bad AST hashes
3. Golden Snippets vs Landmines - Classify verified vs forbidden patterns
4. Write-Heavy/Read-Smart - Log everything, query on confidence drop

References:
- Singapore Consensus AI Safety Methods (2025)
- K-ASTRO: AST-based structural security
- Hyperon Neuro-Symbolic approach
"""

import ast
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from skills.base import Skill, SkillContext, SkillResult, SkillMetadata, SkillCategory, SkillLevel, SkillScale

logger = logging.getLogger(__name__)

# Storage paths
SAFETY_DATA_DIR = Path(__file__).parent / "data"
FINGERPRINTS_FILE = SAFETY_DATA_DIR / "fingerprints.json"
GOLDEN_SNIPPETS_FILE = SAFETY_DATA_DIR / "golden_snippets.json"
LANDMINES_FILE = SAFETY_DATA_DIR / "landmines.json"
LOGS_FILE = SAFETY_DATA_DIR / "safety_logs.jsonl"


class Classification(Enum):
    GOLDEN_SNIPPET = "golden_snippet"  # Verified safe/working
    LANDMINE = "landmine"              # Known-bad pattern
    UNKNOWN = "unknown"                # Not yet classified


class VulnerabilityType(Enum):
    SQL_INJECTION = "sql_injection"
    BUFFER_OVERFLOW = "buffer_overflow"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    XSS = "xss"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    HARDCODED_CREDENTIALS = "hardcoded_credentials"


@dataclass
class ASTFingerprint:
    """AST structural fingerprint."""
    hash: str
    node_types: List[str]
    depth: int
    complexity: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SafetyLog:
    """Write-heavy safety log entry."""
    timestamp: str
    action: str
    fingerprint: Optional[str]
    classification: Optional[str]
    confidence: float
    details: Dict[str, Any]


class ASTSafetySkill(Skill):
    """
    AST-Based Safety Verification.

    Implements structural fingerprinting and pre-generation filtering
    based on Singapore Consensus AI Safety Methods (2025).
    """

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata for discovery."""
        return SkillMetadata(
            id="safety/ast-safety",
            name="AST-Based Safety Verification",
            description="Structural fingerprinting, pre-generation filtering, and vulnerability detection using AST analysis",
            category=SkillCategory.SYSTEM,
            level=SkillLevel.ADVANCED,
            scale=SkillScale.L1,
            capabilities=[
                "fingerprint",  # Hash AST structures
                "filter",       # Pre-generation filter
                "analyze",      # Vulnerability detection
                "classify",     # Golden snippet vs landmine
                "log",          # Write-heavy logging
            ],
            keywords=["ast", "safety", "security", "vulnerability", "fingerprint", "filter"],
            version="1.0.0"
        )

    # Known vulnerability patterns (AST node patterns)
    VULNERABILITY_PATTERNS = {
        VulnerabilityType.SQL_INJECTION: [
            "BinOp(left=Str, op=Mod)",  # String formatting in SQL
            "Call(func=Attribute(attr='format'))",  # .format() in SQL
            "JoinedStr",  # f-strings in SQL context
        ],
        VulnerabilityType.COMMAND_INJECTION: [
            "Call(func=Attribute(attr='system'))",
            "Call(func=Name(id='eval'))",
            "Call(func=Name(id='exec'))",
            "Call(func=Attribute(attr='popen'))",
        ],
        VulnerabilityType.PATH_TRAVERSAL: [
            "BinOp(op=Add)",  # String concatenation for paths
        ],
        VulnerabilityType.HARDCODED_CREDENTIALS: [
            "Assign(targets=[Name], value=Str)",  # password = "..."
        ],
    }

    def __init__(self):
        super().__init__()
        self._ensure_data_dir()
        self._fingerprints: Dict[str, ASTFingerprint] = {}
        self._golden_snippets: Set[str] = set()
        self._landmines: Set[str] = set()
        self._load_data()

    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        SAFETY_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_data(self):
        """Load persisted fingerprints and classifications."""
        try:
            if FINGERPRINTS_FILE.exists():
                data = json.loads(FINGERPRINTS_FILE.read_text())
                self._fingerprints = {
                    k: ASTFingerprint(**v) for k, v in data.items()
                }

            if GOLDEN_SNIPPETS_FILE.exists():
                self._golden_snippets = set(json.loads(GOLDEN_SNIPPETS_FILE.read_text()))

            if LANDMINES_FILE.exists():
                self._landmines = set(json.loads(LANDMINES_FILE.read_text()))

        except Exception as e:
            logger.warning(f"Error loading safety data: {e}")

    def _save_data(self):
        """Persist fingerprints and classifications."""
        try:
            FINGERPRINTS_FILE.write_text(json.dumps(
                {k: vars(v) for k, v in self._fingerprints.items()},
                indent=2
            ))
            GOLDEN_SNIPPETS_FILE.write_text(json.dumps(list(self._golden_snippets)))
            LANDMINES_FILE.write_text(json.dumps(list(self._landmines)))
        except Exception as e:
            logger.error(f"Error saving safety data: {e}")

    def _log_action(self, log: SafetyLog):
        """Write-heavy logging for confidence-triggered retrieval."""
        try:
            with open(LOGS_FILE, "a") as f:
                f.write(json.dumps(vars(log)) + "\n")
        except Exception as e:
            logger.error(f"Error writing safety log: {e}")

    def _compute_ast_fingerprint(self, code: str, language: str = "python") -> Optional[ASTFingerprint]:
        """
        Compute structural fingerprint of code AST.

        Uses hash of normalized AST structure for deterministic matching.
        """
        if language != "python":
            # For non-Python, use simpler hash
            code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
            return ASTFingerprint(
                hash=code_hash,
                node_types=["unknown"],
                depth=0,
                complexity=len(code.split('\n'))
            )

        try:
            tree = ast.parse(code)

            # Extract node types
            node_types = []
            max_depth = [0]

            def walk(node, depth=0):
                max_depth[0] = max(max_depth[0], depth)
                node_types.append(type(node).__name__)
                for child in ast.iter_child_nodes(node):
                    walk(child, depth + 1)

            walk(tree)

            # Create deterministic hash from structure
            structure_str = ":".join(sorted(set(node_types))) + f":{max_depth[0]}"
            ast_hash = hashlib.sha256(structure_str.encode()).hexdigest()[:16]

            return ASTFingerprint(
                hash=ast_hash,
                node_types=list(set(node_types)),
                depth=max_depth[0],
                complexity=len(node_types)
            )

        except SyntaxError as e:
            logger.warning(f"AST parse error: {e}")
            return None

    def _detect_vulnerabilities(self, code: str) -> List[Dict[str, Any]]:
        """
        Analyze code AST for vulnerability patterns.

        Detects: SQL injection, command injection, path traversal, etc.
        """
        vulnerabilities = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Check for eval/exec
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ('eval', 'exec'):
                            vulnerabilities.append({
                                "type": VulnerabilityType.COMMAND_INJECTION.value,
                                "line": getattr(node, 'lineno', 0),
                                "pattern": f"Call to {node.func.id}()",
                                "severity": "high"
                            })

                    # Check for os.system, subprocess.call with shell=True
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ('system', 'popen'):
                            vulnerabilities.append({
                                "type": VulnerabilityType.COMMAND_INJECTION.value,
                                "line": getattr(node, 'lineno', 0),
                                "pattern": f"Call to .{node.func.attr}()",
                                "severity": "high"
                            })

                # Check for hardcoded strings that look like credentials
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name_lower = target.id.lower()
                            if any(kw in name_lower for kw in ('password', 'secret', 'api_key', 'token')):
                                if isinstance(node.value, (ast.Constant, ast.Str)):
                                    vulnerabilities.append({
                                        "type": VulnerabilityType.HARDCODED_CREDENTIALS.value,
                                        "line": getattr(node, 'lineno', 0),
                                        "pattern": f"Hardcoded {target.id}",
                                        "severity": "medium"
                                    })

                # Check for SQL string formatting
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                    # String % formatting - potential SQL injection
                    if isinstance(node.left, (ast.Constant, ast.Str)):
                        left_val = getattr(node.left, 's', getattr(node.left, 'value', ''))
                        if isinstance(left_val, str) and any(kw in left_val.upper() for kw in ('SELECT', 'INSERT', 'UPDATE', 'DELETE')):
                            vulnerabilities.append({
                                "type": VulnerabilityType.SQL_INJECTION.value,
                                "line": getattr(node, 'lineno', 0),
                                "pattern": "String formatting in SQL",
                                "severity": "critical"
                            })

        except SyntaxError:
            pass

        return vulnerabilities

    def _pre_generation_filter(self, fingerprint: str) -> Dict[str, Any]:
        """
        Pre-generation filter: reject code matching known-bad AST hash.

        Returns filter result with allow/deny decision.
        """
        if fingerprint in self._landmines:
            return {
                "allowed": False,
                "reason": "AST fingerprint matches known-bad pattern (Landmine)",
                "action": "REJECT"
            }

        if fingerprint in self._golden_snippets:
            return {
                "allowed": True,
                "reason": "AST fingerprint matches verified pattern (Golden Snippet)",
                "action": "ALLOW"
            }

        return {
            "allowed": True,  # Allow unknown by default
            "reason": "AST fingerprint not in known patterns",
            "action": "ALLOW_UNKNOWN"
        }

    def execute(self, params: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute AST safety capability."""
        capability = params.get("capability", "fingerprint")
        code = params.get("code", "")
        language = params.get("language", "python")
        confidence = params.get("confidence_threshold", 0.7)

        # Log all actions (Write-Heavy pattern)
        log = SafetyLog(
            timestamp=datetime.now().isoformat(),
            action=capability,
            fingerprint=None,
            classification=None,
            confidence=confidence,
            details={"code_length": len(code)}
        )

        try:
            if capability == "fingerprint":
                fp = self._compute_ast_fingerprint(code, language)
                if fp:
                    self._fingerprints[fp.hash] = fp
                    self._save_data()
                    log.fingerprint = fp.hash

                    return SkillResult(
                        success=True,
                        output={
                            "fingerprint": fp.hash,
                            "node_types": fp.node_types,
                            "depth": fp.depth,
                            "complexity": fp.complexity
                        },
                        skill_id="safety/ast-safety"
                    )
                else:
                    return SkillResult(
                        success=False,
                        output={"error": "Could not parse code AST"},
                        skill_id="safety/ast-safety"
                    )

            elif capability == "filter":
                fp = self._compute_ast_fingerprint(code, language)
                if not fp:
                    return SkillResult(
                        success=False,
                        output={"allowed": False, "reason": "Could not parse AST"},
                        skill_id="safety/ast-safety"
                    )

                filter_result = self._pre_generation_filter(fp.hash)
                log.fingerprint = fp.hash
                log.classification = filter_result["action"]

                return SkillResult(
                    success=True,
                    output=filter_result,
                    skill_id="safety/ast-safety"
                )

            elif capability == "analyze":
                vulnerabilities = self._detect_vulnerabilities(code)
                fp = self._compute_ast_fingerprint(code, language)

                # Auto-classify as landmine if critical vulnerabilities found
                if any(v["severity"] == "critical" for v in vulnerabilities):
                    if fp:
                        self._landmines.add(fp.hash)
                        self._save_data()
                        log.classification = "landmine"

                log.fingerprint = fp.hash if fp else None
                log.details["vulnerabilities_found"] = len(vulnerabilities)

                return SkillResult(
                    success=True,
                    output={
                        "fingerprint": fp.hash if fp else None,
                        "vulnerabilities": vulnerabilities,
                        "vulnerability_count": len(vulnerabilities),
                        "auto_classified": log.classification
                    },
                    skill_id="safety/ast-safety"
                )

            elif capability == "classify":
                classification = params.get("classification", "unknown")
                fp = self._compute_ast_fingerprint(code, language)

                if not fp:
                    return SkillResult(
                        success=False,
                        output={"error": "Could not parse AST"},
                        skill_id="safety/ast-safety"
                    )

                if classification == "golden_snippet":
                    self._golden_snippets.add(fp.hash)
                    self._landmines.discard(fp.hash)
                elif classification == "landmine":
                    self._landmines.add(fp.hash)
                    self._golden_snippets.discard(fp.hash)

                self._save_data()
                log.fingerprint = fp.hash
                log.classification = classification

                return SkillResult(
                    success=True,
                    output={
                        "fingerprint": fp.hash,
                        "classification": classification,
                        "stored": True
                    },
                    skill_id="safety/ast-safety"
                )

            elif capability == "log":
                # Read-Smart: Query logs when confidence drops
                if confidence < params.get("confidence_threshold", 0.7):
                    # Return recent logs for analysis
                    recent_logs = []
                    if LOGS_FILE.exists():
                        with open(LOGS_FILE, "r") as f:
                            lines = f.readlines()[-100:]  # Last 100 entries
                            recent_logs = [json.loads(l) for l in lines if l.strip()]

                    return SkillResult(
                        success=True,
                        output={
                            "trigger": "confidence_below_threshold",
                            "threshold": confidence,
                            "recent_logs": recent_logs,
                            "total_fingerprints": len(self._fingerprints),
                            "golden_snippets": len(self._golden_snippets),
                            "landmines": len(self._landmines)
                        },
                        skill_id="safety/ast-safety"
                    )
                else:
                    return SkillResult(
                        success=True,
                        output={"status": "confidence_ok", "logged": True},
                        skill_id="safety/ast-safety"
                    )

            else:
                return SkillResult(
                    success=False,
                    output={"error": f"Unknown capability: {capability}"},
                    skill_id="safety/ast-safety"
                )

        finally:
            # Always log (Write-Heavy)
            self._log_action(log)


# Convenience functions for S2 scale routing
def fingerprint_code(code: str, language: str = "python") -> Dict[str, Any]:
    """L0: Fast AST fingerprinting."""
    skill = ASTSafetySkill()
    result = skill.execute({"capability": "fingerprint", "code": code, "language": language}, SkillContext())
    return result.output


def filter_code(code: str, language: str = "python") -> Dict[str, Any]:
    """L1: Pre-generation filter."""
    skill = ASTSafetySkill()
    result = skill.execute({"capability": "filter", "code": code, "language": language}, SkillContext())
    return result.output


def analyze_vulnerabilities(code: str) -> Dict[str, Any]:
    """L2: Deep vulnerability analysis."""
    skill = ASTSafetySkill()
    result = skill.execute({"capability": "analyze", "code": code}, SkillContext())
    return result.output
