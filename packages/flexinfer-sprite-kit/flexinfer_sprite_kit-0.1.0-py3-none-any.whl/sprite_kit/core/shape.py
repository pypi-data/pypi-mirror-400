"""Geometric shape primitives."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Self

from sprite_kit.core.color import Color


@dataclass(frozen=True)
class Point:
    """2D point with basic operations.

    Example:
        >>> p1 = Point(10, 20)
        >>> p2 = Point(30, 40)
        >>> p1 + p2
        Point(x=40, y=60)
    """

    x: float
    y: float

    def __add__(self, other: Point) -> Self:
        """Add two points."""
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Self:
        """Subtract two points."""
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Self:
        """Scale point by scalar."""
        return self.__class__(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Self:
        """Divide point by scalar."""
        return self.__class__(self.x / scalar, self.y / scalar)

    def distance_to(self, other: Point) -> float:
        """Calculate distance to another point."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def angle_to(self, other: Point) -> float:
        """Calculate angle to another point in radians."""
        return math.atan2(other.y - self.y, other.x - self.x)

    def rotate(self, angle: float, origin: Point | None = None) -> Self:
        """Rotate point around origin.

        Args:
            angle: Rotation angle in radians
            origin: Center of rotation (default: (0, 0))

        Returns:
            Rotated point
        """
        if origin is None:
            origin = Point(0, 0)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        dx = self.x - origin.x
        dy = self.y - origin.y

        return self.__class__(
            origin.x + dx * cos_a - dy * sin_a,
            origin.y + dx * sin_a + dy * cos_a,
        )

    def lerp(self, other: Point, t: float) -> Self:
        """Linear interpolate to another point."""
        return self.__class__(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )


