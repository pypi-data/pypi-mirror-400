import json

from hnet.hierarchical_memory import HierarchicalMemory


def fake_embed(text: str):
    return [float(len(text)), float(len(text.split())), 1.0]


def test_metadata_longer_truncated(tmp_path):
    mem = HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5, overlap_tokens=1
    )
    mem.add_segment("c1", "hello world")
    meta_path = tmp_path / "meta_v1.json"
    data = json.loads(meta_path.read_text())
    data.append({"conversation_id": "bad", "text": "oops", "version": 1})
    meta_path.write_text(json.dumps(data))
    loaded = HierarchicalMemory(storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5)
    assert loaded.index is not None
    assert loaded.index.ntotal == len(loaded.metadata) == 1
    assert all(m["conversation_id"] != "bad" for m in loaded.metadata)


def test_metadata_shorter_rebuilds_index(tmp_path):
    mem = HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5, overlap_tokens=1
    )
    mem.add_segment("c1", "hello world")
    mem.add_segment("c2", "second entry")
    meta_path = tmp_path / "meta_v2.json"
    data = json.loads(meta_path.read_text())
    data.pop()  # remove last entry
    meta_path.write_text(json.dumps(data))
    loaded = HierarchicalMemory(storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5)
    assert loaded.index is not None
    assert loaded.index.ntotal == len(loaded.metadata) == 1
    # search for removed conversation should return nothing
    assert not loaded.search("c2", "second", top_k=1)


def test_save_alignment_guard(tmp_path):
    mem = HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5, overlap_tokens=1
    )
    mem.add_segment("c1", "hello world")
    # introduce misalignment
    mem.metadata.append({"conversation_id": "c2", "text": "bad", "version": 1})
    mem._save()
    assert mem.index is not None
    assert len(mem.metadata) == mem.index.ntotal == 1
