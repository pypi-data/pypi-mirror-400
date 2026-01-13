"""Semantic API for AI agents to generate sprites.

Provides a high-level, natural language-inspired interface
for sprite generation without requiring art knowledge.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from sprite_kit.core.color import Color
from sprite_kit.core.shape import Point
from sprite_kit.sprites.base import Sprite
from sprite_kit.sprites.character import (
    CharacterArchetype,
    CharacterSize,
    CharacterSprite,
    CharacterStance,
)
from sprite_kit.sprites.effect import EffectSprite, EffectType
from sprite_kit.sprites.icon import IconCategory, IconSprite


class SpriteAgent(BaseModel):
    """Semantic interface for AI agents to generate sprites.

    Designed for agents that don't have art knowledge but need
    to generate context-appropriate game sprites.

    Example:
        ```python
        agent = SpriteAgent()

        # Generate from context description
        sprite = agent.generate_for_context(
            "fierce goblin warrior preparing to attack"
        )

        # Generate specific sprite types
        character = agent.generate_character("mysterious guardian")
        effect = agent.generate_effect("magical healing aura")
        icon = agent.generate_icon("heart health indicator")
        ```
    """

    seed: int = 42

    # Context keywords to character archetype mapping
    ARCHETYPE_KEYWORDS: ClassVar[dict[str, CharacterArchetype]] = {
        # Warrior types
        "warrior": CharacterArchetype.WARRIOR,
        "fighter": CharacterArchetype.WARRIOR,
        "soldier": CharacterArchetype.WARRIOR,
        "knight": CharacterArchetype.WARRIOR,
        "barbarian": CharacterArchetype.WARRIOR,
        # Mage types
        "mage": CharacterArchetype.MAGE,
        "wizard": CharacterArchetype.MAGE,
        "sorcerer": CharacterArchetype.MAGE,
        "witch": CharacterArchetype.MAGE,
        "magic": CharacterArchetype.MAGE,
        "arcane": CharacterArchetype.MAGE,
        # Rogue types
        "rogue": CharacterArchetype.ROGUE,
        "thief": CharacterArchetype.ROGUE,
        "assassin": CharacterArchetype.ROGUE,
        "ninja": CharacterArchetype.ROGUE,
        "shadow": CharacterArchetype.ROGUE,
        # Healer types
        "healer": CharacterArchetype.HEALER,
        "priest": CharacterArchetype.HEALER,
        "cleric": CharacterArchetype.HEALER,
        "medic": CharacterArchetype.HEALER,
        # Guardian types
        "guardian": CharacterArchetype.GUARDIAN,
        "warden": CharacterArchetype.GUARDIAN,
        "protector": CharacterArchetype.GUARDIAN,
        "defender": CharacterArchetype.GUARDIAN,
        "paladin": CharacterArchetype.GUARDIAN,
        # Mystic types
        "mystic": CharacterArchetype.MYSTIC,
        "oracle": CharacterArchetype.MYSTIC,
        "seer": CharacterArchetype.MYSTIC,
        "prophet": CharacterArchetype.MYSTIC,
        "shaman": CharacterArchetype.MYSTIC,
        # Villager types
        "villager": CharacterArchetype.VILLAGER,
        "peasant": CharacterArchetype.VILLAGER,
        "farmer": CharacterArchetype.VILLAGER,
        "citizen": CharacterArchetype.VILLAGER,
        # Merchant types
        "merchant": CharacterArchetype.MERCHANT,
        "trader": CharacterArchetype.MERCHANT,
        "shopkeeper": CharacterArchetype.MERCHANT,
        "vendor": CharacterArchetype.MERCHANT,
        # Goblin types
        "goblin": CharacterArchetype.GOBLIN,
        "imp": CharacterArchetype.GOBLIN,
        "gremlin": CharacterArchetype.GOBLIN,
        # Skeleton types
        "skeleton": CharacterArchetype.SKELETON,
        "undead": CharacterArchetype.SKELETON,
        "bone": CharacterArchetype.SKELETON,
        # Bruiser types
        "bruiser": CharacterArchetype.BRUISER,
        "brute": CharacterArchetype.BRUISER,
        "ogre": CharacterArchetype.BRUISER,
        "troll": CharacterArchetype.BRUISER,
    }

    # Context keywords to stance mapping
    STANCE_KEYWORDS: ClassVar[dict[str, CharacterStance]] = {
        # Neutral
        "neutral": CharacterStance.NEUTRAL,
        "idle": CharacterStance.NEUTRAL,
        "standing": CharacterStance.NEUTRAL,
        "relaxed": CharacterStance.NEUTRAL,
        # Act
        "act": CharacterStance.ACT,
        "attack": CharacterStance.ACT,
        "action": CharacterStance.ACT,
        "striking": CharacterStance.ACT,
        "fighting": CharacterStance.ACT,
        "combat": CharacterStance.ACT,
        "aggressive": CharacterStance.ACT,
        # Observe
        "observe": CharacterStance.OBSERVE,
        "watching": CharacterStance.OBSERVE,
        "looking": CharacterStance.OBSERVE,
        "alert": CharacterStance.OBSERVE,
        "aware": CharacterStance.OBSERVE,
        "searching": CharacterStance.OBSERVE,
        # Protect
        "protect": CharacterStance.PROTECT,
        "defending": CharacterStance.PROTECT,
        "shielding": CharacterStance.PROTECT,
        "guarding": CharacterStance.PROTECT,
        "blocking": CharacterStance.PROTECT,
        # Support
        "support": CharacterStance.SUPPORT,
        "healing": CharacterStance.SUPPORT,
        "helping": CharacterStance.SUPPORT,
        "blessing": CharacterStance.SUPPORT,
        "aiding": CharacterStance.SUPPORT,
    }

    # Context keywords to effect type mapping
    EFFECT_KEYWORDS: ClassVar[dict[str, EffectType]] = {
        # Aura
        "aura": EffectType.AURA,
        "field": EffectType.AURA,
        "ambient": EffectType.AURA,
        "surrounding": EffectType.AURA,
        # Pulse
        "pulse": EffectType.PULSE,
        "wave": EffectType.PULSE,
        "ring": EffectType.PULSE,
        "ripple": EffectType.PULSE,
        # Sparkle
        "sparkle": EffectType.SPARKLE,
        "star": EffectType.SPARKLE,
        "twinkle": EffectType.SPARKLE,
        "shimmer": EffectType.SPARKLE,
        "glitter": EffectType.SPARKLE,
        # Impact
        "impact": EffectType.IMPACT,
        "hit": EffectType.IMPACT,
        "explosion": EffectType.IMPACT,
        "burst": EffectType.IMPACT,
        "strike": EffectType.IMPACT,
        # Glow
        "glow": EffectType.GLOW,
        "light": EffectType.GLOW,
        "radiance": EffectType.GLOW,
        "shine": EffectType.GLOW,
        # Particles
        "particle": EffectType.PARTICLES,
        "dust": EffectType.PARTICLES,
        "cloud": EffectType.PARTICLES,
        "mist": EffectType.PARTICLES,
        "smoke": EffectType.PARTICLES,
    }

    # Context keywords to icon category mapping
    ICON_KEYWORDS: ClassVar[dict[str, tuple[IconCategory, str]]] = {
        # Heart icons
        "heart": (IconCategory.HEART, "calm"),
        "health": (IconCategory.HEART, "calm"),
        "love": (IconCategory.HEART, "bonded"),
        "life": (IconCategory.HEART, "calm"),
        "calm": (IconCategory.HEART, "calm"),
        "agitated": (IconCategory.HEART, "agitated"),
        "hopeful": (IconCategory.HEART, "hopeful"),
        "bonded": (IconCategory.HEART, "bonded"),
        "critical": (IconCategory.HEART, "critical"),
        # Stance icons
        "observe": (IconCategory.STANCE, "observe"),
        "eye": (IconCategory.STANCE, "observe"),
        "watch": (IconCategory.STANCE, "observe"),
        "complementary": (IconCategory.STANCE, "complementary"),
        # Element icons
        "fire": (IconCategory.ELEMENT, "fire"),
        "flame": (IconCategory.ELEMENT, "fire"),
        "frost": (IconCategory.ELEMENT, "frost"),
        "ice": (IconCategory.ELEMENT, "frost"),
        "lightning": (IconCategory.ELEMENT, "lightning"),
        "thunder": (IconCategory.ELEMENT, "lightning"),
        "shadow": (IconCategory.ELEMENT, "shadow"),
        "dark": (IconCategory.ELEMENT, "shadow"),
        "nature": (IconCategory.ELEMENT, "nature"),
        "plant": (IconCategory.ELEMENT, "nature"),
        "spirit": (IconCategory.ELEMENT, "spirit"),
        "soul": (IconCategory.ELEMENT, "spirit"),
        # Ritual icons
        "meditation": (IconCategory.RITUAL, "meditation"),
        "meditate": (IconCategory.RITUAL, "meditation"),
        "vigil": (IconCategory.RITUAL, "vigil"),
        "candle": (IconCategory.RITUAL, "vigil"),
        "bonding": (IconCategory.RITUAL, "bonding"),
        "dream": (IconCategory.RITUAL, "dream"),
        "moon": (IconCategory.RITUAL, "dream"),
    }

    # Intensity keywords
    INTENSITY_KEYWORDS: ClassVar[dict[str, float]] = {
        "subtle": 0.2,
        "gentle": 0.3,
        "soft": 0.3,
        "faint": 0.2,
        "mild": 0.4,
        "moderate": 0.5,
        "normal": 0.5,
        "strong": 0.7,
        "intense": 0.8,
        "powerful": 0.9,
        "fierce": 0.9,
        "blazing": 1.0,
        "overwhelming": 1.0,
    }

    # Color keywords
    COLOR_KEYWORDS: ClassVar[dict[str, Color]] = {
        "red": Color(220, 60, 60),
        "blue": Color(60, 120, 220),
        "green": Color(60, 180, 80),
        "yellow": Color(240, 200, 60),
        "orange": Color(240, 140, 40),
        "purple": Color(160, 80, 200),
        "pink": Color(240, 140, 180),
        "white": Color(240, 240, 240),
        "black": Color(30, 30, 30),
        "gold": Color(255, 215, 0),
        "silver": Color(192, 192, 192),
        "crimson": Color(180, 30, 30),
        "azure": Color(40, 160, 220),
        "emerald": Color(40, 180, 100),
    }

    def generate_for_context(
        self,
        context: str,
        sprite_type: str = "auto",
        size: int = 64,
    ) -> Sprite:
        """Generate a sprite appropriate for a game context.

        Parses the context description to determine appropriate
        sprite type, style, and colors.

        Args:
            context: Natural language description of what's needed
                (e.g., "fierce goblin warrior", "healing magic effect")
            sprite_type: "character", "effect", "icon", or "auto"
            size: Sprite size in pixels

        Returns:
            Generated Sprite
        """
        context_lower = context.lower()

        # Determine sprite type if auto
        if sprite_type == "auto":
            sprite_type = self._detect_sprite_type(context_lower)

        if sprite_type == "character":
            return self.generate_character(context, size)
        elif sprite_type == "effect":
            return self.generate_effect(context, size)
        elif sprite_type == "icon":
            return self.generate_icon(context, size)
        else:
            # Default to character
            return self.generate_character(context, size)

    def _detect_sprite_type(self, context: str) -> str:
        """Detect sprite type from context keywords."""
        # Effect indicators
        effect_hints = [
            "effect",
            "aura",
            "glow",
            "sparkle",
            "particle",
            "pulse",
            "burst",
            "impact",
            "magic",
            "spell",
        ]
        for hint in effect_hints:
            if hint in context:
                return "effect"

        # Icon indicators
        icon_hints = [
            "icon",
            "heart",
            "element",
            "ritual",
            "indicator",
            "ui",
            "button",
        ]
        for hint in icon_hints:
            if hint in context:
                return "icon"

        # Default to character
        return "character"

    def generate_character(
        self,
        context: str,
        size: int = 64,
    ) -> Sprite:
        """Generate a character sprite from context.

        Args:
            context: Description of the character
            size: Base size hint (used to determine CharacterSize)

        Returns:
            Generated character Sprite
        """
        context_lower = context.lower()

        # Determine archetype
        archetype = self._analyze_archetype(context_lower)

        # Determine stance
        stance = self._analyze_stance(context_lower)

        # Determine size category from context or size hint
        char_size = self._analyze_character_size(context_lower)
        if char_size == CharacterSize.MEDIUM:
            # Override based on size hint if no explicit size in context
            if size <= 40:
                char_size = CharacterSize.SMALL
            elif size >= 96:
                char_size = CharacterSize.LARGE

        # Create generator and generate
        generator = CharacterSprite(
            archetype=archetype,
            size=char_size,
            seed=self.seed,
        )

        return generator.generate(stance=stance)

    def _analyze_archetype(self, context: str) -> CharacterArchetype:
        """Analyze context to determine character archetype."""
        for keyword, archetype in self.ARCHETYPE_KEYWORDS.items():
            if keyword in context:
                return archetype
        return CharacterArchetype.WARRIOR  # Default

    def _analyze_stance(self, context: str) -> CharacterStance:
        """Analyze context to determine character stance."""
        for keyword, stance in self.STANCE_KEYWORDS.items():
            if keyword in context:
                return stance
        return CharacterStance.NEUTRAL  # Default

    def _analyze_character_size(self, context: str) -> CharacterSize:
        """Analyze context to determine character size."""
        if any(w in context for w in ["small", "tiny", "little", "mini"]):
            return CharacterSize.SMALL
        if any(w in context for w in ["large", "big", "huge", "giant"]):
            return CharacterSize.LARGE
        return CharacterSize.MEDIUM

    def generate_effect(
        self,
        context: str,
        size: int = 64,
        effect_size: float | None = None,
    ) -> Sprite:
        """Generate an effect sprite from context.

        Args:
            context: Description of the effect
            size: Sprite size in pixels
            effect_size: Optional effect radius (defaults to size * 0.4)

        Returns:
            Generated effect Sprite
        """
        context_lower = context.lower()

        # Determine effect type
        effect_type = self._analyze_effect_type(context_lower)

        # Determine intensity
        intensity = self._analyze_intensity(context_lower)

        # Determine color override
        color_override = self._analyze_color(context_lower)

        # Calculate effect size
        eff_size = effect_size if effect_size else size * 0.4

        # Create generator and generate
        generator = EffectSprite(
            effect_type=effect_type,
            intensity=intensity,
            seed=self.seed,
            color_override=color_override,
        )

        return generator.generate(
            center=Point(size / 2, size / 2),
            size=eff_size,
            sprite_size=size,
        )

    def _analyze_effect_type(self, context: str) -> EffectType:
        """Analyze context to determine effect type."""
        for keyword, effect_type in self.EFFECT_KEYWORDS.items():
            if keyword in context:
                return effect_type
        return EffectType.GLOW  # Default

    def _analyze_intensity(self, context: str) -> float:
        """Analyze context to determine effect intensity."""
        for keyword, intensity in self.INTENSITY_KEYWORDS.items():
            if keyword in context:
                return intensity
        return 0.5  # Default

    def _analyze_color(self, context: str) -> Color | None:
        """Analyze context to extract color."""
        for keyword, color in self.COLOR_KEYWORDS.items():
            if keyword in context:
                return color
        return None

    def generate_icon(
        self,
        context: str,
        size: int = 32,
    ) -> Sprite:
        """Generate an icon sprite from context.

        Args:
            context: Description of the icon
            size: Icon size in pixels

        Returns:
            Generated icon Sprite
        """
        context_lower = context.lower()

        # Determine icon category and type
        category, icon_type = self._analyze_icon(context_lower)

        # Create generator and generate
        generator = IconSprite(
            category=category,
            seed=self.seed,
        )

        return generator.generate(icon_type, size)

    def _analyze_icon(self, context: str) -> tuple[IconCategory, str]:
        """Analyze context to determine icon category and type."""
        for keyword, (category, icon_type) in self.ICON_KEYWORDS.items():
            if keyword in context:
                return category, icon_type
        return IconCategory.HEART, "calm"  # Default

    def generate_all_stances(
        self,
        archetype: str | CharacterArchetype,
        size: CharacterSize = CharacterSize.MEDIUM,
    ) -> dict[str, Sprite]:
        """Generate all stance variations for a character archetype.

        Args:
            archetype: Character archetype name or enum
            size: Character size category

        Returns:
            Dict mapping stance name to sprite
        """
        if isinstance(archetype, str):
            archetype_lower = archetype.lower()
            arch = self.ARCHETYPE_KEYWORDS.get(archetype_lower, CharacterArchetype.WARRIOR)
        else:
            arch = archetype

        generator = CharacterSprite(
            archetype=arch,
            size=size,
            seed=self.seed,
        )

        # Returns dict[CharacterStance, Sprite], convert keys to strings
        stance_sprites = generator.generate_all_stances()
        return {stance.value: sprite for stance, sprite in stance_sprites.items()}

    def generate_effect_sequence(
        self,
        effect_type: str | EffectType,
        frame_count: int = 4,
        size: int = 64,
    ) -> list[Sprite]:
        """Generate a sequence of effect sprites for animation.

        Args:
            effect_type: Effect type name or enum
            frame_count: Number of frames
            size: Sprite size

        Returns:
            List of sprites representing animation frames
        """
        if isinstance(effect_type, str):
            eff_type = self.EFFECT_KEYWORDS.get(effect_type.lower(), EffectType.GLOW)
        else:
            eff_type = effect_type

        sprites = []
        for i in range(frame_count):
            # Vary intensity across frames for animation
            intensity = 0.3 + (0.7 * (i / max(1, frame_count - 1)))

            generator = EffectSprite(
                effect_type=eff_type,
                intensity=intensity,
                seed=self.seed + i,
            )

            sprite = generator.generate(
                center=Point(size / 2, size / 2),
                size=size * 0.4,
                sprite_size=size,
            )
            sprites.append(sprite)

        return sprites

    def generate_icon_set(
        self,
        category: str | IconCategory,
        size: int = 32,
    ) -> dict[str, Sprite]:
        """Generate all icons in a category.

        Args:
            category: Icon category name or enum
            size: Icon size

        Returns:
            Dict mapping icon name to sprite
        """
        if isinstance(category, str):
            cat_lower = category.lower()
            cat_map = {
                "heart": IconCategory.HEART,
                "stance": IconCategory.STANCE,
                "element": IconCategory.ELEMENT,
                "ritual": IconCategory.RITUAL,
            }
            cat = cat_map.get(cat_lower, IconCategory.HEART)
        else:
            cat = category

        generator = IconSprite(
            category=cat,
            seed=self.seed,
        )

        return generator.generate_all(size)

    @classmethod
    def list_archetypes(cls) -> list[str]:
        """List available character archetypes."""
        return [a.value for a in CharacterArchetype]

    @classmethod
    def list_stances(cls) -> list[str]:
        """List available character stances."""
        return [s.value for s in CharacterStance]

    @classmethod
    def list_effect_types(cls) -> list[str]:
        """List available effect types."""
        return [e.value for e in EffectType]

    @classmethod
    def list_icon_categories(cls) -> list[str]:
        """List available icon categories."""
        return [c.value for c in IconCategory]
