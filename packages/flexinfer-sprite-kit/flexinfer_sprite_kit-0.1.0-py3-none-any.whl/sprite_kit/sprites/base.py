"""Base sprite classes for sprite generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel

from sprite_kit.core.shape import Rect, Shape


class SpriteCategory(str, Enum):
    """Categories of sprites."""

    CHARACTER = "character"
    TILE = "tile"
    EFFECT = "effect"
    PARTICLE = "particle"
    ICON = "icon"
    PROP = "prop"


@dataclass
class Layer:
    """A layer within a sprite containing shapes.

    Layers are rendered in order, with later layers on top.

    Example:
        >>> layer = Layer(name="body")
        >>> layer.add_shape(Circle(cx=32, cy=32, r=16, fill=Color.from_hex("#FF0000")))
    """

    name: str
    shapes: list[Shape] = field(default_factory=list)
    opacity: float = 1.0
    visible: bool = True

    def add_shape(self, shape: Shape) -> None:
        """Add a shape to the layer.

        Args:
            shape: Shape to add
        """
        self.shapes.append(shape)

    def bounds(self) -> Rect:
        """Get combined bounds of all shapes.

        Returns:
            Bounding rect, or empty rect if no shapes
        """
        if not self.shapes:
            return Rect(0, 0, 0, 0)

        all_bounds = [s.bounds() for s in self.shapes]
        min_x = min(b.x for b in all_bounds)
        min_y = min(b.y for b in all_bounds)
        max_x = max(b.x + b.width for b in all_bounds)
        max_y = max(b.y + b.height for b in all_bounds)

        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def to_svg(self) -> str:
        """Render layer as SVG group.

        Returns:
            SVG g element with all shapes
        """
        if not self.visible or not self.shapes:
            return ""

        attrs = [f'id="{self.name}"']
        if self.opacity < 1.0:
            attrs.append(f'opacity="{self.opacity}"')

        shapes_svg = "\n    ".join(s.to_svg() for s in self.shapes)
        return f"<g {' '.join(attrs)}>\n    {shapes_svg}\n  </g>"


class Sprite(BaseModel):
    """Base sprite class containing layers of shapes.

    A sprite is a collection of named layers, each containing shapes.
    Sprites can be exported to SVG or PNG.

    Example:
        >>> sprite = Sprite(name="goblin", width=64, height=80)
        >>> layer = Layer(name="body")
        >>> layer.add_shape(Circle(cx=32, cy=40, r=20))
        >>> sprite.add_layer(layer)
        >>> svg = sprite.to_svg()
    """

    name: str
    category: SpriteCategory = SpriteCategory.CHARACTER
    width: int = 64
    height: int = 64
    layers: list[Layer] = []
    metadata: dict[str, str] = {}
    defs: list[str] = []  # SVG defs (gradients, filters, etc.)
    palette: Any = None  # Palette instance, kept as Any to avoid circular imports

    model_config = {"arbitrary_types_allowed": True}

    def add_layer(self, layer: Layer) -> None:
        """Add a layer to the sprite.

        Args:
            layer: Layer to add
        """
        self.layers.append(layer)

    def get_layer(self, name: str) -> Layer | None:
        """Get layer by name.

        Args:
            name: Layer name

        Returns:
            Layer or None if not found
        """
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None

    def insert_layer(self, index: int, layer: Layer) -> None:
        """Insert layer at specific index.

        Args:
            index: Position to insert at
            layer: Layer to insert
        """
        self.layers.insert(index, layer)

    def remove_layer(self, name: str) -> bool:
        """Remove layer by name.

        Args:
            name: Layer name

        Returns:
            True if removed, False if not found
        """
        for i, layer in enumerate(self.layers):
            if layer.name == name:
                self.layers.pop(i)
                return True
        return False

    def bounds(self) -> Rect:
        """Get combined bounds of all layers.

        Returns:
            Bounding rect
        """
        if not self.layers:
            return Rect(0, 0, self.width, self.height)

        all_bounds = [layer.bounds() for layer in self.layers if layer.visible]
        if not all_bounds:
            return Rect(0, 0, self.width, self.height)

        min_x = min(b.x for b in all_bounds)
        min_y = min(b.y for b in all_bounds)
        max_x = max(b.x + b.width for b in all_bounds)
        max_y = max(b.y + b.height for b in all_bounds)

        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def add_def(self, definition: str) -> None:
        """Add an SVG definition (gradient, filter, etc.).

        Args:
            definition: SVG definition element
        """
        self.defs.append(definition)

    def to_svg(self) -> str:
        """Render sprite as complete SVG document.

        Returns:
            SVG string
        """
        # Build defs section
        defs_content = ""
        if self.defs:
            defs_inner = "\n    ".join(self.defs)
            defs_content = f"  <defs>\n    {defs_inner}\n  </defs>\n"

        # Build layers
        layers_content = "\n  ".join(layer.to_svg() for layer in self.layers if layer.visible)

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">
{defs_content}  {layers_content}
</svg>"""

    def clone(self, new_name: str | None = None) -> Sprite:
        """Create a deep copy of the sprite.

        Args:
            new_name: Optional new name for the clone

        Returns:
            Cloned sprite
        """
        import copy

        cloned = copy.deepcopy(self)
        if new_name:
            cloned.name = new_name
        return cloned


class AnimationFrame(BaseModel):
    """Single frame in an animation."""

    sprite: Sprite
    duration_ms: int = 100

    model_config = {"arbitrary_types_allowed": True}


