import builtins
import importlib


def fake_embed(text: str):
    return [float(len(text)), float(len(text.split())), 1.0]


def test_numpy_fallback(tmp_path, monkeypatch):
    original_import = builtins.__import__

    def mocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "faiss":
            raise ModuleNotFoundError
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", mocked_import)
    hm = importlib.reload(importlib.import_module("hnet.hierarchical_memory"))
    mem = hm.HierarchicalMemory(
        storage_dir=tmp_path, embedding_fn=fake_embed, max_tokens=5, overlap_tokens=1
    )
    assert mem.index is None
    mem.add_segment("conv1", "hello world. bye now.")
    assert isinstance(mem.index, hm.NumpyIndex)
    out = mem.search("conv1", "hello", top_k=1)
    assert out and out[0].startswith("hello")
