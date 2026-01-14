import yaml
from pathlib import Path


def write_config(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_determine_stage(monkeypatch, tmp_path):
    import plugins.profile.evolution as evo

    cfg_path = tmp_path / "avatar_evolution.yaml"
    write_config(cfg_path, {"dragon": {"egg": 0, "adult": 20}})
    monkeypatch.setattr(evo, "CONFIG_PATH", cfg_path)

    assert evo.determine_stage("dragon", 0) == "egg"
    assert evo.determine_stage("dragon", 25) == "adult"
    assert evo.determine_stage("unknown", 5) is None


def test_evolve_avatar_copies_stage_assets(monkeypatch, tmp_path):
    import plugins.profile.evolution as evo

    # Prepare config and assets
    cfg_path = tmp_path / "avatar_evolution.yaml"
    write_config(cfg_path, {"dragon": {"egg": 0, "young": 10}})
    assets = tmp_path / "assets"
    (assets / "dragon").mkdir(parents=True, exist_ok=True)
    (assets / "dragon" / "egg.png").write_bytes(b"egg")
    (assets / "dragon" / "young.png").write_bytes(b"young")

    profile_dir = tmp_path / "profiles"

    # Monkeypatch module paths and badge/frame helpers
    monkeypatch.setattr(evo, "CONFIG_PATH", cfg_path)
    monkeypatch.setattr(evo, "ASSETS_DIR", assets)
    monkeypatch.setattr(evo, "PROFILE_DIR", profile_dir)
    monkeypatch.setattr(evo, "badge_paths", lambda user_id: ["b1.png"])
    monkeypatch.setattr(evo, "frame_paths", lambda user_id: ["f1.png"])

    # First evolution: egg
    out1 = evo.evolve_avatar("u1", "dragon", 0)
    assert (profile_dir / "u1.png").read_bytes() == b"egg"
    assert out1["badges"] == ["b1.png"] and out1["frames"] == ["f1.png"]

    # No change when stage remains the same
    evo.evolve_avatar("u1", "dragon", 5)
    assert (profile_dir / "u1.png").read_bytes() == b"egg"

    # Upgrade to young
    evo.evolve_avatar("u1", "dragon", 10)
    assert (profile_dir / "u1.png").read_bytes() == b"young"
