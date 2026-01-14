import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from core.settings import settings

if os.getenv("SKIP_OPENVINO") == "true":
    pytest.skip("Skipping OpenVINO tests on CI by policy", allow_module_level=True)

np = pytest.importorskip("numpy", reason="NumPy is not installed")
pytest.importorskip("openvino", reason="OpenVINO is not installed")
pytest.importorskip("transformers", reason="Transformers is not installed")


def test_get_embeddings_shape(monkeypatch):
    """OpenVINO runtime is mocked and embedding vector shape validated."""
    import integrations.openvino_embedder as oe

    monkeypatch.setattr(settings, "OPENVINO_EMBEDDING_MODEL", "dummy.xml")
    monkeypatch.setattr(settings, "OPENVINO_TOKENIZER", "dummy-tokenizer")
    monkeypatch.setattr(settings, "USE_OPENVINO", True)

    fake_output = MagicMock()
    fake_result = np.ones((1, 3), dtype=float)

    compiled_model = MagicMock()
    compiled_model.inputs = [MagicMock(any_name="input_ids"), MagicMock(any_name="attention_mask")]
    compiled_model.output.return_value = fake_output
    compiled_model.return_value = {fake_output: fake_result}

    core = MagicMock()
    core.read_model.return_value = "model"
    core.compile_model.return_value = compiled_model

    tokenizer = MagicMock()
    tokenizer.return_value = {
        "input_ids": np.array([[1, 2, 3]]),
        "attention_mask": np.array([[1, 1, 1]]),
    }

    # Reset module globals in case of previous runs
    oe._core = None
    oe._compiled_model = None
    oe._output = None
    oe._tokenizer = None

    fake_core_module = types.ModuleType("core")
    fake_core_module.Core = MagicMock(return_value=core)
    fake_openvino = types.ModuleType("openvino")
    fake_openvino.runtime = fake_core_module

    fake_transformers = types.ModuleType("transformers")
    fake_auto_tokenizer = MagicMock()
    fake_auto_tokenizer.from_pretrained.return_value = tokenizer
    fake_transformers.AutoTokenizer = fake_auto_tokenizer

    with patch.dict(
        sys.modules,
        {
            "openvino": fake_openvino,
            "openvino.runtime": fake_core_module,
            "transformers": fake_transformers,
        },
    ):
        vec = oe.get_embeddings("hello world")
    assert isinstance(vec, list)
    assert len(vec) == 3
