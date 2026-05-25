# termux-store

A native graphical app store for Termux X11. It uses Termux `pkg` as the
package backend and a local curated catalog in `data/curated_packages.md`.

The goal is not to replace Termux repositories. The goal is to make native
packages easier to discover, install, and understand on Android with Termux X11.

## Requirements

- Termux from F-Droid
- Termux X11 for the graphical interface
- Python 3.11+
- PyQt5
- Papirus Icon Theme

## Install in Termux

```bash
pkg update && pkg upgrade
pkg install python git x11-repo
pkg install pyqt5 papirus-icon-theme
```

Do not install PyQt5 with `pip` on Termux. Use `pkg install pyqt5` instead,
because the pip package tries to compile Qt bindings locally and requires a
working `qmake`.

The app currently has no required runtime dependencies from `pip`.

## Run

Open Termux X11 first, then run:

```bash
DISPLAY=:0 python main.py
```

Outside Termux, the app can still open but package operations return empty
results because `pkg` is not available. The curated catalog is still loaded.

## Project layout

```text
termux-store/
  main.py
  core/
    package.py
    pkg_manager.py
    db_sync.py
    icon_resolver.py
    categories.py
  ui/
    main_window.py
    sidebar.py
    search_bar.py
    package_card.py
    package_grid.py
    package_detail.py
    install_dialog.py
  data/
    curated_packages.md
  cache/
  config/
  tests/
```

## Roadmap

- Curated app catalog from `data/curated_packages.md`
- Search and category filtering
- Papirus icon resolution with fallback icon
- Install/remove actions through `pkg`
- Real-time install/remove output dialog
- Package detail dialog

## License

MIT
