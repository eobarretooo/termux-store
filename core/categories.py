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
    ("fonts", "Fonts"),
]


def category_label(category_id: str) -> str:
    return dict(CATEGORIES).get(category_id, category_id.title())
