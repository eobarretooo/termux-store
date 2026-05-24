import json

from core.db_sync import DbSync


class Response:
    def __init__(self, payload):
        self.payload = payload
        self.text = json.dumps(payload)

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_fetch_index_writes_cache(tmp_path):
    sync = DbSync(cache_dir=tmp_path, http_get=lambda *args, **kwargs: Response([{"name": "vim"}]))

    assert sync.fetch_index() == [{"name": "vim"}]
    assert (tmp_path / "index.json").exists()


def test_fetch_index_falls_back_to_cache(tmp_path):
    (tmp_path / "index.json").write_text('[{"name": "cached"}]', encoding="utf-8")

    def failing_get(*args, **kwargs):
        raise RuntimeError("offline")

    sync = DbSync(cache_dir=tmp_path, http_get=failing_get)

    assert sync.fetch_index() == [{"name": "cached"}]
