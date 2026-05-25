from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable, Sequence

from core.package import Package


Runner = Callable[..., subprocess.CompletedProcess[str]]
ARCHITECTURES = {"aarch64", "arm", "i686", "x86_64", "all"}
APT_NOISE_LINES = {"Listing...", "Sorting...", "Full Text Search..."}


class PkgManager:
    def __init__(
        self,
        pkg_executable: str = "pkg",
        runner: Runner = subprocess.run,
    ) -> None:
        self.pkg_executable = pkg_executable
        self.runner = runner

    def available(self) -> bool:
        return shutil.which(self.pkg_executable) is not None

    def list_all(self) -> list[Package]:
        result = self._run(["list-all"])
        if result.returncode != 0:
            return []

        return [pkg for line in result.stdout.splitlines() if (pkg := self._parse_line(line))]

    def search(self, query: str) -> list[Package]:
        if not query.strip():
            return []

        result = self._run(["search", query])
        if result.returncode != 0:
            return []

        return [pkg for line in result.stdout.splitlines() if (pkg := self._parse_line(line))]

    def install(self, name: str) -> tuple[bool, str]:
        result = self._run(["install", "-y", name])
        return result.returncode == 0, self._combined_output(result)

    def remove(self, name: str) -> tuple[bool, str]:
        result = self._run(["uninstall", "-y", name])
        return result.returncode == 0, self._combined_output(result)

    def show(self, name: str) -> str:
        result = self._run(["show", name])
        return self._combined_output(result)

    def _run(self, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
        command = [self.pkg_executable, *args]
        try:
            return self.runner(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return subprocess.CompletedProcess(command, 127, "", "pkg executable not found")

    @staticmethod
    def _parse_line(line: str) -> Package | None:
        line = line.strip()
        if not line:
            return None

        parts = line.split()
        if not parts:
            return None

        raw_name = parts[0]
        if raw_name in APT_NOISE_LINES or "/" not in raw_name:
            return None

        name = raw_name.split("/", 1)[0]
        if not name:
            return None

        version = parts[1] if len(parts) > 1 else ""
        installed = "[installed" in line or "[installed," in line
        description_parts = [
            part
            for part in parts[2:]
            if part not in ARCHITECTURES and not part.startswith("[installed")
        ]
        description = " ".join(description_parts)

        return Package(
            name=name,
            version=version,
            description=description,
            installed=installed,
            install_command=f"pkg install {name}",
        )

    @staticmethod
    def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
        return "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
