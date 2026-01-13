"""Color primitives with manipulation methods."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Color:
    """Immutable color representation with manipulation methods.

    Supports RGB values (0-255) with optional alpha (0.0-1.0).

    Example:
        >>> Color.from_hex("#FF5500")
        Color(r=255, g=85, b=0, a=1.0)
        >>> Color(255, 0, 0).lighten(0.2).to_hex()
        '#FF3333'
    """

    r: int
    g: int
    b: int
    a: float = 1.0

    def __post_init__(self) -> None:
        """Validate color values."""
        if not (0 <= self.r <= 255 and 0 <= self.g <= 255 and 0 <= self.b <= 255):
            raise ValueError(f"RGB values must be 0-255, got ({self.r}, {self.g}, {self.b})")
        if not 0.0 <= self.a <= 1.0:
            raise ValueError(f"Alpha must be 0.0-1.0, got {self.a}")

    @classmethod
    def from_hex(cls, hex_str: str) -> Self:
        """Parse hex color (#RRGGBB, #RGB, or RRGGBB).

        Args:
            hex_str: Hex color string

        Returns:
            Color instance

        Example:
            >>> Color.from_hex("#FF5500")
            Color(r=255, g=85, b=0, a=1.0)
        """
        hex_str = hex_str.lstrip("#")

        if len(hex_str) == 3:
            hex_str = "".join(c * 2 for c in hex_str)

        if len(hex_str) != 6:
            raise ValueError(f"Invalid hex color: {hex_str}")

        if not re.match(r"^[0-9A-Fa-f]{6}$", hex_str):
            raise ValueError(f"Invalid hex color: {hex_str}")

        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return cls(r, g, b)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, a: float = 1.0) -> Self:
        """Create from RGB values.

        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            a: Alpha (0.0-1.0)

        Returns:
            Color instance
        """
        return cls(r, g, b, a)

    def to_hex(self) -> str:
        """Export as hex string (#RRGGBB).

        Returns:
            Hex color string
        """
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_rgba(self) -> str:
        """Export as rgba() CSS string.

        Returns:
            CSS rgba string
        """
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a})"

    def to_rgb_tuple(self) -> tuple[int, int, int]:
        """Export as RGB tuple.

        Returns:
            (r, g, b) tuple
        """
        return (self.r, self.g, self.b)

    def lighten(self, amount: float = 0.2) -> Self:
        """Return lightened color.

        Args:
            amount: Amount to lighten (0.0-1.0)

        Returns:
            New lightened Color
        """
        return self.__class__(
            r=min(255, int(self.r + (255 - self.r) * amount)),
            g=min(255, int(self.g + (255 - self.g) * amount)),
            b=min(255, int(self.b + (255 - self.b) * amount)),
            a=self.a,
        )

    def darken(self, amount: float = 0.2) -> Self:
        """Return darkened color.

        Args:
            amount: Amount to darken (0.0-1.0)

        Returns:
            New darkened Color
        """
        return self.__class__(
            r=max(0, int(self.r * (1 - amount))),
            g=max(0, int(self.g * (1 - amount))),
            b=max(0, int(self.b * (1 - amount))),
            a=self.a,
        )

    def with_alpha(self, alpha: float) -> Self:
        """Return color with adjusted alpha.

        Args:
            alpha: New alpha value (0.0-1.0)

        Returns:
            New Color with adjusted alpha
        """
        return self.__class__(self.r, self.g, self.b, alpha)

    def lerp(self, other: Color, t: float) -> Self:
        """Linear interpolate to another color.

        Args:
            other: Target color
            t: Interpolation factor (0.0 = self, 1.0 = other)

        Returns:
            Interpolated Color
        """
        t = max(0.0, min(1.0, t))
        return self.__class__(
            r=int(self.r + (other.r - self.r) * t),
            g=int(self.g + (other.g - self.g) * t),
            b=int(self.b + (other.b - self.b) * t),
            a=self.a + (other.a - self.a) * t,
        )

    def complementary(self) -> Self:
        """Return complementary (opposite) color.

        Returns:
            Complementary Color
        """
        return self.__class__(255 - self.r, 255 - self.g, 255 - self.b, self.a)

    def __str__(self) -> str:
        """Return hex representation."""
        return self.to_hex()


def color_scale(start: Color, end: Color, steps: int) -> list[Color]:
    """Generate gradient steps between two colors.

    Args:
        start: Starting color
        end: Ending color
        steps: Number of steps (including start and end)

    Returns:
        List of Colors forming a gradient

    Example:
        >>> colors = color_scale(Color.from_hex("#000"), Color.from_hex("#FFF"), 3)
        >>> [c.to_hex() for c in colors]
        ['#000000', '#7F7F7F', '#FFFFFF']
    """
    if steps < 2:
        return [start]
    return [start.lerp(end, i / (steps - 1)) for i in range(steps)]
