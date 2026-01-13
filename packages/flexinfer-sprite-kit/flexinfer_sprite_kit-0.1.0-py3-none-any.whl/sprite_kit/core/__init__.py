"""Core primitives for sprite generation."""

from sprite_kit.core.color import Color, color_scale
from sprite_kit.core.palette import Palette, PaletteRegistry
from sprite_kit.core.rng import SeededRNG
from sprite_kit.core.shape import Circle, Path, Point, Polygon, Rect, Rectangle

__all__ = [
    "Color",
    "color_scale",
    "Palette",
    "PaletteRegistry",
    "SeededRNG",
    "Point",
    "Rect",
    "Circle",
    "Rectangle",
    "Polygon",
    "Path",
]
