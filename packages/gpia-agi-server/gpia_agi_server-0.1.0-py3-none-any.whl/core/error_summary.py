"""Helpers for condensing verbose log output into a short summary."""

from __future__ import annotations

from hnet.dynamic_chunker import summarize_long_text
from typing import Callable, Iterable, List


def _summarize_chunk(chunk: str) -> str:
    """Return a terse representation of *chunk*.

    The first line is kept and truncated to 200 characters.  This avoids
    requiring an LLM while still producing a readable synopsis for each
    chunk of log text.
    """

    lines = [line for line in chunk.strip().splitlines() if line.strip()]
    if not lines:
        return ""
    first = lines[0]
    if len(first) > 200:
        first = first[:197] + "..."
    if len(lines) > 1:
        first += " ..."
    return first


def summarize_chunks(
    chunks: Iterable[Iterable[str]],
    summarize: Callable[[str], str] = _summarize_chunk,
) -> str:
    """Summarize a sequence of pre-chunked parts.

    Each ``chunk`` in ``chunks`` is an iterable of string fragments. The
    fragments are concatenated without additional separators so repeated
    portions remain contiguous. The resulting chunk is then summarized via
    ``summarize``. The individual summaries are joined with newlines.
    """

    summarized: List[str] = []
    for parts in chunks:
        joined_chunk = "".join(parts)
        summarized.append(summarize(joined_chunk))
    return "\n".join(summarized)


def summarize(raw: str, *, max_tokens: int = 800, overlap_tokens: int = 80) -> str:
    """Summarize ``raw`` log text using H-Net dynamic chunking.

    Parameters
    ----------
    raw:
        Raw log text to condense.
    max_tokens:
        Token budget for each chunk.  Use smaller values for tests.
    overlap_tokens:
        Number of tokens to overlap across chunk boundaries.
    """

    return summarize_long_text(
        raw,
        summarize=_summarize_chunk,
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
    )


__all__ = ["summarize", "summarize_chunks"]
