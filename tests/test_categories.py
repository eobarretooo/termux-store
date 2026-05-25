from core.categories import infer_category


def test_infer_category_for_common_termux_packages():
    assert infer_category("vim") == "development"
    assert infer_category("python") == "development"
    assert infer_category("openssh") == "network"
    assert infer_category("ffmpeg") == "multimedia"
    assert infer_category("nmap") == "security"
    assert infer_category("font-jetbrains-mono") == "fonts"
    assert infer_category("0ad-data") == "games"
    assert infer_category("some-unknown-package") == "utilities"
