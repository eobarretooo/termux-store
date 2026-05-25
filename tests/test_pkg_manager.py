import subprocess

from core.pkg_manager import PkgManager


def test_list_all_parses_pkg_output():
    def runner(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            0,
            "Listing...\nvim/stable 9.1 aarch64 [installed]\nmpv/x11 0.39 aarch64\n",
            "",
        )

    manager = PkgManager(runner=runner)
    packages = manager.list_all()

    assert [package.name for package in packages] == ["vim", "mpv"]
    assert [package.description for package in packages] == ["", ""]
    assert packages[0].installed is True
    assert packages[1].installed is False


def test_parse_line_rejects_apt_noise_and_description_lines():
    assert PkgManager._parse_line("Listing...") is None
    assert PkgManager._parse_line("  terminal editor") is None


def test_install_returns_success_and_output():
    def runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, "installed", "")

    manager = PkgManager(runner=runner)

    assert manager.install("vim") == (True, "installed")
