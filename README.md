# termux-store

A native graphical package browser for Termux. It uses Termux `pkg` as the
real package backend and enriches packages with community metadata from
[termux-store-db](https://github.com/eobarretooo/termux-store-db).

The goal is not to replace Termux repositories. The goal is to make native
packages easier to discover, install, and understand on Android with Termux X11.

## Requirements

- Termux from F-Droid
- Termux X11 for the graphical interface
- Python 3.11+
- PyQt5

## Install in Termux

```bash
pkg update && pkg upgrade
pkg install python git x11-repo
pkg install pyqt5
python -m pip install -r requirements.txt
```

Do not install PyQt5 with `pip` on Termux. Use `pkg install pyqt5` instead,
because the pip package tries to compile Qt bindings locally and requires a
working `qmake`.

## Run

Open Termux X11 first, then run:

```bash
DISPLAY=:0 python main.py
```

Outside Termux, the app can still open but package operations return empty
results because `pkg` is not available.

## Project layout

```text
termux-store/
  main.py
  core/
    package.py
    pkg_manager.py
    db_sync.py
    categories.py
  ui/
    main_window.py
    sidebar.py
    search_bar.py
    package_grid.py
    package_detail.py
    install_dialog.py
  cache/
  config/
  tests/
```

## Roadmap

- Package listing from `pkg list-all`
- Search and category filtering
- Metadata sync from `termux-store-db`
- Install/remove actions through `pkg`
- Package detail dialog
- Screenshot viewer
- Rating submission flow
- Robust background loading and terminal output display

## License

MIT
