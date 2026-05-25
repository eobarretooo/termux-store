import re


CATEGORIES = [
    ("all", "All"),
    ("development", "Development"),
    ("terminal", "Terminal"),
    ("multimedia", "Multimedia"),
    ("network", "Network"),
    ("utilities", "Utilities"),
    ("security", "Security"),
    ("graphics", "Graphics"),
    ("productivity", "Productivity"),
    ("games", "Games"),
    ("desktop", "Desktop"),
    ("fonts", "Fonts"),
]

CATEGORY_KEYWORDS = {
    "development": {
        "clang",
        "cmake",
        "compiler",
        "gcc",
        "gdb",
        "git",
        "golang",
        "jdk",
        "lldb",
        "lua",
        "make",
        "neovim",
        "node",
        "npm",
        "perl",
        "php",
        "python",
        "ruby",
        "rust",
        "sqlite",
        "vim",
        "yarn",
    },
    "terminal": {
        "bash",
        "busybox",
        "coreutils",
        "fish",
        "fzf",
        "htop",
        "mc",
        "nano",
        "ranger",
        "screen",
        "shell",
        "termux",
        "tmux",
        "tree",
        "zsh",
    },
    "multimedia": {
        "alsa",
        "audio",
        "exif",
        "ffmpeg",
        "flac",
        "mp3",
        "mpv",
        "music",
        "opus",
        "video",
        "vorbis",
        "wav",
        "youtube",
        "yt-dlp",
    },
    "network": {
        "aria2",
        "bind",
        "curl",
        "dns",
        "ftp",
        "http",
        "iproute",
        "lynx",
        "net",
        "openssh",
        "rsync",
        "ssh",
        "tcp",
        "tor",
        "wget",
        "whois",
    },
    "security": {
        "age",
        "aircrack",
        "crypt",
        "gpg",
        "hash",
        "hydra",
        "john",
        "nmap",
        "openssl",
        "pass",
        "sqlmap",
        "ssl",
        "tshark",
    },
    "graphics": {
        "cairo",
        "fontconfig",
        "gdk",
        "gtk",
        "image",
        "imagemagick",
        "jpeg",
        "mesa",
        "png",
        "qt",
        "svg",
        "wayland",
        "x11",
        "xorg",
    },
    "productivity": {
        "calcurse",
        "calendar",
        "doc",
        "ledger",
        "note",
        "office",
        "pandoc",
        "pdf",
        "task",
        "tex",
    },
    "games": {
        "0ad",
        "bastet",
        "chess",
        "doom",
        "game",
        "moon-buggy",
        "nethack",
        "overkill",
        "rogue",
        "sdl",
        "solitaire",
    },
    "fonts": {
        "font",
        "nerd-font",
        "ttf",
    },
    "desktop": {
        "awesome",
        "bspwm",
        "desktop",
        "dmenu",
        "dunst",
        "dwm",
        "fluxbox",
        "i3",
        "icewm",
        "jwm",
        "openbox",
        "picom",
        "rofi",
        "tint2",
        "wmaker",
        "xwallpaper",
    },
}


def category_label(category_id: str) -> str:
    return dict(CATEGORIES).get(category_id, category_id.title())


def infer_category(package_name: str) -> str:
    normalized = package_name.lower()
    tokens = set(re.split(r"[^a-z0-9]+", normalized))

    if normalized.startswith("font-") or normalized.startswith("ttf-"):
        return "fonts"

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(_keyword_matches(normalized, tokens, keyword) for keyword in keywords):
            return category

    return "utilities"


def _keyword_matches(normalized: str, tokens: set[str], keyword: str) -> bool:
    if normalized == keyword or keyword in tokens:
        return True

    if normalized.startswith(keyword):
        return True

    return len(keyword) >= 4 and keyword in normalized
