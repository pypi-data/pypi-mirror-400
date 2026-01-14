"""
Dialogue Dramatizer

Turns grounded notes into a two-speaker script with prosody markers.
"""

from typing import List, Dict


class DialogueDramatizer:
    def __init__(self, host: str = "Host", expert: str = "Expert") -> None:
        self.host = host
        self.expert = expert

    def identify_key_themes(self, notes: List[str]) -> List[str]:
        return notes[:3]

    def assign_persona_roles(self) -> Dict[str, str]:
        return {"A": self.host, "B": self.expert}

    def generate_banter_turn(self, theme: str) -> List[str]:
        return [
            f"{self.host}: Let's unpack {theme}.",
            f"{self.expert}: Sure—think of it like a quick analogy.",
            f"{self.host}: Interesting, but what about the trade-offs?",
        ]

    def insert_prosody_markers(self, lines: List[str]) -> List[str]:
        return [line.replace("?", "? <break time='300ms'/>") for line in lines]

    def dramatize(self, notes: List[str]) -> List[str]:
        themes = self.identify_key_themes(notes)
        script: List[str] = []
        for theme in themes:
            turns = self.generate_banter_turn(theme)
            script.extend(self.insert_prosody_markers(turns))
        return script
