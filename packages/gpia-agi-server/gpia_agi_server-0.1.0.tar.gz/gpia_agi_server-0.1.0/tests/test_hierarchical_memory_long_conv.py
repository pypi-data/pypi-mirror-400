"""End-to-end tests for long conversations in hierarchical memory."""

from hnet.hierarchical_memory import HierarchicalMemory


def fake_embed(text: str) -> list[float]:
    for tok in text.split():
        if tok.isdigit():
            return [float(tok)]
    return [0.0]


def test_long_conversation_context(tmp_path):
    mem = HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5, overlap_tokens=1
    )
    for i in range(50):
        mem.add_segment("conv", f"turn {i} content")

    recent = mem.search("conv", "turn 49", top_k=1)
    assert recent and "49" in recent[0]

    early = mem.search("conv", "turn 0", top_k=1)
    assert early and "0" in early[0]


def test_retrieve_multiple_chunks(tmp_path):
    """Retrieving several relevant chunks from a long conversation."""

    mem = HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5, overlap_tokens=1
    )
    for i in range(100):
        mem.add_segment("conv", f"turn {i} content")

    hits = mem.search("conv", "turn 5", top_k=3)
    assert len(hits) == 3
    assert "5" in hits[0]
