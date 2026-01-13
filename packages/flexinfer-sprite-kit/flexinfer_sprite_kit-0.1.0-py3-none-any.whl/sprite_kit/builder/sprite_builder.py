"""Fluent builder API for sprite construction."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Self

from sprite_kit.core.color import Color
from sprite_kit.core.shape import Circle, Path, Point, Polygon, Rectangle

if TYPE_CHECKING:
    from sprite_kit.core.palette import Palette
    from sprite_kit.sprites.base import Sprite


# Import these lazily to avoid circular imports
def _get_sprite_classes():
    from sprite_kit.sprites.base import Layer, Sprite, SpriteCategory

    return Layer, Sprite, SpriteCategory


def _get_svg_helpers():
    from sprite_kit.output.svg import (
        create_glow_filter,
        create_gradient,
        create_radial_gradient,
    )

    return create_gradient, create_radial_gradient, create_glow_filter


class SpriteBuilder:
    """Fluent API for building sprites.

    Provides a chainable interface for constructing sprites layer by layer.

    Example:
        >>> from sprite_kit import SpriteBuilder, Color
        >>> sprite = (
        ...     SpriteBuilder("goblin", 64, 80)
        ...     .layer("body")
        ...         .circle(32, 50, 20, fill=Color(100, 80, 60))
        ...     .end_layer()
        ...     .layer("face")
        ...         .circle(32, 35, 12, fill=Color(100, 80, 60))
        ...     .end_layer()
        ...     .build()
        ... )
    """

    def __init__(
        self,
        name: str,
        width: int = 64,
        height: int = 64,
        category: str = "character",
    ) -> None:
        """Initialize sprite builder.

        Args:
            name: Sprite name
            width: Sprite width in pixels
            height: Sprite height in pixels
            category: Sprite category (string or SpriteCategory)
        """
        Layer, Sprite, SpriteCategory = _get_sprite_classes()

        # Handle string or enum category
        if isinstance(category, str):
            category = SpriteCategory(category)

        self._sprite = Sprite(
            name=name,
            category=category,
            width=width,
            height=height,
            layers=[],
            metadata={},
            defs=[],
        )
        self._current_layer = None  # type: Layer | None
        self._palette: Palette | None = None

        # Cache the Layer class for later use
        self._Layer = Layer

    # === Layer Management ===

    def layer(self, name: str, opacity: float = 1.0) -> Self:
        """Create or select a layer.

        If a layer with this name exists, select it. Otherwise, create a new one.

        Args:
            name: Layer name
            opacity: Layer opacity (0.0-1.0)

        Returns:
            Self for chaining
        """
        # End any current layer first
        if self._current_layer is not None:
            self.end_layer()

        # Check if layer exists
        existing = self._sprite.get_layer(name)
        if existing:
            self._current_layer = existing
        else:
            self._current_layer = self._Layer(name=name, opacity=opacity)

        return self

    def end_layer(self) -> Self:
        """Finalize and add current layer to sprite.

        Returns:
            Self for chaining
        """
        if self._current_layer is not None:
            # Only add if not already in sprite
            if self._sprite.get_layer(self._current_layer.name) is None:
                self._sprite.add_layer(self._current_layer)
            self._current_layer = None
        return self

    # === Shape Methods ===

    def circle(
        self,
        cx: float,
        cy: float,
        r: float,
        fill: Color | str | None = None,
        stroke: Color | None = None,
        stroke_width: float = 1.0,
        opacity: float = 1.0,
        filter_id: str | None = None,
    ) -> Self:
        """Add a circle to the current layer.

        Args:
            cx: Center X coordinate
            cy: Center Y coordinate
            r: Radius
            fill: Fill color (Color, gradient ID like "url(#grad)", or None)
            stroke: Stroke color
            stroke_width: Stroke width
            opacity: Shape opacity
            filter_id: Optional filter ID to apply

        Returns:
            Self for chaining
        """
        self._ensure_layer()

        transform = f'filter="url(#{filter_id})"' if filter_id else None
        shape = Circle(
            cx=cx,
            cy=cy,
            r=r,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            opacity=opacity,
            transform=transform,
        )
        self._current_layer.add_shape(shape)  # type: ignore[union-attr]
        return self

    def rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rx: float = 0,
        ry: float = 0,
        fill: Color | str | None = None,
        stroke: Color | None = None,
        stroke_width: float = 1.0,
        opacity: float = 1.0,
    ) -> Self:
        """Add a rectangle to the current layer.

        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Rectangle width
            height: Rectangle height
            rx: X corner radius
            ry: Y corner radius
            fill: Fill color
            stroke: Stroke color
            stroke_width: Stroke width
            opacity: Shape opacity

        Returns:
            Self for chaining
        """
        self._ensure_layer()

        shape = Rectangle(
            x=x,
            y=y,
            width=width,
            height=height,
            rx=rx,
            ry=ry if ry else rx,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            opacity=opacity,
        )
        self._current_layer.add_shape(shape)  # type: ignore[union-attr]
        return self

    def polygon(
        self,
        points: list[Point] | list[tuple[float, float]],
        fill: Color | str | None = None,
        stroke: Color | None = None,
        stroke_width: float = 1.0,
        opacity: float = 1.0,
    ) -> Self:
        """Add a polygon to the current layer.

        Args:
            points: List of points (Point objects or (x, y) tuples)
            fill: Fill color
            stroke: Stroke color
            stroke_width: Stroke width
            opacity: Shape opacity

        Returns:
            Self for chaining
        """
        self._ensure_layer()

        # Convert tuples to Points if needed
        pts = [Point(p[0], p[1]) if isinstance(p, tuple) else p for p in points]

        shape = Polygon(
            points=pts,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            opacity=opacity,
        )
        self._current_layer.add_shape(shape)  # type: ignore[union-attr]
        return self

    def path(
        self,
        d: str,
        fill: Color | str | None = None,
        stroke: Color | None = None,
        stroke_width: float = 1.0,
        opacity: float = 1.0,
    ) -> Self:
        """Add an SVG path to the current layer.

        Args:
            d: SVG path data string
            fill: Fill color
            stroke: Stroke color
            stroke_width: Stroke width
            opacity: Shape opacity

        Returns:
            Self for chaining
        """
        self._ensure_layer()

        shape = Path(
            d=d,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            opacity=opacity,
        )
        self._current_layer.add_shape(shape)  # type: ignore[union-attr]
        return self

    # === Convenience Shape Methods ===

    def star(
        self,
        cx: float,
        cy: float,
        outer_r: float,
        inner_r: float,
        points: int = 5,
        rotation: float = -math.pi / 2,
        fill: Color | str | None = None,
        stroke: Color | None = None,
    ) -> Self:
        """Add a star shape to the current layer.

        Args:
            cx: Center X
            cy: Center Y
            outer_r: Outer radius (tips)
            inner_r: Inner radius (valleys)
            points: Number of star points
            rotation: Rotation in radians (default: point up)
            fill: Fill color
            stroke: Stroke color

        Returns:
            Self for chaining
        """
        self._ensure_layer()

        shape = Polygon.star(
            center=Point(cx, cy),
            outer_r=outer_r,
            inner_r=inner_r,
            points_count=points,
            rotation=rotation,
            fill=fill,
            stroke=stroke,
        )
        self._current_layer.add_shape(shape)  # type: ignore[union-attr]
        return self

    def hexagon(
        self,
        cx: float,
        cy: float,
        size: float,
        flat_top: bool = True,
        fill: Color | str | None = None,
        stroke: Color | None = None,
    ) -> Self:
        """Add a hexagon to the current layer.

        Args:
            cx: Center X
            cy: Center Y
            size: Distance from center to vertex
            flat_top: If True, flat edge on top; if False, point on top
            fill: Fill color
            stroke: Stroke color

        Returns:
            Self for chaining
        """
        self._ensure_layer()

        rotation = 0 if flat_top else math.pi / 6
        shape = Polygon.regular(
            center=Point(cx, cy),
            radius=size,
            sides=6,
            rotation=rotation,
            fill=fill,
            stroke=stroke,
        )
        self._current_layer.add_shape(shape)  # type: ignore[union-attr]
        return self

    def regular_polygon(
        self,
        cx: float,
        cy: float,
        radius: float,
        sides: int,
        rotation: float = 0,
        fill: Color | str | None = None,
        stroke: Color | None = None,
    ) -> Self:
        """Add a regular polygon to the current layer.

        Args:
            cx: Center X
            cy: Center Y
            radius: Distance from center to vertices
            sides: Number of sides
            rotation: Rotation in radians
            fill: Fill color
            stroke: Stroke color

        Returns:
            Self for chaining
        """
        self._ensure_layer()

        shape = Polygon.regular(
            center=Point(cx, cy),
            radius=radius,
            sides=sides,
            rotation=rotation,
            fill=fill,
            stroke=stroke,
        )
        self._current_layer.add_shape(shape)  # type: ignore[union-attr]
        return self

    # === Definition Methods ===

    def define_gradient(
        self,
        gradient_id: str,
        colors: list[Color | str],
        direction: str = "vertical",
    ) -> Self:
        """Add a linear gradient definition.

        Args:
            gradient_id: ID for referencing the gradient (e.g., "url(#myGrad)")
            colors: List of colors (Color objects or hex strings)
            direction: "vertical", "horizontal", or "diagonal"

        Returns:
            Self for chaining
        """
        create_gradient, _, _ = _get_svg_helpers()
        hex_colors = [c.to_hex() if isinstance(c, Color) else c for c in colors]
        gradient = create_gradient(gradient_id, hex_colors, direction)
        self._sprite.add_def(gradient)
        return self

    def define_radial_gradient(
        self,
        gradient_id: str,
        colors: list[Color | str],
        cx: float = 50,
        cy: float = 50,
        r: float = 50,
    ) -> Self:
        """Add a radial gradient definition.

        Args:
            gradient_id: ID for referencing the gradient
            colors: List of colors (center to edge)
            cx: Center X as percentage
            cy: Center Y as percentage
            r: Radius as percentage

        Returns:
            Self for chaining
        """
        _, create_radial_gradient, _ = _get_svg_helpers()
        hex_colors = [c.to_hex() if isinstance(c, Color) else c for c in colors]
        gradient = create_radial_gradient(gradient_id, hex_colors, cx, cy, r)
        self._sprite.add_def(gradient)
        return self

    def define_glow_filter(
        self,
        filter_id: str,
        color: Color | str,
        blur: float = 2.0,
    ) -> Self:
        """Add a glow filter definition.

        Args:
            filter_id: ID for referencing the filter
            color: Glow color
            blur: Blur standard deviation

        Returns:
            Self for chaining
        """
        _, _, create_glow_filter = _get_svg_helpers()
        hex_color = color.to_hex() if isinstance(color, Color) else color
        filt = create_glow_filter(filter_id, hex_color, blur)
        self._sprite.add_def(filt)
        return self

    def define(self, svg_def: str) -> Self:
        """Add a raw SVG definition.

        Args:
            svg_def: Raw SVG definition element

        Returns:
            Self for chaining
        """
        self._sprite.add_def(svg_def)
        return self

    # === Metadata Methods ===

    def with_palette(self, palette: Palette) -> Self:
        """Associate a palette with the sprite.

        Args:
            palette: Palette to use

        Returns:
            Self for chaining
        """
        self._palette = palette
        self._sprite.palette = palette
        return self

    def with_metadata(self, key: str, value: str) -> Self:
        """Add metadata to the sprite.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for chaining
        """
        self._sprite.metadata[key] = value
        return self

    # === Build ===

    def build(self) -> Sprite:
        """Finalize and return the sprite.

        Returns:
            Completed Sprite instance
        """
        # End any open layer
        if self._current_layer is not None:
            self.end_layer()

        return self._sprite

    # === Internal ===

    def _ensure_layer(self) -> None:
        """Ensure we have a current layer, creating 'default' if needed."""
        if self._current_layer is None:
            self._current_layer = self._Layer(name="default")

    # === Palette Helper ===

    def palette_color(self, name: str) -> Color:
        """Get a color from the associated palette.

        Args:
            name: Color name in the palette

        Returns:
            Color instance

        Raises:
            ValueError: If no palette is set or color not found
        """
        if self._palette is None:
            raise ValueError("No palette set. Use with_palette() first.")
        return self._palette[name]
