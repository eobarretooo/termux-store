from core.db_sync import DbSync


def test_fetch_index_parses_curated_markdown(tmp_path):
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

    sync = DbSync(data_file=data_file)

    assert sync.index_by_name()["geany"]["category"] == "development"
    assert sync.index_by_name()["geany"]["gui"] is True
    assert sync.index_by_name()["vim"]["x11_required"] is False


def test_curated_packages_returns_package_objects(tmp_path):
    data_file = tmp_path / "curated_packages.md"
    data_file.write_text(
        """
## Games (games)

| Pacote | Descricao | GUI | X11 |
|---|---|---|---|
| 0ad | Strategy game | yes | yes |
""",
        encoding="utf-8",
    )

    packages = DbSync(data_file=data_file).curated_packages()

    assert len(packages) == 1
    assert packages[0].name == "0ad"
    assert packages[0].category == "games"
