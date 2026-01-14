import json
import os
from pathlib import Path

import pytest
import tkinter as tk

from ui.pixel_avatar import PixelAvatarEditor, edit_avatar


pytestmark = pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="No display")


def test_save_uses_atomic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    called = {}

    def fake_replace(src, dst):
        called["src"] = src
        called["dst"] = dst
        original_replace(src, dst)

    original_replace = os.replace
    monkeypatch.setattr(os, "replace", fake_replace)

    editor = PixelAvatarEditor("tester")
    editor.pixels[0][0] = 1
    editor._save()
    editor.destroy()

    assert called["src"] != called["dst"]
    path = Path("plugins/profile/avatars/tester.json")
    assert path.exists()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["pixels"][0][0] == 1


def test_edit_avatar_handles_tclerror(monkeypatch, capsys):
    def fake_init(*args, **kwargs):
        raise tk.TclError("no display")

    monkeypatch.setattr(PixelAvatarEditor, "__init__", fake_init)
    edit_avatar("tester")
    captured = capsys.readouterr()
    assert "Failed to start GUI" in captured.out
