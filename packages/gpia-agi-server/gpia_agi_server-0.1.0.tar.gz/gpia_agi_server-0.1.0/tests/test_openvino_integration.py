import asyncio
import json
import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from core import kb
from core.bus_client import BusClient
from core.settings import settings

np = pytest.importorskip("numpy", reason="NumPy is not installed")


def test_kb_add_entry_with_embedding(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "USE_OPENVINO", True)
    monkeypatch.setattr(settings, "OPENVINO_EMBEDDING_MODEL", "dummy.xml")
    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    kb.ensure_db()

    with patch("integrations.openvino_embedder.get_embeddings", return_value=[0.1, 0.2, 0.3]):
        kb.add_entry(kind="test", text="hello world")

    with kb._connect() as conn:
        row = conn.execute("SELECT data FROM entries").fetchone()
    stored = json.loads(row[0])
    assert stored["embedding"] == [0.1, 0.2, 0.3]


def test_bus_client_publish_includes_embedding(monkeypatch):
    monkeypatch.setattr(settings, "USE_OPENVINO", True)
    monkeypatch.setattr(settings, "OPENVINO_EMBEDDING_MODEL", "dummy.xml")

    async_mock = AsyncMock()
    bc = BusClient("http://example", "t", lambda _: None)
    bc._arequest = async_mock

    with patch("integrations.openvino_embedder.get_embeddings", return_value=[1.0, 2.0]):
        async def publish_and_close():
            await bc.publish("topic", "hello")
            await bc.stop()

        asyncio.run(publish_and_close())

    args, kwargs = async_mock.call_args
    payload = kwargs["json"]["data"]
    assert payload["embedding"] == [1.0, 2.0]


def test_get_embeddings_missing_runtime(monkeypatch):
    import integrations.openvino_embedder as oe

    monkeypatch.setattr(settings, "USE_OPENVINO", True)
    monkeypatch.setattr(settings, "OPENVINO_EMBEDDING_MODEL", "dummy.xml")

    oe._core = None
    oe._compiled_model = None
    oe._tokenizer = None
    oe.Core = None

    with pytest.raises(RuntimeError):
        oe.get_embeddings("hi")


def test_cpu_fallback_when_no_npu(monkeypatch):
    import integrations.openvino_embedder as oe

    monkeypatch.setattr(settings, "USE_OPENVINO", True)
    monkeypatch.setattr(settings, "OPENVINO_EMBEDDING_MODEL", "npu.xml")
    monkeypatch.setattr(settings, "OPENVINO_EMBEDDING_MODEL_CPU", "cpu.xml")
    monkeypatch.setattr(settings, "OPENVINO_TOKENIZER", "tok")

    oe._core = None
    oe._compiled_model = None
    oe._output = None
    oe._tokenizer = None

    fake_output = MagicMock()
    fake_result = np.ones((1, 3), dtype=float)

    compiled_model = MagicMock()
    compiled_model.inputs = [MagicMock(any_name="input_ids"), MagicMock(any_name="attention_mask")]
    compiled_model.output.return_value = fake_output
    compiled_model.return_value = {fake_output: fake_result}

    core_instance = MagicMock()
    core_instance.available_devices = ["CPU"]
    core_instance.read_model.return_value = "model"
    core_instance.compile_model.return_value = compiled_model
    CoreMock = MagicMock(return_value=core_instance)

    tokenizer = MagicMock()
    tokenizer.return_value = {
        "input_ids": np.array([[1, 2, 3]]),
        "attention_mask": np.array([[1, 1, 1]]),
    }

    fake_transformers = types.ModuleType("transformers")
    fake_auto_tokenizer = MagicMock()
    fake_auto_tokenizer.from_pretrained.return_value = tokenizer
    fake_transformers.AutoTokenizer = fake_auto_tokenizer

    monkeypatch.setattr(oe, "Core", CoreMock)

    with patch.dict(sys.modules, {"transformers": fake_transformers}):
        vec = oe.get_embeddings("hello")

    core_instance.read_model.assert_called_once_with("cpu.xml")
    assert core_instance.compile_model.call_args.kwargs["device_name"] == "CPU"
    assert compiled_model.call_count == 2
    assert isinstance(vec, list)
