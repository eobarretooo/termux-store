from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Package:
    name: str
    version: str = ""
    description: str = ""
    installed: bool = False
    category: str = "utilities"
    gui: bool = False
    x11_required: bool = False
    long_description: str = ""
    install_command: str = ""
    launch_command: str = ""
    tips: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    rating_great: int = 0
    rating_unstable: int = 0
    rating_broken: int = 0

    @property
    def display_description(self) -> str:
        return self.long_description or self.description or self.short_fallback

    @property
    def short_fallback(self) -> str:
        return "No description available."

    def apply_metadata(self, metadata: dict) -> None:
        self.category = metadata.get("category", self.category)
        self.gui = bool(metadata.get("gui", self.gui))
        self.x11_required = bool(metadata.get("x11_required", self.x11_required))
        self.description = metadata.get("short_description", self.description)
        self.long_description = metadata.get("long_description", self.long_description)
        self.install_command = metadata.get("install_command", self.install_command)
        self.launch_command = metadata.get("launch_command", self.launch_command)
        self.tips = list(metadata.get("tips", self.tips))
        self.screenshots = list(metadata.get("screenshots", self.screenshots))

        rating = metadata.get("community_rating") or metadata.get("rating") or {}
        self.rating_great = int(rating.get("works_great", self.rating_great))
        self.rating_unstable = int(rating.get("unstable", self.rating_unstable))
        self.rating_broken = int(rating.get("broken", self.rating_broken))
