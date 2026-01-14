import threading

from hnet.hierarchical_memory import HierarchicalMemory


# deterministic fake embedding for tests


def fake_embed(text: str):
    return [float(len(text)), float(len(text.split())), 1.0]


def test_persistence_and_versioning(tmp_path):
    mem = HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5, overlap_tokens=1
    )
    mem.add_segment("conv1", "hello world. bye now.")
    assert mem.version == 1
    loaded = HierarchicalMemory(storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5)
    assert loaded.version == 1
    assert loaded.index.ntotal == mem.index.ntotal
    res = loaded.search("conv1", "hello", top_k=1)
    assert res and res[0].startswith("hello")


def test_concurrent_writes(tmp_path):
    mem = HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=4, overlap_tokens=1
    )

    texts = [
        "alpha one. beta two.",
        "gamma three. delta four.",
        "epsilon five. zeta six.",
    ]

    def worker(cid: str, text: str):
        mem.add_segment(cid, text)

    threads = []
    for i, t in enumerate(texts):
        th = threading.Thread(target=worker, args=(f"c{i}", t))
        threads.append(th)
        th.start()
    for th in threads:
        th.join()

    # ensure all chunks were stored
    assert mem.index.ntotal >= len(texts)
    # a search should return a relevant chunk
    out = mem.search("c1", "gamma three.", top_k=5)
    assert out and out[0].startswith("gamma")
