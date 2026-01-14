from hnet.dynamic_chunker import DynamicChunker, summarize_long_text
from core import kb
import agents


def test_chunker_respects_budget():
    text = " ".join([f"Sentence {i}." for i in range(200)])
    ch = DynamicChunker(max_tokens=200, overlap_tokens=40)
    parts = ch.chunk(text)
    assert len(parts) >= 2
    assert all(len(p.split()) < 400 for p in parts)


def test_hierarchical_summarize_reduces_size():
    text = " ".join([f"This is a long sentence number {i}." for i in range(500)])
    s = summarize_long_text(text, summarize=lambda x: x[:120], max_tokens=300)
    assert len(s) <= 600


def test_token_count_fallback_when_tiktoken_unavailable(monkeypatch):
    import hnet.dynamic_chunker as dc

    monkeypatch.setattr(dc, "tiktoken", None)
    assert dc.tiktoken is None
    # 3 words -> int(3 / 0.75) == 4
    assert dc._token_count("one two three") == 4


def test_overlap_across_chunk_boundary(monkeypatch):
    import hnet.dynamic_chunker as dc

    monkeypatch.setattr(dc, "tiktoken", None)
    text = "Sentence one. Sentence two. Sentence three."
    ch = dc.DynamicChunker(max_tokens=4, overlap_tokens=2)
    parts = ch.chunk(text)
    assert parts[0] == "Sentence one. Sentence two."
    assert parts[1] == "Sentence two. Sentence three."


def test_long_sentence_is_split(monkeypatch):
    import hnet.dynamic_chunker as dc

    monkeypatch.setattr(dc, "tiktoken", None)
    text = " ".join(["word"] * 100) + "."
    ch = dc.DynamicChunker(max_tokens=40, overlap_tokens=10)
    parts = ch.chunk(text)
    assert len(parts) > 1
    assert all(dc._token_count(p) <= ch.max_tokens for p in parts)


def test_hierarchical_summaries_persist_across_agent_exchanges(tmp_path, monkeypatch):
    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    kb.ensure_db()

    def summarizer(t: str) -> str:
        return t.upper()

    kb.ingest_hierarchical_text(
        "user: hello\nassistant: hi",
        summarizer,
        max_tokens=50,
        overlap_tokens=0,
    )
    kb.ingest_hierarchical_text(
        "user: next\nassistant: ok",
        summarizer,
        max_tokens=50,
        overlap_tokens=0,
    )

    context = agents.fetch_context(n=10)
    assert "USER: HELLO" in context
    assert "USER: NEXT" in context
