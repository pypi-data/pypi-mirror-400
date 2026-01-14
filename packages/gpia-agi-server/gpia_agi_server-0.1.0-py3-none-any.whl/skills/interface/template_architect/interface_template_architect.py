"""
Template Architect (Ollama TEMPLATE)

Builds and validates Jinja2 templates for Modelfiles.
"""

class TemplateArchitect:
    def detect_chat_format(self, base_model: str) -> str:
        if "llama" in base_model.lower():
            return "llama3"
        if "chatml" in base_model.lower():
            return "chatml"
        return "generic"

    def construct_jinja2_layout(self, system_block: str) -> str:
        return "{{ .System }}\\n\\n{{ .Prompt }}\\n\\n{{ .Response }}"

    def validate_template_syntax(self, template: str) -> bool:
        # Placeholder: ensure braces are balanced
        return template.count("{{") == template.count("}}")
