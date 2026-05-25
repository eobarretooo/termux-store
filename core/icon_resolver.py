from __future__ import annotations

import os
from pathlib import Path


PAPIRUS_APPS_DIR = Path("/data/data/com.termux/files/usr/share/icons/Papirus/48x48/apps")
FALLBACK_ICON = Path(__file__).resolve().parents[1] / "assets" / "fallback_icon.svg"


def get_icon(package_name: str) -> str:
    direct = PAPIRUS_APPS_DIR / f"{package_name}.svg"
    if direct.exists():
        return str(direct)

    try:
        for filename in os.listdir(PAPIRUS_APPS_DIR):
            if package_name.lower() in filename.lower() and filename.endswith(".svg"):
                return str(PAPIRUS_APPS_DIR / filename)
    except FileNotFoundError:
        pass

    return str(FALLBACK_ICON)
