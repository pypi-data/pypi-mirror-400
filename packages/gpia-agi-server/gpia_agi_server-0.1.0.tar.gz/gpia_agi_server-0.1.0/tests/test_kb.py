import json
import sqlite3
from pathlib import Path
from typing import List

from core import kb


def test_kb_entry_logging(tmp_path, monkeypatch):
    """Persist and query knowledge-base entries."""
    data_file = Path(__file__).parent / "data" / "kb_entries.json"
    entries = json.loads(data_file.read_text())
    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    kb.ensure_db()
    for entry in entries:
        kb.add_entry(**entry)
    last_entries = kb.last(2)
    assert len(last_entries) == 2
    search_entries = kb.search("hello")
    assert any("hello" in r["data"] for r in search_entries)
    first_id = last_entries[0]["id"]
    entry = kb.get(first_id)
    assert entry["id"] == first_id


def test_summarize_entry_accuracy():
    entry = {"data": "Alpha beta gamma delta. Epsilon zeta eta theta. Iota kappa lambda mu."}
    calls: List[str] = []

    def summarizer(text: str) -> str:
        first = text.split()[0]
        calls.append(first)
        return first

    summary = kb.summarize_entry(
        entry,
        summarizer,
        max_tokens=5,
        overlap_tokens=0,
    )
    assert summary.splitlines() == calls
    assert calls == ["Alpha", "Alpha", "Epsilon"]


def test_summarize_entry_token_budget():
    entry = {"data": "one two three. four five six. seven eight nine."}
    calls: List[int] = []

    def summarizer(text: str) -> str:
        calls.append(len(text.split()))
        return " ".join(text.split()[:2])

    summary = kb.summarize_entry(
        entry,
        summarizer,
        max_tokens=5,
        overlap_tokens=0,
    )
    assert len(summary.split()) <= 5
    assert len(calls) == 4
    assert calls[-1] == 6


def test_ingest_hierarchical_text_multi_level(tmp_path, monkeypatch):
    text = (
        "one two three. four five six. seven eight nine. ten eleven twelve. "
        "thirteen fourteen fifteen. sixteen seventeen eighteen."
    )

    def summarizer(t: str) -> str:
        return t.split()[0]

    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    kb.ensure_db()
    kb.ingest_hierarchical_text(text, summarizer, max_tokens=5, overlap_tokens=0)

    conn = sqlite3.connect(kb.get_db_path())
    rows = conn.execute("SELECT kind, data FROM entries ORDER BY id").fetchall()
    conn.close()

    entries = [(kind, json.loads(data)) for kind, data in rows]
    chunk_levels = {d["level"] for kind, d in entries if kind == "kb_chunk"}
    summary_levels = {d["level"] for kind, d in entries if kind == "kb_summary"}

    assert chunk_levels == {0, 1}
    assert summary_levels == {0, 1, 2}


def test_update_preserves_overlap(tmp_path, monkeypatch):
    text = "Sentence one. Sentence two. Sentence three."
    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    kb.ensure_db()
    kb.update(text, max_tokens=4, overlap_tokens=2)

    entries = list(reversed(kb.last(2)))
    texts = [json.loads(e["data"])["text"] for e in entries]
    assert texts[0] == "Sentence one. Sentence two."
    assert texts[1] == "Sentence two. Sentence three."


def test_schema_initialized_once(tmp_path, monkeypatch):
    create_calls: list[str] = []

    real_connect = sqlite3.connect

    class ConnWrapper:
        def __init__(self, conn):
            self._conn = conn

        def execute(self, sql, *ea, **ekw):
            if sql.strip().upper().startswith("CREATE"):
                create_calls.append(sql)
            return self._conn.execute(sql, *ea, **ekw)

        def __getattr__(self, name):
            return getattr(self._conn, name)

    def connect_wrapper(*a, **kw):
        return ConnWrapper(real_connect(*a, **kw))

    monkeypatch.setattr(sqlite3, "connect", connect_wrapper)
    monkeypatch.setenv("KB_DB_PATH", str(tmp_path / "kb.db"))
    kb.ensure_db()

    init_count = len(create_calls)

    kb.add_entry(kind="a", text="hello")
    kb.last()
    kb.search("hello")

    assert len(create_calls) == init_count
