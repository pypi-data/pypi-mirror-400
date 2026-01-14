from core import kb
import agents
from hnet.dynamic_chunker import DynamicChunker


class DummyMemory:
    def add_segment(self, conversation_id, text):
        pass

    def search(self, conversation_id, query, top_k=5):
        return []


def test_fetch_context_dynamic_chunking_and_summary(monkeypatch, tmp_path):
    import hnet.dynamic_chunker as dc

    monkeypatch.setattr(dc, "tiktoken", None)
    monkeypatch.setattr(kb.settings, "USE_OPENVINO", False)
    entries = []
    monkeypatch.setattr(
        kb,
        "add_entry",
        lambda **data: entries.append(
            {"id": len(entries) + 1, "kind": data.get("kind"), "data": str(data), "ts": ""}
        ),
    )
    monkeypatch.setattr(kb, "last", lambda n=31: list(reversed(entries))[:n])
    monkeypatch.setattr(agents, "last", lambda n=31: list(reversed(entries))[:n])
    long_text = " ".join(f"w{i}" for i in range(60))
    kb.add_entry(kind="note", text=long_text)

    boundaries = []

    def fake_ingest(text, summarizer, *, max_tokens, overlap_tokens, meta=None):
        ch = DynamicChunker(max_tokens=max_tokens, overlap_tokens=overlap_tokens)
        chunks = ch.chunk(text)
        boundaries.extend(len(c.split()) for c in chunks)
        return " | ".join(summarizer(c) for c in chunks)

    monkeypatch.setattr(kb, "ingest_hierarchical_text", fake_ingest)
    monkeypatch.setattr(agents, "ingest_hierarchical_text", fake_ingest)
    monkeypatch.setattr(agents, "HierarchicalMemory", lambda **kwargs: DummyMemory())
    monkeypatch.setattr(
        agents,
        "DynamicChunker",
        lambda *a, **k: DynamicChunker(max_tokens=20, overlap_tokens=5),
    )

    context = agents.fetch_context(n=1)

    assert all(b <= 20 for b in boundaries)
    assert "w0" in context and "w59" in context


class QueryMemory(DummyMemory):
    def __init__(self):
        self.queries = []

    def search(self, conversation_id, query, top_k=5):
        self.queries.append((conversation_id, query))
        return ["reconstructed"]


def test_fetch_context_query_reconstruction(monkeypatch, tmp_path):
    import hnet.dynamic_chunker as dc

    monkeypatch.setattr(dc, "tiktoken", None)
    monkeypatch.setattr(kb.settings, "USE_OPENVINO", False)
    entries = []
    monkeypatch.setattr(
        kb,
        "add_entry",
        lambda **data: entries.append(
            {"id": len(entries) + 1, "kind": data.get("kind"), "data": str(data), "ts": ""}
        ),
    )
    monkeypatch.setattr(kb, "last", lambda n=31: list(reversed(entries))[:n])
    monkeypatch.setattr(agents, "last", lambda n=31: list(reversed(entries))[:n])
    kb.add_entry(kind="note", text="alpha beta gamma delta")

    monkeypatch.setattr(
        kb,
        "ingest_hierarchical_text",
        lambda text, summarizer, **kw: summarizer(text),
    )
    monkeypatch.setattr(
        agents,
        "ingest_hierarchical_text",
        lambda text, summarizer, **kw: summarizer(text),
    )
    mem = QueryMemory()
    monkeypatch.setattr(agents, "HierarchicalMemory", lambda **kw: mem)
    monkeypatch.setattr(
        agents,
        "DynamicChunker",
        lambda *a, **k: DynamicChunker(max_tokens=20, overlap_tokens=5),
    )

    context = agents.fetch_context(n=1, query="beta")
    assert "reconstructed" in context
    assert mem.queries == [("kb", "beta")]


def test_fetch_context_handles_invalid_json(monkeypatch):
    import hnet.dynamic_chunker as dc

    monkeypatch.setattr(dc, "tiktoken", None)
    monkeypatch.setattr(kb.settings, "USE_OPENVINO", False)

    entries = []

    def fake_add(**data):
        entries.append(
            {"id": len(entries) + 1, "kind": data.get("kind"), "data": data.get("text"), "ts": ""}
        )

    monkeypatch.setattr(kb, "add_entry", fake_add)
    monkeypatch.setattr(kb, "last", lambda n=31: list(reversed(entries))[:n])
    monkeypatch.setattr(agents, "last", lambda n=31: list(reversed(entries))[:n])

    kb.add_entry(kind="note", text="ignored")
    entries[-1]["data"] = "not json"

    monkeypatch.setattr(
        kb,
        "ingest_hierarchical_text",
        lambda text, summarizer, **kw: summarizer(text),
    )
    monkeypatch.setattr(
        agents,
        "ingest_hierarchical_text",
        lambda text, summarizer, **kw: summarizer(text),
    )
    monkeypatch.setattr(agents, "HierarchicalMemory", lambda **kw: DummyMemory())
    monkeypatch.setattr(
        agents,
        "DynamicChunker",
        lambda *a, **k: DynamicChunker(max_tokens=20, overlap_tokens=5),
    )

    context = agents.fetch_context(n=1)
    assert "not json" in context
