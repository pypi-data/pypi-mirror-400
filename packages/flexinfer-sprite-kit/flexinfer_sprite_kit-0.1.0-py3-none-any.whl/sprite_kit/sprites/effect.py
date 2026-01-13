"""Visual effect sprite generator."""

from __future__ import annotations

import math
from enum import Enum

from pydantic import BaseModel

from sprite_kit.builder.sprite_builder import SpriteBuilder
from sprite_kit.core.color import Color
from sprite_kit.core.palette import Palette, PaletteRegistry
from sprite_kit.core.rng import SeededRNG
from sprite_kit.core.shape import Point
from sprite_kit.sprites.base import Sprite, SpriteCategory


class EffectType(str, Enum):
    """Types of visual effects."""

    AURA = "aura"
    PULSE = "pulse"
    SPARKLE = "sparkle"
    IMPACT = "impact"
    GLOW = "glow"
    PARTICLES = "particles"


# Effect type to default palette color
EFFECT_PALETTE_KEYS: dict[EffectType, tuple[str, str]] = {
    EffectType.AURA: ("companion", "warden"),
    EffectType.PULSE: ("heart", "calm"),
    EffectType.SPARKLE: ("stance", "act"),
    EffectType.IMPACT: ("heart", "agitated"),
    EffectType.GLOW: ("ui", "accent"),
    EffectType.PARTICLES: ("elements", "spirit"),
}


