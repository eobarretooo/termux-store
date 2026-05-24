from core.db_sync import DbSync


def test_fetch_index_writes_cache(tmp_path):
    sync = DbSync(cache_dir=tmp_path, http_get=lambda url, timeout: '[{"name": "vim"}]')

    assert sync.fetch_index() == [{"name": "vim"}]
    assert (tmp_path / "index.json").exists()


def test_fetch_index_falls_back_to_cache(tmp_path):
    (tmp_path / "index.json").write_text('[{"name": "cached"}]', encoding="utf-8")

    def failing_get(url, timeout):
        raise RuntimeError("offline")

    sync = DbSync(cache_dir=tmp_path, http_get=failing_get)

    assert sync.fetch_index() == [{"name": "cached"}]
