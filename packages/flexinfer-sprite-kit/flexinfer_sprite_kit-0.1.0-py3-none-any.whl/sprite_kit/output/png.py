"""PNG export functionality using cairosvg and Pillow."""

from __future__ import annotations

from enum import Enum
from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image

from sprite_kit.output.svg import SVGExporter
from sprite_kit.sprites.base import Animation, Sprite, SpriteSheet


class PixelStyle(str, Enum):
    """Pixel art rendering style."""

    CRISP = "crisp"  # Nearest-neighbor scaling, hard edges
    SMOOTH = "smooth"  # Bilinear scaling, anti-aliased
    DITHERED = "dithered"  # Reduced color palette with dithering


class PNGExporter:
    """Export sprites as PNG images.

    Uses cairosvg to render SVG to PNG, with optional
    Pillow post-processing for pixel art styles.

    Example:
        >>> from sprite_kit import SpriteBuilder, PNGExporter
        >>> sprite = SpriteBuilder("icon", 32, 32).circle(16, 16, 10).build()
        >>> exporter = PNGExporter(scale=2, style=PixelStyle.CRISP)
        >>> exporter.export_file(sprite, "icon.png")
    """

    def __init__(
        self,
        scale: float = 1.0,
        style: PixelStyle = PixelStyle.SMOOTH,
        background_color: str | None = None,
        palette_size: int = 16,
    ) -> None:
        """Initialize PNG exporter.

        Args:
            scale: Scale factor for output (2.0 = 2x size)
            style: Pixel rendering style
            background_color: Optional background color (e.g., "#ffffff")
            palette_size: Color palette size for dithered mode
        """
        self.scale = scale
        self.style = style
        self.background_color = background_color
        self.palette_size = palette_size
        self._svg_exporter = SVGExporter()

    def export(self, sprite: Sprite) -> bytes:
        """Export sprite as PNG bytes.

        Args:
            sprite: Sprite to export

        Returns:
            PNG image as bytes
        """
        svg_string = self._svg_exporter.export(sprite)
        return self._render_png(svg_string, sprite.width, sprite.height)

    def export_image(self, sprite: Sprite) -> Image.Image:
        """Export sprite as PIL Image.

        Args:
            sprite: Sprite to export

        Returns:
            PIL Image object
        """
        png_bytes = self.export(sprite)
        return Image.open(BytesIO(png_bytes))

    def export_file(self, sprite: Sprite, path: str | Path) -> None:
        """Export sprite to PNG file.

        Args:
            sprite: Sprite to export
            path: Output file path
        """
        png_bytes = self.export(sprite)
        Path(path).write_bytes(png_bytes)

    def export_animation(
        self,
        animation: Animation,
        output_dir: str | Path,
        prefix: str = "",
    ) -> list[Path]:
        """Export animation frames as PNG files.

        Args:
            animation: Animation to export
            output_dir: Output directory
            prefix: Filename prefix

        Returns:
            List of exported file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for i, frame in enumerate(animation.frames):
            filename = f"{prefix}{animation.name}_frame{i:03d}.png"
            path = output_dir / filename
            self.export_file(frame.sprite, path)
            paths.append(path)

        return paths

    def export_sheet(self, sheet: SpriteSheet) -> bytes:
        """Export sprite sheet as single PNG.

        Args:
            sheet: SpriteSheet to export

        Returns:
            PNG image as bytes
        """
        svg_string = self._svg_exporter.export_sheet(sheet)
        total_width = sheet.columns * sheet.cell_width
        total_height = sheet.rows * sheet.cell_height
        return self._render_png(svg_string, total_width, total_height)

    def export_sheet_file(self, sheet: SpriteSheet, path: str | Path) -> None:
        """Export sprite sheet to PNG file.

        Args:
            sheet: SpriteSheet to export
            path: Output file path
        """
        png_bytes = self.export_sheet(sheet)
        Path(path).write_bytes(png_bytes)

    def export_sheet_image(self, sheet: SpriteSheet) -> Image.Image:
        """Export sprite sheet as PIL Image.

        Args:
            sheet: SpriteSheet to export

        Returns:
            PIL Image object
        """
        png_bytes = self.export_sheet(sheet)
        return Image.open(BytesIO(png_bytes))

    def _render_png(self, svg_string: str, width: int, height: int) -> bytes:
        """Render SVG string to PNG bytes.

        Args:
            svg_string: SVG content
            width: Original width
            height: Original height

        Returns:
            PNG bytes
        """
        # Calculate output dimensions
        output_width = int(width * self.scale)
        output_height = int(height * self.scale)

        # Render SVG to PNG using cairosvg
        png_bytes = cairosvg.svg2png(
            bytestring=svg_string.encode("utf-8"),
            output_width=output_width,
            output_height=output_height,
            background_color=self.background_color,
        )

        # Apply post-processing based on style
        if self.style == PixelStyle.CRISP:
            png_bytes = self._apply_crisp_scaling(png_bytes, width, height)
        elif self.style == PixelStyle.DITHERED:
            png_bytes = self._apply_dithering(png_bytes)

        return png_bytes

    def _apply_crisp_scaling(self, png_bytes: bytes, orig_width: int, orig_height: int) -> bytes:
        """Apply nearest-neighbor scaling for pixel art look.

        First renders at original size, then scales up with
        nearest-neighbor interpolation for hard pixel edges.

        Args:
            png_bytes: Input PNG bytes
            orig_width: Original sprite width
            orig_height: Original sprite height

        Returns:
            Processed PNG bytes
        """
        if self.scale <= 1.0:
            return png_bytes

        # Re-render at original size first for crispness
        img = Image.open(BytesIO(png_bytes))

        # If already at target size, just return
        target_width = int(orig_width * self.scale)
        target_height = int(orig_height * self.scale)

        if img.width == target_width and img.height == target_height:
            # Scale down then back up with nearest neighbor
            small = img.resize((orig_width, orig_height), Image.Resampling.LANCZOS)
            crisp = small.resize((target_width, target_height), Image.Resampling.NEAREST)
        else:
            crisp = img.resize((target_width, target_height), Image.Resampling.NEAREST)

        # Save to bytes
        output = BytesIO()
        crisp.save(output, format="PNG")
        return output.getvalue()

    def _apply_dithering(self, png_bytes: bytes) -> bytes:
        """Apply color palette reduction with dithering.

        Reduces colors to create a retro pixel art aesthetic.

        Args:
            png_bytes: Input PNG bytes

        Returns:
            Dithered PNG bytes
        """
        img = Image.open(BytesIO(png_bytes))

        # Preserve alpha channel
        if img.mode == "RGBA":
            # Split alpha
            r, g, b, a = img.split()

            # Convert RGB to palette
            rgb = Image.merge("RGB", (r, g, b))
            rgb = rgb.quantize(colors=self.palette_size, dither=Image.Dither.FLOYDSTEINBERG)
            rgb = rgb.convert("RGB")

            # Recombine with alpha
            r, g, b = rgb.split()
            img = Image.merge("RGBA", (r, g, b, a))
        else:
            # Simple palette conversion
            img = img.quantize(colors=self.palette_size, dither=Image.Dither.FLOYDSTEINBERG)
            img = img.convert("RGB")

        # Save to bytes
        output = BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()


def create_gif(
    frames: list[Sprite],
    output_path: str | Path,
    duration_ms: int = 100,
    loop: int = 0,
    scale: float = 1.0,
    style: PixelStyle = PixelStyle.SMOOTH,
    background_color: str = "#ffffff",
) -> None:
    """Create animated GIF from sprite frames.

    Args:
        frames: List of sprite frames
        output_path: Output GIF path
        duration_ms: Duration per frame in milliseconds
        loop: Number of loops (0 = infinite)
        scale: Scale factor
        style: Pixel style
        background_color: Background color for transparency
    """
    exporter = PNGExporter(scale=scale, style=style, background_color=background_color)

    # Convert RGBA to P (palette) mode for GIF compatibility
    images = []
    for frame in frames:
        img = exporter.export_image(frame)
        # GIF doesn't support RGBA, convert to P mode
        if img.mode == "RGBA":
            # Create a background and paste with alpha
            bg = Image.new("RGB", img.size, background_color)
            bg.paste(img, mask=img.split()[3])
            img = bg.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        elif img.mode != "P":
            img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        images.append(img)

    # Save as animated GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=loop,
    )


def create_spritesheet_png(
    sprites: list[Sprite],
    output_path: str | Path,
    columns: int = 4,
    scale: float = 1.0,
    style: PixelStyle = PixelStyle.SMOOTH,
) -> dict:
    """Create a sprite sheet PNG with metadata.

    Args:
        sprites: List of sprites
        output_path: Output PNG path
        columns: Sprites per row
        scale: Scale factor
        style: Pixel style

    Returns:
        Sprite sheet metadata dict
    """
    if not sprites:
        raise ValueError("No sprites provided")

    # Create sheet
    sheet = SpriteSheet(
        name="spritesheet",
        cell_width=sprites[0].width,
        cell_height=sprites[0].height,
        columns=columns,
    )

    for sprite in sprites:
        sheet.add_sprite(sprite)

    # Export
    exporter = PNGExporter(scale=scale, style=style)
    exporter.export_sheet_file(sheet, output_path)

    # Return metadata
    return sheet.get_metadata()
