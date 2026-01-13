"""Character sprite generator."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

from sprite_kit.builder.sprite_builder import SpriteBuilder
from sprite_kit.core.color import Color
from sprite_kit.core.palette import Palette, PaletteRegistry
from sprite_kit.core.rng import SeededRNG
from sprite_kit.sprites.base import Sprite, SpriteCategory


class CharacterArchetype(str, Enum):
    """Pre-defined character archetypes."""

    # Player types
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    HEALER = "healer"

    # Kindred Keep companions
    GUARDIAN = "guardian"  # Warden
    MYSTIC = "mystic"  # Oracle

    # NPCs
    VILLAGER = "villager"
    MERCHANT = "merchant"

    # Enemies
    GOBLIN = "goblin"
    SKELETON = "skeleton"
    BRUISER = "bruiser"
    BEAST = "beast"
    BOSS = "boss"


class CharacterStance(str, Enum):
    """Character stance/pose."""

    NEUTRAL = "neutral"
    ACT = "act"
    OBSERVE = "observe"
    PROTECT = "protect"
    SUPPORT = "support"
    ATTACK = "attack"
    HURT = "hurt"


class CharacterSize(str, Enum):
    """Character size category."""

    SMALL = "small"  # 32x40
    MEDIUM = "medium"  # 64x80
    LARGE = "large"  # 96x120
    BOSS = "boss"  # 128x160


# Size dimensions mapping
SIZE_DIMENSIONS: dict[CharacterSize, tuple[int, int]] = {
    CharacterSize.SMALL: (32, 40),
    CharacterSize.MEDIUM: (64, 80),
    CharacterSize.LARGE: (96, 120),
    CharacterSize.BOSS: (128, 160),
}


# Archetype to color mapping
ARCHETYPE_COLORS: dict[CharacterArchetype, str] = {
    CharacterArchetype.WARRIOR: "#8B4513",  # Saddle brown
    CharacterArchetype.MAGE: "#4B0082",  # Indigo
    CharacterArchetype.ROGUE: "#2F4F4F",  # Dark slate gray
    CharacterArchetype.HEALER: "#228B22",  # Forest green
    CharacterArchetype.GUARDIAN: "#5E8B7C",  # Warden teal
    CharacterArchetype.MYSTIC: "#8B7BB8",  # Oracle purple
    CharacterArchetype.VILLAGER: "#A0522D",  # Sienna
    CharacterArchetype.MERCHANT: "#DAA520",  # Goldenrod
    CharacterArchetype.GOBLIN: "#6B8E23",  # Olive drab
    CharacterArchetype.SKELETON: "#F5F5DC",  # Beige
    CharacterArchetype.BRUISER: "#724932",  # Brown
    CharacterArchetype.BEAST: "#4A3A3A",  # Dark brown
    CharacterArchetype.BOSS: "#8B0000",  # Dark red
}


# Stance to effect color mapping
STANCE_COLORS: dict[CharacterStance, str] = {
    CharacterStance.NEUTRAL: "#8A8A8A",
    CharacterStance.ACT: "#D4A055",
    CharacterStance.OBSERVE: "#7B9EB8",
    CharacterStance.PROTECT: "#5E8B7C",
    CharacterStance.SUPPORT: "#B8879B",
    CharacterStance.ATTACK: "#C45C4A",
    CharacterStance.HURT: "#8B3A3A",
}


class CharacterSprite(BaseModel):
    """Generator for character sprites.

    Generates humanoid character sprites with stance variations.

    Example:
        >>> gen = CharacterSprite(archetype=CharacterArchetype.GUARDIAN)
        >>> sprite = gen.generate(CharacterStance.NEUTRAL)
        >>> all_stances = gen.generate_all_stances()
    """

    archetype: CharacterArchetype
    size: CharacterSize = CharacterSize.MEDIUM
    seed: int = 42
    palette: Palette | None = None

    # Archetype to palette name mapping
    ARCHETYPE_PALETTES: ClassVar[dict[CharacterArchetype, str]] = {
        CharacterArchetype.GUARDIAN: "companion",
        CharacterArchetype.MYSTIC: "companion",
    }

    model_config = {"arbitrary_types_allowed": True}

    def get_palette(self) -> Palette:
        """Get the palette for this character."""
        if self.palette:
            return self.palette

        registry = PaletteRegistry.load_default()

        # Check if archetype has a specific palette
        if self.archetype in self.ARCHETYPE_PALETTES:
            return registry.get(self.ARCHETYPE_PALETTES[self.archetype])

        # Use default companion palette
        return registry.get("companion")

    def get_primary_color(self) -> Color:
        """Get the primary color for this archetype."""
        hex_color = ARCHETYPE_COLORS.get(self.archetype, "#808080")
        return Color.from_hex(hex_color)

    def generate(self, stance: CharacterStance = CharacterStance.NEUTRAL) -> Sprite:
        """Generate a character sprite in the given stance.

        Args:
            stance: Character stance

        Returns:
            Generated Sprite
        """
        _rng = SeededRNG(self.seed)  # Reserved for future randomization
        width, height = SIZE_DIMENSIONS[self.size]
        primary = self.get_primary_color()
        secondary = primary.darken(0.2)
        skin = Color.from_hex("#D4B896")
        stance_color = Color.from_hex(STANCE_COLORS.get(stance, "#8A8A8A"))

        # Calculate proportions based on size
        cx = width // 2
        head_y = int(height * 0.25)
        body_y = int(height * 0.35)
        body_h = int(height * 0.35)
        head_r = int(width * 0.18)
        body_w = int(width * 0.35)
        leg_w = int(width * 0.12)
        leg_h = int(height * 0.25)

        name = f"{self.archetype.value}_{stance.value}"
        builder = (
            SpriteBuilder(name, width, height, SpriteCategory.CHARACTER)
            .with_metadata("archetype", self.archetype.value)
            .with_metadata("stance", stance.value)
        )

        # Add glow filter for stance effects
        builder.define_glow_filter("stanceGlow", stance_color.to_hex(), blur=2.0)

        # Stance effect layer (ground circle for act/observe)
        if stance in (CharacterStance.ACT, CharacterStance.OBSERVE):
            effect_y = height - int(height * 0.1)
            effect_r = int(width * 0.25)
            builder.layer("effect").circle(
                cx,
                effect_y,
                effect_r,
                fill=stance_color.with_alpha(0.4),
                filter_id="stanceGlow",
            ).end_layer()

        # Shadow layer
        shadow_y = height - int(height * 0.08)
        shadow_r = int(width * 0.2)
        builder.layer("shadow").circle(cx, shadow_y, shadow_r, fill=Color(0, 0, 0, 0.3)).end_layer()

        # Legs layer
        leg_y = body_y + body_h - 5
        leg_spacing = int(width * 0.08)
        builder.layer("legs").rect(
            cx - leg_spacing - leg_w // 2,
            leg_y,
            leg_w,
            leg_h,
            rx=2,
            fill=secondary,
        ).rect(
            cx + leg_spacing - leg_w // 2,
            leg_y,
            leg_w,
            leg_h,
            rx=2,
            fill=secondary,
        ).end_layer()

        # Body layer
        builder.layer("body").rect(
            cx - body_w // 2, body_y, body_w, body_h, rx=4, fill=primary
        ).end_layer()

        # Arms layer - position varies by stance
        arm_w = int(width * 0.1)
        arm_h = int(height * 0.2)
        arm_y = body_y + 5

        if stance == CharacterStance.PROTECT:
            # Arms forward/up
            builder.layer("arms").rect(
                cx - body_w // 2 - arm_w + 2,
                arm_y - 5,
                arm_w,
                arm_h,
                rx=2,
                fill=skin,
            ).rect(
                cx + body_w // 2 - 2,
                arm_y - 5,
                arm_w,
                arm_h,
                rx=2,
                fill=skin,
            ).end_layer()
        elif stance == CharacterStance.ACT:
            # One arm raised
            builder.layer("arms").rect(
                cx - body_w // 2 - arm_w + 2,
                arm_y,
                arm_w,
                arm_h,
                rx=2,
                fill=skin,
            ).rect(
                cx + body_w // 2 - 2,
                arm_y - 10,  # Raised
                arm_w,
                arm_h,
                rx=2,
                fill=skin,
            ).end_layer()
        else:
            # Normal arms at sides
            builder.layer("arms").rect(
                cx - body_w // 2 - arm_w + 2,
                arm_y,
                arm_w,
                arm_h,
                rx=2,
                fill=skin,
            ).rect(
                cx + body_w // 2 - 2,
                arm_y,
                arm_w,
                arm_h,
                rx=2,
                fill=skin,
            ).end_layer()

        # Head layer
        builder.layer("head").circle(cx, head_y, head_r, fill=skin).end_layer()

        # Face layer
        eye_spacing = int(head_r * 0.4)
        eye_r = max(2, int(head_r * 0.2))
        eye_y = head_y - int(head_r * 0.1)

        builder.layer("face").circle(cx - eye_spacing, eye_y, eye_r, fill=Color(30, 30, 30)).circle(
            cx + eye_spacing, eye_y, eye_r, fill=Color(30, 30, 30)
        ).end_layer()

        # Hurt stance: add damage indicator
        if stance == CharacterStance.HURT:
            builder.layer("damage").circle(
                cx, head_y, head_r + 3, stroke=Color.from_hex("#8B3A3A"), stroke_width=2
            ).end_layer()

        return builder.build()

    def generate_all_stances(self) -> dict[CharacterStance, Sprite]:
        """Generate sprites for all common stances.

        Returns:
            Dict mapping stance to sprite
        """
        stances = [
            CharacterStance.NEUTRAL,
            CharacterStance.ACT,
            CharacterStance.OBSERVE,
            CharacterStance.PROTECT,
            CharacterStance.SUPPORT,
        ]
        return {stance: self.generate(stance) for stance in stances}

    def generate_enemy_stances(self) -> dict[CharacterStance, Sprite]:
        """Generate enemy-appropriate stances.

        Returns:
            Dict mapping stance to sprite
        """
        stances = [
            CharacterStance.NEUTRAL,
            CharacterStance.ATTACK,
            CharacterStance.HURT,
        ]
        return {stance: self.generate(stance) for stance in stances}

    @classmethod
    def from_context(
        cls,
        context: str,
        size: CharacterSize = CharacterSize.MEDIUM,
        seed: int = 42,
    ) -> CharacterSprite:
        """Create from natural language description.

        Args:
            context: Description like "fierce goblin warrior"
            size: Character size
            seed: Random seed

        Returns:
            CharacterSprite instance
        """
        context_lower = context.lower()

        # Map keywords to archetypes
        archetype = CharacterArchetype.WARRIOR  # Default

        keyword_map = {
            "warrior": CharacterArchetype.WARRIOR,
            "fighter": CharacterArchetype.WARRIOR,
            "knight": CharacterArchetype.WARRIOR,
            "mage": CharacterArchetype.MAGE,
            "wizard": CharacterArchetype.MAGE,
            "sorcerer": CharacterArchetype.MAGE,
            "rogue": CharacterArchetype.ROGUE,
            "thief": CharacterArchetype.ROGUE,
            "assassin": CharacterArchetype.ROGUE,
            "healer": CharacterArchetype.HEALER,
            "cleric": CharacterArchetype.HEALER,
            "priest": CharacterArchetype.HEALER,
            "warden": CharacterArchetype.GUARDIAN,
            "guardian": CharacterArchetype.GUARDIAN,
            "oracle": CharacterArchetype.MYSTIC,
            "mystic": CharacterArchetype.MYSTIC,
            "seer": CharacterArchetype.MYSTIC,
            "villager": CharacterArchetype.VILLAGER,
            "peasant": CharacterArchetype.VILLAGER,
            "merchant": CharacterArchetype.MERCHANT,
            "shopkeeper": CharacterArchetype.MERCHANT,
            "goblin": CharacterArchetype.GOBLIN,
            "skeleton": CharacterArchetype.SKELETON,
            "bruiser": CharacterArchetype.BRUISER,
            "beast": CharacterArchetype.BEAST,
            "boss": CharacterArchetype.BOSS,
        }

        for keyword, arch in keyword_map.items():
            if keyword in context_lower:
                archetype = arch
                break

        return cls(archetype=archetype, size=size, seed=seed)
