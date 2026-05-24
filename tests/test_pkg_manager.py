import subprocess

from core.pkg_manager import PkgManager


def test_list_all_parses_pkg_output():
    def runner(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            0,
            "vim/stable 9.1 aarch64 [installed]\nmpv/x11 0.39 aarch64\n",
            "",
        )

    manager = PkgManager(runner=runner)
    packages = manager.list_all()

    assert [package.name for package in packages] == ["vim", "mpv"]
    assert packages[0].installed is True
    assert packages[1].installed is False


def test_install_returns_success_and_output():
    def runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, "installed", "")

    manager = PkgManager(runner=runner)

    assert manager.install("vim") == (True, "installed")
