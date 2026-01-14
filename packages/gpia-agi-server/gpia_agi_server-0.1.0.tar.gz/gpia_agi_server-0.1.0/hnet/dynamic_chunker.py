from __future__ import annotations
from typing import Callable, List, Optional
from types import ModuleType

tiktoken: Optional[ModuleType]
try:
    import tiktoken as _tiktoken

    tiktoken = _tiktoken
except Exception:  # pragma: no cover
    tiktoken = None


def _token_count(text: str, model: str | None = None) -> int:
    """Estimate token usage for *text*.

    The function tries to use :mod:`tiktoken` for an exact count with the
    ``cl100k_base`` encoding. If ``tiktoken`` is missing or raises an error
    (e.g. unsupported model), a heuristic based on word count is used
    instead.  The heuristic assumes roughly 0.75 words per token which keeps
    the estimate close to OpenAI's tokenizer for English-like input.
    """

    if tiktoken:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            pass
    w = max(1, len(text.split()))
    return int(w / 0.75)


class DynamicChunker:
    """H-Net style dynamic chunking with soft overlap and budget awareness."""

    def __init__(self, max_tokens: int = 800, overlap_tokens: int = 80):
        if overlap_tokens >= max_tokens:
            raise ValueError("overlap_tokens must be < max_tokens")
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk(self, text: str) -> List[str]:
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        chunks: List[str] = []
        cur: List[str] = []
        cur_tokens = 0
        for s in sentences:
            t = _token_count(s)
            if t > self.max_tokens:
                chunks.extend(self._split_long_sentence(s))
                continue
            if cur_tokens + t <= self.max_tokens:
                cur.append(s)
                cur_tokens += t
            else:
                if cur:
                    chunks.append(" ".join(cur))
                    overlap = self._take_tail_tokens(cur, self.overlap_tokens)
                    cur = overlap + [s]
                    cur_tokens = _token_count(" ".join(cur))
                else:
                    chunks.append(s)
                    cur = []
                    cur_tokens = 0
        if cur:
            chunks.append(" ".join(cur))
        return chunks

    def _split_long_sentence(self, s: str) -> List[str]:
        """Break a single overlong sentence into chunks within budget.

        Token usage is estimated via :func:`_token_count`, benefiting from the
        same ``tiktoken``-with-fallback strategy.  Words are accumulated until
        the estimated tokens would exceed ``max_tokens`` and then flushed to a
        chunk.  This keeps each returned piece under the model's token budget.
        """

        words = s.split()
        out, cur = [], []
        for w in words:
            cur.append(w)
            if _token_count(" ".join(cur)) >= self.max_tokens:
                out.append(" ".join(cur))
                cur = []
        if cur:
            out.append(" ".join(cur))
        return out

    def _take_tail_tokens(self, parts: List[str], budget: int) -> List[str]:
        """Return trailing sentences covering at least ``budget`` tokens.

        Sentences are walked in reverse order and prepended until the
        estimated token count, computed via :func:`_token_count` (again using
        the ``tiktoken``-first then heuristic strategy), meets or exceeds the
        requested ``budget``.
        """

        out: List[str] = []
        for s in reversed(parts):
            out.insert(0, s)
            if _token_count(" ".join(out)) >= budget:
                break
        return out


def summarize_long_text(
    text: str,
    summarize: Callable[[str], str],
    max_tokens: int = 800,
    overlap_tokens: int = 80,
) -> str:
    """Dynamic chunk then summarize with provided callback."""
    ch = DynamicChunker(max_tokens=max_tokens, overlap_tokens=overlap_tokens)
    summaries = [summarize(c) for c in ch.chunk(text)]
    joined = "\n".join(summaries)
    if _token_count(joined) > max_tokens:
        return summarize(joined)
    return joined


def recursive_summarize(text: str, summarize: Callable[[str], str]) -> dict:
    """Recursively summarize ``text`` from sentences to document.

    The function builds a hierarchy of summaries following the
    :class:`H-Net` principle of progressive abstraction.  Each sentence is
    first summarized.  Those summaries are then aggregated into paragraph
    summaries, which are finally condensed into a single document summary.

    Parameters
    ----------
    text:
        Source text to summarize.
    summarize:
        Callback used to summarize arbitrary chunks of text.

    Returns
    -------
    dict
        Mapping with keys ``sentence_summaries`` (list of lists),
        ``paragraph_summaries`` (list) and ``document_summary`` (str).
    """

    import re

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentence_summaries: list[list[str]] = []
    paragraph_summaries: list[str] = []

    for para in paragraphs:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
        sent_sums = [summarize(s) for s in sentences]
        sentence_summaries.append(sent_sums)
        paragraph_summaries.append(summarize("\n".join(sent_sums)))

    document_summary = summarize("\n".join(paragraph_summaries))

    return {
        "sentence_summaries": sentence_summaries,
        "paragraph_summaries": paragraph_summaries,
        "document_summary": document_summary,
    }
