"""Hardware aware tests for OpenVINO NPU selection."""

import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from core.settings import settings

if os.getenv("SKIP_OPENVINO") == "true":
    pytest.skip("Skipping OpenVINO tests on CI by policy", allow_module_level=True)

np = pytest.importorskip("numpy", reason="NumPy is not installed")
ov = pytest.importorskip("openvino", reason="OpenVINO is not installed")


def test_selects_npu_device(monkeypatch):
    """Embedder should use NPU when available."""

    if "NPU" not in ov.runtime.Core().available_devices:
        pytest.skip("NPU device not available")

    import integrations.openvino_embedder as oe

    fake_core = MagicMock()
    fake_core.available_devices = ["NPU", "CPU"]
    fake_result = np.ones((1, 4), dtype=float)

    compiled_model = MagicMock()
    compiled_model.inputs = [MagicMock(any_name="input_ids"), MagicMock(any_name="attention_mask")]
    fake_output = MagicMock()
    compiled_model.output.return_value = fake_output
    compiled_model.return_value = {fake_output: fake_result}

    fake_core.read_model.return_value = "model"
    fake_core.compile_model.return_value = compiled_model

    monkeypatch.setattr(oe, "Core", MagicMock(return_value=fake_core))
    monkeypatch.setattr(settings, "USE_OPENVINO", True)
    monkeypatch.setattr(settings, "OPENVINO_EMBEDDING_MODEL", "dummy.xml")
    monkeypatch.setattr(settings, "OPENVINO_TOKENIZER", "tok")

    tokenizer = MagicMock()
    tokenizer.return_value = {
        "input_ids": np.array([[1]]),
        "attention_mask": np.array([[1]]),
    }

    fake_transformers = types.ModuleType("transformers")
    fake_auto_tokenizer = MagicMock()
    fake_auto_tokenizer.from_pretrained.return_value = tokenizer
    fake_transformers.AutoTokenizer = fake_auto_tokenizer

    with patch.dict(sys.modules, {"transformers": fake_transformers}):
        vec = oe.get_embeddings("hi")

    assert fake_core.compile_model.call_args.kwargs["device_name"] == "NPU"
    assert isinstance(vec, list) and len(vec) == 4
