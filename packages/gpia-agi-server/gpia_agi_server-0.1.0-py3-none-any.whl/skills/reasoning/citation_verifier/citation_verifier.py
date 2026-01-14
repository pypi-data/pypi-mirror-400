"""
Citation Verifier

Validates claims against provided source spans and adds inline citations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Claim:
    text: str
    supported: bool = False
    citation: str = ""


class CitationVerifier:
    def __init__(self, sources: List[Dict[str, Any]]) -> None:
        self.sources = sources

    def extract_claim_atoms(self, text: str) -> List[Claim]:
        parts = [p.strip() for p in text.split(".") if p.strip()]
        return [Claim(text=p + ".") for p in parts]

    def locate_source_span(self, claim: Claim) -> str:
        # Placeholder: in real use, match against sources using similarity
        if self.sources:
            src = self.sources[0]
            return f"{src.get('path','unknown')}:L1"
        return ""

    def generate_inline_citation(self, claim: Claim) -> Claim:
        citation = self.locate_source_span(claim)
        if citation:
            claim.supported = True
            claim.citation = f"[Source: {citation}]"
        return claim

    def prune_unsupported_claims(self, claims: List[Claim]) -> List[Claim]:
        return [c for c in claims if c.supported]

    def verify(self, text: str) -> Dict[str, Any]:
        claims = self.extract_claim_atoms(text)
        claims = [self.generate_inline_citation(c) for c in claims]
        supported = self.prune_unsupported_claims(claims)
        validated = " ".join(f"{c.text} {c.citation}".strip() for c in supported)
        unsupported = [c.text for c in claims if not c.supported]
        return {"validated_text": validated, "unsupported_claims": unsupported}
