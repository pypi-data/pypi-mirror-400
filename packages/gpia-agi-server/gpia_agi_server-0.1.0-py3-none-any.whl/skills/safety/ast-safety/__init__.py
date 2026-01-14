"""
AST-Based Safety Verification
=============================

Implements:
- Structural Fingerprinting (AST hashing)
- Pre-Generation Filter (reject known-bad patterns)
- Golden Snippets vs Landmines classification
- Write-Heavy/Read-Smart pattern

Based on Singapore Consensus AI Safety Methods (2025).
"""

from .skill import (
    ASTSafetySkill,
    ASTFingerprint,
    Classification,
    VulnerabilityType,
    fingerprint_code,
    filter_code,
    analyze_vulnerabilities,
)

__all__ = [
    "ASTSafetySkill",
    "ASTFingerprint",
    "Classification",
    "VulnerabilityType",
    "fingerprint_code",
    "filter_code",
    "analyze_vulnerabilities",
]
