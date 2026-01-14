from fastapi.testclient import TestClient
import server.main as main


def test_oversized_upload_rejected(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    client = TestClient(main.app)
    big_data = b"x" * (5 * 1024 * 1024 + 1)
    files = {"file": ("big.txt", big_data, "text/plain")}
    resp = client.post(
        "/api/files/upload",
        headers={"Authorization": f"Bearer {main.settings.API_TOKEN}"},
        files=files,
    )
    assert resp.status_code == 413
    upload_dir = tmp_path / ".uploads"
    assert upload_dir.exists()
    assert not list(upload_dir.iterdir())
