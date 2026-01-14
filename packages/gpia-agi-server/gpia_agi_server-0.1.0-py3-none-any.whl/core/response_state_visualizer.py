import os
import re
from typing import Iterable, Optional


def _env_enabled(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


class ResponseStateVisualizer:
    """Emit safe, staged previews of a response during CLI runs."""

    def __init__(self, env_key: str = "GPIA_RESPONSE_PREVIEW") -> None:
        self.env_key = env_key

    def enabled(self, verbose: bool) -> bool:
        return verbose and _env_enabled(self.env_key, "0")

    def emit(self, stage: str, text: str) -> None:
        if text is None:
            return
        lines = [line.rstrip() for line in str(text).splitlines() if line.strip()]
        if not lines:
            return
        prefix = f"[Preview:{stage}] "
        print(prefix + lines[0])
        for line in lines[1:]:
            print(" " * len(prefix) + line)

    def emit_list(self, stage: str, items: Iterable[str]) -> None:
        items = [item for item in items if item]
        if not items:
            return
        text = "- " + "\n- ".join(items)
        self.emit(stage, text)

    def draft_from_response(self, response: str, limit: int = 200) -> Optional[str]:
        if not response:
            return None
        lines = [line.strip() for line in response.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("Answer:"):
                return line
        normalized = re.sub(r"\s+", " ", response).strip()
        if len(normalized) <= limit:
            return normalized
        return normalized[: max(0, limit - 3)] + "..."
