"""
System Definition (Ollama SYSTEM)

Drafts persona and constraints for system prompts.
"""

class SystemDefinition:
    def draft_persona_manifest(self, role: str) -> str:
        return f"You are {role}. Follow the constraints below."

    def inject_operational_constraints(self, constraints: list[str]) -> str:
        return "\n".join(constraints)

    def build_system_text(self, role: str, constraints: list[str]) -> str:
        return self.draft_persona_manifest(role) + "\n" + self.inject_operational_constraints(constraints)
