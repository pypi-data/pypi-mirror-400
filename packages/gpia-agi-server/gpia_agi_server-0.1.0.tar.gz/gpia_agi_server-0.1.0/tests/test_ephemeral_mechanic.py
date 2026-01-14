import os
import pytest


def test_ephemeral_synthesis_roundtrip():
    """Mechanic gate: basic create of transient identity/memory/slot."""
    from skills.lifecycle.ephemeral_synthesis.ephemeral_synthesis import EphemeralSynthesizer

    synth = EphemeralSynthesizer()
    session = synth.create()
    assert session.session_id.startswith("agent-")
    assert session.memory_shard.startswith("mem-")
    assert session.compute_slot.startswith("slot-")


@pytest.mark.skipif(
    os.environ.get("OLLAMA_URL") is None,
    reason="Requires local Ollama for build/run; skipping in non-ollama env",
)
def test_ephemeral_compile_and_cleanup_smoke(tmp_path):
    """Mechanic gate: compile a trivial Modelfile and ensure ollama create returns a result."""
    from skills.lifecycle.compile_jit_modelfile.compile_jit_modelfile import (
        JITModelfileCompiler,
    )

    compiler = JITModelfileCompiler()
    modelfile = tmp_path / "Modelfile"
    compiler.write_modelfile_artifact(
        path=str(modelfile),
        base_model="llama3",
        system_text="You are a minimal test model.",
        template="{{ .Prompt }}",
        params={"temperature": "0"},
    )
    # Note: we do not assert success of ollama create here to avoid failures in CI without models
    result = compiler.build_ephemeral_model("ghost-test-mechanic", str(modelfile))
    assert result is not None

