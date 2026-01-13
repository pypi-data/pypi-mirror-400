"""SVG export functionality."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

from sprite_kit.sprites.base import Animation, Sprite, SpriteSheet


class SVGExporter(BaseModel):
    """Export sprites to SVG format.

    Example:
        >>> exporter = SVGExporter()
        >>> exporter.export_file(sprite, "output.svg")
        >>> svg_string = exporter.export(sprite)
    """

    minify: bool = False
    include_metadata: bool = True

    def export(self, sprite: Sprite) -> str:
        """Export sprite as SVG string.

        Args:
            sprite: Sprite to export

        Returns:
            SVG string
        """
        svg = sprite.to_svg()

        if self.minify:
            svg = self._minify(svg)

        return svg

    def export_bytes(self, sprite: Sprite) -> bytes:
        """Export sprite as UTF-8 bytes.

        Args:
            sprite: Sprite to export

        Returns:
            UTF-8 encoded SVG bytes
        """
        return self.export(sprite).encode("utf-8")

    def export_file(self, sprite: Sprite, path: str | Path) -> None:
        """Export sprite to SVG file.

        Args:
            sprite: Sprite to export
            path: Output file path
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.export(sprite))

    def export_animation(self, animation: Animation) -> list[str]:
        """Export animation as list of SVG strings.

        Args:
            animation: Animation to export

        Returns:
            List of SVG strings (one per frame)
        """
        return [self.export(frame.sprite) for frame in animation.frames]

    def export_animation_files(
        self,
        animation: Animation,
        output_dir: str | Path,
        prefix: str = "",
    ) -> list[Path]:
        """Export animation frames to separate files.

        Args:
            animation: Animation to export
            output_dir: Output directory
            prefix: Optional filename prefix

        Returns:
            List of output file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for i, frame in enumerate(animation.frames):
            name = f"{prefix}{animation.name}_{i:03d}.svg"
            path = output_dir / name
            self.export_file(frame.sprite, path)
            paths.append(path)

        return paths

    def export_sheet(self, sheet: SpriteSheet) -> str:
        """Export sprite sheet as single SVG.

        Args:
            sheet: SpriteSheet to export

        Returns:
            SVG string with all sprites arranged in grid
        """
        svg = sheet.to_svg()

        if self.minify:
            svg = self._minify(svg)

        return svg

    def export_sheet_file(self, sheet: SpriteSheet, path: str | Path) -> None:
        """Export sprite sheet to SVG file.

        Args:
            sheet: SpriteSheet to export
            path: Output file path
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.export_sheet(sheet))

    def _minify(self, svg: str) -> str:
        """Minify SVG by removing unnecessary whitespace.

        Args:
            svg: SVG string

        Returns:
            Minified SVG string
        """
        # Remove newlines and extra spaces
        svg = re.sub(r"\s+", " ", svg)
        # Remove spaces around tags
        svg = re.sub(r">\s+<", "><", svg)
        # Remove trailing spaces before />
        svg = re.sub(r"\s+/>", "/>", svg)
        return svg.strip()


def create_gradient(
    gradient_id: str,
    colors: list[str],
    direction: str = "vertical",
) -> str:
    """Create an SVG linear gradient definition.

    Args:
        gradient_id: ID for the gradient
        colors: List of hex color values
        direction: "vertical", "horizontal", or "diagonal"

    Returns:
        SVG linearGradient element

    Example:
        >>> grad = create_gradient("myGrad", ["#FF0000", "#0000FF"])
        >>> '<linearGradient id="myGrad"' in grad
        True
    """
    if direction == "horizontal":
        coords = 'x1="0%" y1="0%" x2="100%" y2="0%"'
    elif direction == "diagonal":
        coords = 'x1="0%" y1="0%" x2="100%" y2="100%"'
    else:  # vertical
        coords = 'x1="0%" y1="0%" x2="0%" y2="100%"'

    stops = []
    for i, color in enumerate(colors):
        offset = (i / (len(colors) - 1)) * 100 if len(colors) > 1 else 0
        stops.append(f'<stop offset="{offset:.0f}%" stop-color="{color}"/>')

    stops_str = "\n      ".join(stops)
    return f"""<linearGradient id="{gradient_id}" {coords}>
      {stops_str}
    </linearGradient>"""


def create_radial_gradient(
    gradient_id: str,
    colors: list[str],
    cx: float = 50,
    cy: float = 50,
    r: float = 50,
) -> str:
    """Create an SVG radial gradient definition.

    Args:
        gradient_id: ID for the gradient
        colors: List of hex color values (center to edge)
        cx: Center X as percentage
        cy: Center Y as percentage
        r: Radius as percentage

    Returns:
        SVG radialGradient element
    """
    stops = []
    for i, color in enumerate(colors):
        offset = (i / (len(colors) - 1)) * 100 if len(colors) > 1 else 0
        stops.append(f'<stop offset="{offset:.0f}%" stop-color="{color}"/>')

    stops_str = "\n      ".join(stops)
    return f"""<radialGradient id="{gradient_id}" cx="{cx}%" cy="{cy}%" r="{r}%">
      {stops_str}
    </radialGradient>"""


def create_glow_filter(
    filter_id: str,
    color: str,
    stddev: float = 2.0,
) -> str:
    """Create a Godot-compatible glow filter.

    Args:
        filter_id: ID for the filter
        color: Glow color (hex)
        stddev: Blur standard deviation

    Returns:
        SVG filter element
    """
    return f"""<filter id="{filter_id}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="{stddev}" result="blur"/>
      <feFlood flood-color="{color}" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="colorBlur"/>
      <feMerge>
        <feMergeNode in="colorBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>"""


def create_drop_shadow_filter(
    filter_id: str,
    dx: float = 2,
    dy: float = 2,
    blur: float = 2,
    opacity: float = 0.3,
) -> str:
    """Create a drop shadow filter.

    Args:
        filter_id: ID for the filter
        dx: Shadow X offset
        dy: Shadow Y offset
        blur: Blur amount
        opacity: Shadow opacity

    Returns:
        SVG filter element
    """
    return f"""<filter id="{filter_id}" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="{dx}" dy="{dy}" stdDeviation="{blur}" flood-opacity="{opacity}"/>
    </filter>"""
