import subprocess

from core.db_sync import DbSync
from core.pkg_manager import PkgManager
from core.store import TermuxStore


def test_store_refresh_merges_curated_catalog_with_pkg_state(tmp_path):
    data_file = tmp_path / "curated_packages.md"
    data_file.write_text(
        """
## Development (development)

| Pacote | Descricao | GUI | X11 |
|---|---|---|---|
| geany | Lightweight IDE | yes | yes |
| vim | Terminal editor | no | no |
""",
        encoding="utf-8",
    )

    def runner(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            0,
            "vim/stable 9.1 aarch64 [installed]\ngeany/x11 2.0 aarch64\n",
            "",
        )

    store = TermuxStore(
        pkg_manager=PkgManager(runner=runner),
        db_sync=DbSync(data_file=data_file),
    )

    store.refresh()

    assert len(store.all_packages()) == 2
    assert store.category_packages("development")[0].category == "development"
    assert [package.name for package in store.installed_packages()] == ["vim"]


def test_store_search_filters_current_listing(tmp_path):
    data_file = tmp_path / "curated_packages.md"
    data_file.write_text(
        """
## Network (network)

| Pacote | Descricao | GUI | X11 |
|---|---|---|---|
| firefox | Web browser | yes | yes |
| qbittorrent | Torrent client | yes | yes |
""",
        encoding="utf-8",
    )

    store = TermuxStore(
        pkg_manager=PkgManager(runner=lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "", "")),
        db_sync=DbSync(data_file=data_file),
    )

    store.refresh()

    results = store.search("web", store.category_packages("network"))

    assert [package.name for package in results] == ["firefox"]
