"""Icon sprite generator."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from sprite_kit.builder.sprite_builder import SpriteBuilder
from sprite_kit.core.color import Color
from sprite_kit.core.palette import Palette, PaletteRegistry
from sprite_kit.core.rng import SeededRNG
from sprite_kit.sprites.base import Sprite, SpriteCategory


class IconCategory(str, Enum):
    """Categories of icons."""

    HEART = "heart"
    STANCE = "stance"
    ELEMENT = "element"
    RITUAL = "ritual"


# Heart state icons
HEART_ICONS = ["calm", "agitated", "hopeful", "bonded", "critical"]

# Stance icons
STANCE_ICONS = ["observe", "act", "complementary", "neutral"]

# Element icons
ELEMENT_ICONS = ["fire", "frost", "lightning", "shadow", "nature", "spirit"]

# Ritual icons
RITUAL_ICONS = ["meditation", "vigil", "bonding", "dream"]


class IconSprite(BaseModel):
    """Generator for UI icons.

    Example:
        >>> gen = IconSprite(category=IconCategory.HEART)
        >>> sprite = gen.generate("calm", size=32)
        >>> all_icons = gen.generate_all(size=32)
    """

    category: IconCategory
    seed: int = 42
    palette: Palette | None = None

    model_config = {"arbitrary_types_allowed": True}

    def get_palette(self) -> Palette:
        """Get the palette for this icon category."""
        if self.palette:
            return self.palette

        registry = PaletteRegistry.load_default()
        palette_map = {
            IconCategory.HEART: "heart",
            IconCategory.STANCE: "stance",
            IconCategory.ELEMENT: "elements",
            IconCategory.RITUAL: "ritual",
        }
        return registry.get(palette_map.get(self.category, "ui"))

    def get_icon_list(self) -> list[str]:
        """Get list of icons in this category."""
        lists = {
            IconCategory.HEART: HEART_ICONS,
            IconCategory.STANCE: STANCE_ICONS,
            IconCategory.ELEMENT: ELEMENT_ICONS,
            IconCategory.RITUAL: RITUAL_ICONS,
        }
        return lists.get(self.category, [])

    def generate(self, icon_type: str, size: int = 32) -> Sprite:
        """Generate an icon sprite.

        Args:
            icon_type: Icon name (e.g., "calm" for heart category)
            size: Icon size in pixels

        Returns:
            Generated Sprite
        """
        palette = self.get_palette()
        color = palette.get(icon_type)
        if color is None:
            color = Color.from_hex("#808080")

        rng = SeededRNG(self.seed)

        if self.category == IconCategory.HEART:
            return self._generate_heart(icon_type, size, color, rng)
        elif self.category == IconCategory.STANCE:
            return self._generate_stance(icon_type, size, color, rng)
        elif self.category == IconCategory.ELEMENT:
            return self._generate_element(icon_type, size, color, rng)
        else:  # RITUAL
            return self._generate_ritual(icon_type, size, color, rng)

    def _generate_heart(self, icon_type: str, size: int, color: Color, rng: SeededRNG) -> Sprite:
        """Generate heart-shaped icon."""
        cx = size // 2
        cy = size // 2
        r = int(size * 0.35)

        builder = (
            SpriteBuilder(f"heart_{icon_type}", size, size, SpriteCategory.ICON)
            .with_metadata("category", "heart")
            .with_metadata("type", icon_type)
        )

        builder.define_glow_filter("heartGlow", color.to_hex(), blur=2.0)

        # Heart shape using two circles and a triangle
        offset = int(r * 0.4)
        builder.layer("heart")

        # Left and right humps
        builder.circle(cx - offset, cy - int(r * 0.2), r, fill=color)
        builder.circle(cx + offset, cy - int(r * 0.2), r, fill=color)

        # Bottom point triangle
        builder.polygon(
            [
                (cx - r - offset + 2, cy),
                (cx + r + offset - 2, cy),
                (cx, cy + int(r * 1.5)),
            ],
            fill=color,
        )

        builder.end_layer()

        # Add highlight
        builder.layer("highlight").circle(
            cx - offset - int(r * 0.3),
            cy - int(r * 0.4),
            int(r * 0.25),
            fill=Color(255, 255, 255, 0.4),
        ).end_layer()

        return builder.build()

    def _generate_stance(self, icon_type: str, size: int, color: Color, rng: SeededRNG) -> Sprite:
        """Generate stance icon."""
        cx = size // 2
        cy = size // 2
        r = int(size * 0.35)

        builder = (
            SpriteBuilder(f"stance_{icon_type}", size, size, SpriteCategory.ICON)
            .with_metadata("category", "stance")
            .with_metadata("type", icon_type)
        )

        builder.define_glow_filter("stanceGlow", color.to_hex(), blur=2.0)

        if icon_type == "observe":
            # Eye shape
            builder.layer("icon")
            builder.circle(cx, cy, r, fill=color)
            builder.circle(cx, cy, int(r * 0.4), fill=Color(255, 255, 255))
            builder.circle(cx, cy, int(r * 0.2), fill=Color(30, 30, 30))
            builder.end_layer()
        elif icon_type == "act":
            # Lightning bolt / action
            builder.layer("icon")
            builder.star(cx, cy, r, int(r * 0.5), points=4, fill=color)
            builder.end_layer()
        elif icon_type == "complementary":
            # Yin-yang style
            builder.layer("icon")
            builder.circle(cx, cy, r, fill=color)
            builder.circle(cx, cy - int(r * 0.4), int(r * 0.3), fill=color.darken(0.3))
            builder.circle(cx, cy + int(r * 0.4), int(r * 0.3), fill=color.lighten(0.3))
            builder.end_layer()
        else:  # neutral
            builder.layer("icon")
            builder.circle(cx, cy, r, fill=color)
            builder.end_layer()

        return builder.build()

    def _generate_element(self, icon_type: str, size: int, color: Color, rng: SeededRNG) -> Sprite:
        """Generate element icon."""
        cx = size // 2
        cy = size // 2
        r = int(size * 0.35)

        builder = (
            SpriteBuilder(f"element_{icon_type}", size, size, SpriteCategory.ICON)
            .with_metadata("category", "element")
            .with_metadata("type", icon_type)
        )

        builder.define_glow_filter("elemGlow", color.to_hex(), blur=2.0)

        if icon_type == "fire":
            # Flame shape
            builder.layer("icon")
            builder.polygon(
                [
                    (cx, cy - r),
                    (cx + int(r * 0.7), cy + r),
                    (cx, cy + int(r * 0.5)),
                    (cx - int(r * 0.7), cy + r),
                ],
                fill=color,
            )
            builder.end_layer()
        elif icon_type == "frost":
            # Snowflake / crystal
            builder.layer("icon")
            builder.star(cx, cy, r, int(r * 0.3), points=6, fill=color)
            builder.end_layer()
        elif icon_type == "lightning":
            # Lightning bolt
            builder.layer("icon")
            builder.polygon(
                [
                    (cx + int(r * 0.3), cy - r),
                    (cx - int(r * 0.2), cy),
                    (cx + int(r * 0.1), cy),
                    (cx - int(r * 0.3), cy + r),
                    (cx + int(r * 0.2), cy - int(r * 0.1)),
                    (cx - int(r * 0.1), cy - int(r * 0.1)),
                ],
                fill=color,
            )
            builder.end_layer()
        elif icon_type == "shadow":
            # Dark circle with gradient
            builder.define_radial_gradient(
                "shadowGrad",
                [color.to_hex(), color.darken(0.5).to_hex()],
            )
            builder.layer("icon").circle(cx, cy, r, fill="url(#shadowGrad)").end_layer()
        elif icon_type == "nature":
            # Leaf shape
            builder.layer("icon")
            builder.circle(cx, cy, r, fill=color)
            builder.circle(cx, cy - int(r * 0.3), int(r * 0.5), fill=color.lighten(0.2))
            builder.end_layer()
        else:  # spirit
            # Ethereal glow
            builder.define_radial_gradient(
                "spiritGrad",
                [
                    color.lighten(0.3).to_hex(),
                    color.to_hex(),
                    color.with_alpha(0).to_rgba(),
                ],
            )
            builder.layer("icon").circle(cx, cy, r, fill="url(#spiritGrad)").end_layer()

        return builder.build()

    def _generate_ritual(self, icon_type: str, size: int, color: Color, rng: SeededRNG) -> Sprite:
        """Generate ritual icon."""
        cx = size // 2
        cy = size // 2
        r = int(size * 0.35)

        builder = (
            SpriteBuilder(f"ritual_{icon_type}", size, size, SpriteCategory.ICON)
            .with_metadata("category", "ritual")
            .with_metadata("type", icon_type)
        )

        builder.define_glow_filter("ritualGlow", color.to_hex(), blur=2.0)

        # Simple geometric shapes for each ritual type
        if icon_type == "meditation":
            # Lotus / sitting pose
            builder.layer("icon")
            builder.circle(cx, cy, r, fill=color)
            builder.circle(cx, cy - int(r * 0.5), int(r * 0.3), fill=color.lighten(0.2))
            builder.end_layer()
        elif icon_type == "vigil":
            # Flame / candle
            builder.layer("icon")
            builder.polygon(
                [
                    (cx, cy - r),
                    (cx + int(r * 0.5), cy + r),
                    (cx - int(r * 0.5), cy + r),
                ],
                fill=color,
            )
            builder.end_layer()
        elif icon_type == "bonding":
            # Two circles connected
            builder.layer("icon")
            builder.circle(cx - int(r * 0.4), cy, int(r * 0.6), fill=color)
            builder.circle(cx + int(r * 0.4), cy, int(r * 0.6), fill=color)
            builder.end_layer()
        else:  # dream
            # Crescent moon
            builder.layer("icon")
            builder.circle(cx, cy, r, fill=color)
            builder.circle(
                cx + int(r * 0.3),
                cy - int(r * 0.2),
                int(r * 0.7),
                fill=Color(30, 30, 40),
            )
            builder.end_layer()

        return builder.build()

    def generate_all(self, size: int = 32) -> dict[str, Sprite]:
        """Generate all icons in the category.

        Args:
            size: Icon size in pixels

        Returns:
            Dict mapping icon name to sprite
        """
        icon_list = self.get_icon_list()
        return {name: self.generate(name, size) for name in icon_list}
