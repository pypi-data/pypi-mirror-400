"""Color palette system compatible with svg-sdk palettes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel

from sprite_kit.core.color import Color


class Palette(BaseModel):
    """Named collection of colors.

    Example:
        >>> palette = Palette(name="test", colors={"primary": "#FF0000", "secondary": "#00FF00"})
        >>> palette["primary"]
        Color(r=255, g=0, b=0, a=1.0)
    """

    name: str
    colors: dict[str, str]

    def __getitem__(self, key: str) -> Color:
        """Get color by name.

        Args:
            key: Color name

        Returns:
            Color instance

        Raises:
            KeyError: If color not found
        """
        if key not in self.colors:
            raise KeyError(f"Color '{key}' not found in palette '{self.name}'")
        return Color.from_hex(self.colors[key])

    def get(self, key: str, default: str | None = None) -> Color | None:
        """Get color by name with optional default.

        Args:
            key: Color name
            default: Default hex color if not found

        Returns:
            Color instance or None
        """
        if key in self.colors:
            return Color.from_hex(self.colors[key])
        if default is not None:
            return Color.from_hex(default)
        return None

    def keys(self) -> list[str]:
        """Get all color names."""
        return list(self.colors.keys())

    def values(self) -> list[Color]:
        """Get all colors."""
        return [Color.from_hex(v) for v in self.colors.values()]

    def items(self) -> list[tuple[str, Color]]:
        """Get all (name, color) pairs."""
        return [(k, Color.from_hex(v)) for k, v in self.colors.items()]

    def __contains__(self, key: str) -> bool:
        """Check if color name exists."""
        return key in self.colors

    def __len__(self) -> int:
        """Get number of colors."""
        return len(self.colors)


class PaletteRegistry(BaseModel):
    """Registry of all available palettes.

    Loads palettes from svg-sdk format JSON file.

    Example:
        >>> registry = PaletteRegistry.load_default()
        >>> palette = registry.get("companion")
        >>> palette["warden"]
        Color(r=94, g=139, b=124, a=1.0)
    """

    palettes: dict[str, Palette]

    # Built-in palette names (compatible with svg-sdk)
    BUILTIN_PALETTES: ClassVar[list[str]] = [
        "brand",
        "neon",
        "indigo",
        "neutral",
        "consulting",
        "heart",
        "stance",
        "ritual",
        "phase",
        "ui",
        "companion",
        "elements",
    ]

    @classmethod
    def load_default(cls) -> PaletteRegistry:
        """Load built-in palettes from data/palettes.json.

        Returns:
            PaletteRegistry with all built-in palettes
        """
        # Find the palettes.json relative to this module
        module_dir = Path(__file__).parent.parent.parent.parent
        palettes_path = module_dir / "data" / "palettes.json"

        if not palettes_path.exists():
            # Fallback: check in installed package location
            import importlib.resources

            try:
                files = importlib.resources.files("sprite_kit")
                palettes_path = files.joinpath("..", "data", "palettes.json")  # type: ignore[assignment]
            except (ImportError, TypeError):
                pass

        return cls.load_from_file(palettes_path)

    @classmethod
    def load_from_file(cls, path: Path | str) -> PaletteRegistry:
        """Load palettes from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            PaletteRegistry with loaded palettes
        """
        path = Path(path)
        with open(path) as f:
            data = json.load(f)

        palettes = {}
        for name, colors in data.items():
            palettes[name] = Palette(name=name, colors=colors)

        return cls(palettes=palettes)

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, str]]) -> PaletteRegistry:
        """Create registry from dictionary.

        Args:
            data: Dict of palette_name -> {color_name: hex_value}

        Returns:
            PaletteRegistry
        """
        palettes = {}
        for name, colors in data.items():
            palettes[name] = Palette(name=name, colors=colors)
        return cls(palettes=palettes)

    def get(self, name: str) -> Palette:
        """Get palette by name.

        Args:
            name: Palette name

        Returns:
            Palette instance

        Raises:
            KeyError: If palette not found
        """
        if name not in self.palettes:
            available = ", ".join(self.palettes.keys())
            raise KeyError(f"Palette '{name}' not found. Available: {available}")
        return self.palettes[name]

    def register(self, palette: Palette) -> None:
        """Register a custom palette.

        Args:
            palette: Palette to register
        """
        self.palettes[palette.name] = palette

    def list_palettes(self) -> list[str]:
        """Get all palette names."""
        return list(self.palettes.keys())

    def __contains__(self, name: str) -> bool:
        """Check if palette exists."""
        return name in self.palettes

    def __getitem__(self, name: str) -> Palette:
        """Get palette by name."""
        return self.get(name)