@dataclass
class Rect:
    """Axis-aligned bounding box."""

    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> Point:
        """Get center point."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def top_left(self) -> Point:
        """Get top-left corner."""
        return Point(self.x, self.y)

    @property
    def bottom_right(self) -> Point:
        """Get bottom-right corner."""
        return Point(self.x + self.width, self.y + self.height)

    @property
    def corners(self) -> list[Point]:
        """Get all four corners."""
        return [
            Point(self.x, self.y),
            Point(self.x + self.width, self.y),
            Point(self.x + self.width, self.y + self.height),
            Point(self.x, self.y + self.height),
        ]

    def contains(self, point: Point) -> bool:
        """Check if point is inside rect."""
        return (
            self.x <= point.x <= self.x + self.width and self.y <= point.y <= self.y + self.height
        )

    def intersects(self, other: Rect) -> bool:
        """Check if this rect intersects another."""
        return not (
            self.x + self.width < other.x
            or other.x + other.width < self.x
            or self.y + self.height < other.y
            or other.y + other.height < self.y
        )

    def inset(self, amount: float) -> Rect:
        """Return rect with edges moved inward."""
        return Rect(
            self.x + amount,
            self.y + amount,
            max(0, self.width - 2 * amount),
            max(0, self.height - 2 * amount),
        )

    def expand(self, amount: float) -> Rect:
        """Return rect with edges moved outward."""
        return self.inset(-amount)


@dataclass
class Shape(ABC):
    """Base class for all drawable shapes."""

    fill: Color | str | None = None
    stroke: Color | None = None
    stroke_width: float = 1.0
    opacity: float = 1.0
    transform: str | None = None

    @abstractmethod
    def to_svg(self) -> str:
        """Render shape as SVG element."""
        pass

    @abstractmethod
    def bounds(self) -> Rect:
        """Get bounding box."""
        pass

    def _style_attrs(self) -> str:
        """Generate common SVG style attributes."""
        attrs = []

        if self.fill is not None:
            if isinstance(self.fill, Color):
                attrs.append(f'fill="{self.fill.to_hex()}"')
                if self.fill.a < 1.0:
                    attrs.append(f'fill-opacity="{self.fill.a}"')
            else:
                attrs.append(f'fill="{self.fill}"')
        else:
            attrs.append('fill="none"')

        if self.stroke is not None:
            attrs.append(f'stroke="{self.stroke.to_hex()}"')
            attrs.append(f'stroke-width="{self.stroke_width}"')
            if self.stroke.a < 1.0:
                attrs.append(f'stroke-opacity="{self.stroke.a}"')

        if self.opacity < 1.0:
            attrs.append(f'opacity="{self.opacity}"')

        if self.transform:
            attrs.append(f'transform="{self.transform}"')

        return " ".join(attrs)


@dataclass
class Circle(Shape):
    """Circle shape."""

    cx: float = 0
    cy: float = 0
    r: float = 10

    def to_svg(self) -> str:
        """Render as SVG circle element."""
        return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.r}" {self._style_attrs()}/>'

    def bounds(self) -> Rect:
        """Get bounding box."""
        return Rect(self.cx - self.r, self.cy - self.r, self.r * 2, self.r * 2)


@dataclass
class Rectangle(Shape):
    """Rectangle shape."""

    x: float = 0
    y: float = 0
    width: float = 10
    height: float = 10
    rx: float = 0
    ry: float = 0

    def to_svg(self) -> str:
        """Render as SVG rect element."""
        rx_attr = f'rx="{self.rx}" ry="{self.ry}"' if self.rx or self.ry else ""
        return (
            f'<rect x="{self.x}" y="{self.y}" '
            f'width="{self.width}" height="{self.height}" '
            f"{rx_attr} {self._style_attrs()}/>"
        )

    def bounds(self) -> Rect:
        """Get bounding box."""
        return Rect(self.x, self.y, self.width, self.height)


@dataclass
class Polygon(Shape):
    """Polygon shape defined by a list of points."""

    points: list[Point] = field(default_factory=list)

    def to_svg(self) -> str:
        """Render as SVG polygon element."""
        points_str = " ".join(f"{p.x},{p.y}" for p in self.points)
        return f'<polygon points="{points_str}" {self._style_attrs()}/>'

    def bounds(self) -> Rect:
        """Get bounding box."""
        if not self.points:
            return Rect(0, 0, 0, 0)
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    @classmethod
    def regular(
        cls,
        center: Point,
        radius: float,
        sides: int,
        rotation: float = 0,
        **kwargs: object,
    ) -> Polygon:
        """Create regular polygon (triangle, pentagon, hexagon, etc.).

        Args:
            center: Center point
            radius: Distance from center to vertices
            sides: Number of sides
            rotation: Rotation in radians
            **kwargs: Additional shape attributes (fill, stroke, etc.)

        Returns:
            Regular polygon
        """
        points = []
        for i in range(sides):
            angle = rotation + (2 * math.pi * i / sides)
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            points.append(Point(x, y))
        return cls(points=points, **kwargs)  # type: ignore[arg-type]

    @classmethod
    def star(
        cls,
        center: Point,
        outer_r: float,
        inner_r: float,
        points_count: int,
        rotation: float = -math.pi / 2,
        **kwargs: object,
    ) -> Polygon:
        """Create star shape.

        Args:
            center: Center point
            outer_r: Outer radius (tips)
            inner_r: Inner radius (valleys)
            points_count: Number of star points
            rotation: Rotation in radians (default: point up)
            **kwargs: Additional shape attributes

        Returns:
            Star polygon
        """
        points = []
        for i in range(points_count * 2):
            angle = rotation + (math.pi * i / points_count)
            r = outer_r if i % 2 == 0 else inner_r
            x = center.x + r * math.cos(angle)
            y = center.y + r * math.sin(angle)
            points.append(Point(x, y))
        return cls(points=points, **kwargs)  # type: ignore[arg-type]


@dataclass
class Path(Shape):
    """SVG path with commands."""

    d: str = ""

    def to_svg(self) -> str:
        """Render as SVG path element."""
        return f'<path d="{self.d}" {self._style_attrs()}/>'

    def bounds(self) -> Rect:
        """Get bounding box (approximation from path data)."""
        # Simple approximation: extract numbers and compute bounds
        import re

        numbers = re.findall(r"[-+]?\d*\.?\d+", self.d)
        if len(numbers) < 2:
            return Rect(0, 0, 0, 0)

        xs = [float(numbers[i]) for i in range(0, len(numbers), 2)]
        ys = [float(numbers[i]) for i in range(1, len(numbers), 2)]

        if not xs or not ys:
            return Rect(0, 0, 0, 0)

        return Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


class PathBuilder:
    """Fluent builder for SVG path commands.

    Example:
        >>> path = PathBuilder().move_to(Point(0, 0)).line_to(Point(100, 100)).close().build()
        >>> path.d
        'M 0 0 L 100 100 Z'
    """

    def __init__(self) -> None:
        self._commands: list[str] = []

    def move_to(self, p: Point) -> Self:
        """Move to point (M command)."""
        self._commands.append(f"M {p.x} {p.y}")
        return self

    def line_to(self, p: Point) -> Self:
        """Line to point (L command)."""
        self._commands.append(f"L {p.x} {p.y}")
        return self

    def horizontal_to(self, x: float) -> Self:
        """Horizontal line to x (H command)."""
        self._commands.append(f"H {x}")
        return self

    def vertical_to(self, y: float) -> Self:
        """Vertical line to y (V command)."""
        self._commands.append(f"V {y}")
        return self

    def curve_to(self, p: Point, c1: Point, c2: Point | None = None) -> Self:
        """Bezier curve to point.

        Args:
            p: End point
            c1: First control point
            c2: Second control point (for cubic), None for quadratic
        """
        if c2 is None:
            self._commands.append(f"Q {c1.x} {c1.y} {p.x} {p.y}")
        else:
            self._commands.append(f"C {c1.x} {c1.y} {c2.x} {c2.y} {p.x} {p.y}")
        return self

    def arc_to(
        self,
        p: Point,
        rx: float,
        ry: float,
        rotation: float = 0,
        large_arc: bool = False,
        sweep: bool = True,
    ) -> Self:
        """Arc to point (A command)."""
        large = 1 if large_arc else 0
        sweep_flag = 1 if sweep else 0
        self._commands.append(f"A {rx} {ry} {rotation} {large} {sweep_flag} {p.x} {p.y}")
        return self

    def close(self) -> Self:
        """Close path (Z command)."""
        self._commands.append("Z")
        return self

    def build(self, **kwargs: object) -> Path:
        """Build the Path shape.

        Args:
            **kwargs: Additional shape attributes (fill, stroke, etc.)

        Returns:
            Path shape
        """
        return Path(d=" ".join(self._commands), **kwargs)  # type: ignore[arg-type]
