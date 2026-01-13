"""py-sprite-kit: Procedural sprite generation library.

Generate SVG and PNG sprites with semantic agent API
for game development and procedural content generation.

Example:
    >>> from sprite_kit import SpriteAgent, SVGExporter
    >>> agent = SpriteAgent()
    >>> sprite = agent.generate_character("fierce goblin warrior")
    >>> SVGExporter().export_file(sprite, "goblin.svg")
"""

from sprite_kit.agent.sprite_agent import SpriteAgent
from sprite_kit.builder.sprite_builder import SpriteBuilder
from sprite_kit.core.color import Color, color_scale
from sprite_kit.core.palette import Palette, PaletteRegistry
from sprite_kit.core.rng import SeededRNG
from sprite_kit.core.shape import (
    Circle,
    Path,
    PathBuilder,
    Point,
    Polygon,
    Rect,
    Rectangle,
)
from sprite_kit.output.png import (
    PixelStyle,
    PNGExporter,
    create_gif,
    create_spritesheet_png,
)
from sprite_kit.output.svg import (
    SVGExporter,
    create_drop_shadow_filter,
    create_glow_filter,
    create_gradient,
    create_radial_gradient,
)
from sprite_kit.sprites.base import (
    Animation,
    AnimationFrame,
    Layer,
    Sprite,
    SpriteCategory,
    SpriteSheet,
)
from sprite_kit.sprites.character import (
    CharacterArchetype,
    CharacterSize,
    CharacterSprite,
    CharacterStance,
)
from sprite_kit.sprites.effect import EffectSprite, EffectType
from sprite_kit.sprites.icon import IconCategory, IconSprite

__version__ = "0.1.0"

__all__ = [
    # Core
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
    "PathBuilder",
    # Sprites
    "Sprite",
    "Layer",
    "Animation",
    "AnimationFrame",
    "SpriteSheet",
    "SpriteCategory",
    # Builder
    "SpriteBuilder",
    # Generators
    "CharacterSprite",
    "CharacterArchetype",
    "CharacterStance",
    "CharacterSize",
    "EffectSprite",
    "EffectType",
    "IconSprite",
    "IconCategory",
    # Output - SVG
    "SVGExporter",
    "create_gradient",
    "create_radial_gradient",
    "create_glow_filter",
    "create_drop_shadow_filter",
    # Output - PNG
    "PNGExporter",
    "PixelStyle",
    "create_gif",
    "create_spritesheet_png",
    # Agent
    "SpriteAgent",
]