class Animation(BaseModel):
    """Animated sprite sequence.

    Example:
        >>> anim = Animation(name="walk")
        >>> anim.add_frame(sprite1, duration_ms=100)
        >>> anim.add_frame(sprite2, duration_ms=100)
    """

    name: str
    frames: list[AnimationFrame] = []
    loop: bool = True

    model_config = {"arbitrary_types_allowed": True}

    def add_frame(self, sprite: Sprite, duration_ms: int = 100) -> None:
        """Add a frame to the animation.

        Args:
            sprite: Sprite for this frame
            duration_ms: Frame duration in milliseconds
        """
        self.frames.append(AnimationFrame(sprite=sprite, duration_ms=duration_ms))

    def total_duration_ms(self) -> int:
        """Get total animation duration.

        Returns:
            Total duration in milliseconds
        """
        return sum(f.duration_ms for f in self.frames)

    def frame_at(self, time_ms: int) -> AnimationFrame | None:
        """Get frame at specific time.

        Args:
            time_ms: Time in milliseconds

        Returns:
            AnimationFrame at that time, or None if empty
        """
        if not self.frames:
            return None

        total = self.total_duration_ms()
        if total == 0:
            return self.frames[0]

        if self.loop:
            time_ms = time_ms % total

        elapsed = 0
        for frame in self.frames:
            elapsed += frame.duration_ms
            if time_ms < elapsed:
                return frame

        return self.frames[-1]

    def frame_count(self) -> int:
        """Get number of frames."""
        return len(self.frames)


class SpriteSheet(BaseModel):
    """Collection of sprites arranged in a grid.

    Example:
        >>> sheet = SpriteSheet(name="characters", columns=4, cell_width=64, cell_height=80)
        >>> sheet.add_sprite(goblin_sprite)
        >>> sheet.add_sprite(warrior_sprite)
    """

    name: str
    sprites: list[Sprite] = []
    columns: int = 4
    cell_width: int = 64
    cell_height: int = 64
    padding: int = 0

    model_config = {"arbitrary_types_allowed": True}

    def add_sprite(self, sprite: Sprite) -> None:
        """Add a sprite to the sheet.

        Args:
            sprite: Sprite to add
        """
        self.sprites.append(sprite)

    @property
    def rows(self) -> int:
        """Calculate number of rows needed."""
        if not self.sprites:
            return 0
        return (len(self.sprites) + self.columns - 1) // self.columns

    @property
    def total_width(self) -> int:
        """Calculate total sheet width."""
        return self.columns * (self.cell_width + self.padding) - self.padding

    @property
    def total_height(self) -> int:
        """Calculate total sheet height."""
        return self.rows * (self.cell_height + self.padding) - self.padding

    def get_sprite_at(self, col: int, row: int) -> Sprite | None:
        """Get sprite at grid position.

        Args:
            col: Column index (0-based)
            row: Row index (0-based)

        Returns:
            Sprite or None if out of bounds
        """
        index = row * self.columns + col
        if 0 <= index < len(self.sprites):
            return self.sprites[index]
        return None

    def get_cell_rect(self, index: int) -> Rect:
        """Get the rectangle for a cell at the given index.

        Args:
            index: Sprite index

        Returns:
            Cell rect
        """
        row = index // self.columns
        col = index % self.columns
        x = col * (self.cell_width + self.padding)
        y = row * (self.cell_height + self.padding)
        return Rect(x, y, self.cell_width, self.cell_height)

    def to_svg(self) -> str:
        """Render sprite sheet as single SVG.

        Returns:
            SVG string with all sprites
        """
        # Collect all defs
        all_defs: list[str] = []
        for sprite in self.sprites:
            all_defs.extend(sprite.defs)

        defs_content = ""
        if all_defs:
            defs_inner = "\n    ".join(all_defs)
            defs_content = f"  <defs>\n    {defs_inner}\n  </defs>\n"

        # Render each sprite at its grid position
        sprites_content = []
        for i, sprite in enumerate(self.sprites):
            cell = self.get_cell_rect(i)
            # Get sprite content without the svg wrapper
            layers_svg = "\n    ".join(layer.to_svg() for layer in sprite.layers if layer.visible)
            # Wrap in a translated group
            sprites_content.append(
                f'  <g transform="translate({cell.x}, {cell.y})">\n    {layers_svg}\n  </g>'
            )

        content = "\n".join(sprites_content)

        w, h = self.total_width, self.total_height
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">
{defs_content}{content}
</svg>"""

    def get_metadata(self) -> dict:
        """Generate TexturePacker-compatible metadata.

        Returns:
            Metadata dict
        """
        frames = {}
        for i, sprite in enumerate(self.sprites):
            cell = self.get_cell_rect(i)
            frames[sprite.name] = {
                "frame": {
                    "x": int(cell.x),
                    "y": int(cell.y),
                    "w": self.cell_width,
                    "h": self.cell_height,
                },
                "sourceSize": {"w": self.cell_width, "h": self.cell_height},
                "spriteSourceSize": {
                    "x": 0,
                    "y": 0,
                    "w": self.cell_width,
                    "h": self.cell_height,
                },
            }

        return {
            "frames": frames,
            "meta": {
                "app": "py-sprite-kit",
                "version": "0.1.0",
                "image": f"{self.name}.png",
                "format": "RGBA8888",
                "size": {"w": self.total_width, "h": self.total_height},
                "scale": 1,
            },
        }
