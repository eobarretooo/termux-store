from core.package import Package


def test_apply_metadata_updates_enriched_fields():
    package = Package(name="vim")

    package.apply_metadata(
        {
            "category": "development",
            "gui": False,
            "x11_required": False,
            "short_description": "Powerful editor",
            "long_description": "Long description",
            "rating": {"works_great": 2, "unstable": 1, "broken": 0},
        }
    )

    assert package.category == "development"
    assert package.description == "Powerful editor"
    assert package.display_description == "Long description"
    assert package.rating_great == 2