class EffectSprite(BaseModel):
    """Generator for visual effect sprites.

    Example:
        >>> gen = EffectSprite(effect_type=EffectType.AURA)
        >>> sprite = gen.generate(Point(32, 32), size=40)
    """

    effect_type: EffectType
    intensity: float = 0.5  # 0.0-1.0
    seed: int = 42
    palette: Palette | None = None
    color_override: Color | None = None

    model_config = {"arbitrary_types_allowed": True}

    def get_color(self) -> Color:
        """Get the effect color."""
        if self.color_override:
            return self.color_override

        if self.palette:
            # Try to get appropriate color from palette
            for key in self.palette.keys():
                return self.palette[key]

        # Use default from effect type
        palette_name, color_key = EFFECT_PALETTE_KEYS.get(self.effect_type, ("ui", "accent"))
        registry = PaletteRegistry.load_default()
        return registry.get(palette_name)[color_key]

    def generate(
        self,
        center: Point | None = None,
        size: float = 32.0,
        sprite_size: int = 64,
    ) -> Sprite:
        """Generate an effect sprite.

        Args:
            center: Center point (defaults to sprite center)
            size: Effect size/radius
            sprite_size: Output sprite dimensions

        Returns:
            Generated Sprite
        """
        if center is None:
            center = Point(sprite_size / 2, sprite_size / 2)

        rng = SeededRNG(self.seed)
        color = self.get_color()

        if self.effect_type == EffectType.AURA:
            return self._generate_aura(center, size, sprite_size, color, rng)
        elif self.effect_type == EffectType.PULSE:
            return self._generate_pulse(center, size, sprite_size, color, rng)
        elif self.effect_type == EffectType.SPARKLE:
            return self._generate_sparkle(center, size, sprite_size, color, rng)
        elif self.effect_type == EffectType.IMPACT:
            return self._generate_impact(center, size, sprite_size, color, rng)
        elif self.effect_type == EffectType.GLOW:
            return self._generate_glow(center, size, sprite_size, color, rng)
        else:  # PARTICLES
            return self._generate_particles(center, size, sprite_size, color, rng)

    def _generate_aura(
        self,
        center: Point,
        size: float,
        sprite_size: int,
        color: Color,
        rng: SeededRNG,
    ) -> Sprite:
        """Generate aura effect."""
        builder = SpriteBuilder(
            f"aura_{self.seed}", sprite_size, sprite_size, SpriteCategory.EFFECT
        )
        builder.define_glow_filter("auraGlow", color.to_hex(), blur=4.0)
        builder.define_radial_gradient(
            "auraGrad",
            [color.with_alpha(0.6).to_rgba(), color.with_alpha(0).to_rgba()],
        )

        # Outer glow
        builder.layer("glow").circle(center.x, center.y, size, fill="url(#auraGrad)").end_layer()

        # Inner core
        core_size = size * 0.4 * self.intensity
        builder.layer("core").circle(
            center.x, center.y, core_size, fill=color.with_alpha(0.5)
        ).end_layer()

        return builder.build()

    def _generate_pulse(
        self,
        center: Point,
        size: float,
        sprite_size: int,
        color: Color,
        rng: SeededRNG,
    ) -> Sprite:
        """Generate pulse ring effect."""
        builder = SpriteBuilder(
            f"pulse_{self.seed}", sprite_size, sprite_size, SpriteCategory.EFFECT
        )

        ring_count = 3
        for i in range(ring_count):
            opacity = 0.6 - (i * 0.2)
            ring_size = size * (0.5 + i * 0.25)
            builder.layer(f"ring_{i}").circle(
                center.x,
                center.y,
                ring_size,
                stroke=color.with_alpha(opacity),
                stroke_width=2,
            ).end_layer()

        return builder.build()

    def _generate_sparkle(
        self,
        center: Point,
        size: float,
        sprite_size: int,
        color: Color,
        rng: SeededRNG,
    ) -> Sprite:
        """Generate sparkle effect."""
        builder = SpriteBuilder(
            f"sparkle_{self.seed}", sprite_size, sprite_size, SpriteCategory.EFFECT
        )
        builder.define_glow_filter("sparkleGlow", color.to_hex(), blur=2.0)

        builder.layer("sparkles")
        count = int(5 + self.intensity * 10)
        for _ in range(count):
            angle = rng.uniform(0, 2 * math.pi)
            dist = rng.uniform(size * 0.2, size)
            x = center.x + dist * math.cos(angle)
            y = center.y + dist * math.sin(angle)
            r = rng.uniform(1, 3) * self.intensity
            opacity = rng.uniform(0.4, 0.9)
            builder.circle(x, y, r, fill=color.with_alpha(opacity))

        builder.end_layer()
        return builder.build()

    def _generate_impact(
        self,
        center: Point,
        size: float,
        sprite_size: int,
        color: Color,
        rng: SeededRNG,
    ) -> Sprite:
        """Generate impact burst effect."""
        builder = SpriteBuilder(
            f"impact_{self.seed}", sprite_size, sprite_size, SpriteCategory.EFFECT
        )
        builder.define_glow_filter("impactGlow", color.to_hex(), blur=3.0)

        # Star burst
        builder.layer("burst")
        builder.star(
            center.x,
            center.y,
            outer_r=size,
            inner_r=size * 0.4,
            points=8,
            fill=color.with_alpha(0.7),
        )
        builder.end_layer()

        # Core
        builder.layer("core").circle(
            center.x, center.y, size * 0.3, fill=color.lighten(0.3)
        ).end_layer()

        return builder.build()

    def _generate_glow(
        self,
        center: Point,
        size: float,
        sprite_size: int,
        color: Color,
        rng: SeededRNG,
    ) -> Sprite:
        """Generate simple glow effect."""
        builder = SpriteBuilder(
            f"glow_{self.seed}", sprite_size, sprite_size, SpriteCategory.EFFECT
        )
        builder.define_radial_gradient(
            "glowGrad",
            [
                color.with_alpha(0.8).to_rgba(),
                color.with_alpha(0.3).to_rgba(),
                color.with_alpha(0).to_rgba(),
            ],
        )

        builder.layer("glow").circle(center.x, center.y, size, fill="url(#glowGrad)").end_layer()

        return builder.build()

    def _generate_particles(
        self,
        center: Point,
        size: float,
        sprite_size: int,
        color: Color,
        rng: SeededRNG,
    ) -> Sprite:
        """Generate particle cloud effect."""
        builder = SpriteBuilder(
            f"particles_{self.seed}", sprite_size, sprite_size, SpriteCategory.EFFECT
        )

        builder.layer("particles")
        count = int(8 + self.intensity * 12)
        for _ in range(count):
            angle = rng.uniform(0, 2 * math.pi)
            dist = rng.uniform(0, size)
            x = center.x + dist * math.cos(angle)
            y = center.y + dist * math.sin(angle)
            r = rng.uniform(1, 4)
            opacity = rng.uniform(0.3, 0.7)
            # Vary color slightly
            varied = color.lerp(color.lighten(0.3), rng.uniform(0, 0.5))
            builder.circle(x, y, r, fill=varied.with_alpha(opacity))

        builder.end_layer()
        return builder.build()

    @classmethod
    def from_context(
        cls,
        context: str,
        intensity: float = 0.5,
        seed: int = 42,
    ) -> EffectSprite:
        """Create from natural language description.

        Args:
            context: Description like "magical aura" or "sparkle effect"
            intensity: Effect intensity
            seed: Random seed

        Returns:
            EffectSprite instance
        """
        context_lower = context.lower()

        effect_type = EffectType.GLOW  # Default

        keyword_map = {
            "aura": EffectType.AURA,
            "pulse": EffectType.PULSE,
            "ring": EffectType.PULSE,
            "sparkle": EffectType.SPARKLE,
            "star": EffectType.SPARKLE,
            "impact": EffectType.IMPACT,
            "hit": EffectType.IMPACT,
            "burst": EffectType.IMPACT,
            "glow": EffectType.GLOW,
            "light": EffectType.GLOW,
            "particle": EffectType.PARTICLES,
            "dust": EffectType.PARTICLES,
            "cloud": EffectType.PARTICLES,
        }

        for keyword, etype in keyword_map.items():
            if keyword in context_lower:
                effect_type = etype
                break

        return cls(effect_type=effect_type, intensity=intensity, seed=seed)
