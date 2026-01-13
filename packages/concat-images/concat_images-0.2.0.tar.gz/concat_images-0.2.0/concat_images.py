#!/usr/bin/env python3
"""
Image concatenation script that combines multiple images into one.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Literal, Tuple
from PIL import Image

Orientation = Literal['vertical', 'horizontal']
Alignment = Literal['begin', 'center', 'end']
Color = Tuple[int, int, int, int]

DEFAULT_BACKGROUND: Color = (255, 255, 255, 255)


def parse_color(color_str: str) -> Color:
    """Parse color string to RGBA tuple."""
    if color_str == 'transparent':
        return (0, 0, 0, 0)

    try:
        parts = [int(x.strip()) for x in color_str.split(',')]
        if len(parts) == 3:
            return (parts[0], parts[1], parts[2], 255)
        elif len(parts) == 4:
            return (parts[0], parts[1], parts[2], parts[3])
        else:
            raise ValueError("Color must have 3 (RGB) or 4 (RGBA) components")
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid color '{color_str}'. Use R,G,B or R,G,B,A format (e.g., 255,255,255 or 0,0,0,0) or 'transparent'"
        ) from e


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Concatenate multiple images into one.',
        usage='%(prog)s output_path image1 image2 [image3 ...] [options]'
    )

    parser.add_argument(
        'output',
        help='Path to output image'
    )

    parser.add_argument(
        'images',
        nargs='+',
        help='Paths to images (at least 2 required)'
    )

    parser.add_argument(
        '--orientation', '-o',
        choices=['vertical', 'horizontal'],
        default='vertical',
        help='Orientation of concatenation (default: vertical)'
    )

    parser.add_argument(
        '--space', '-s',
        type=int,
        default=0,
        help='Pixels of space between images (default: 0)'
    )

    parser.add_argument(
        '--align', '-a',
        choices=['begin', 'center', 'end'],
        default='center',
        help='Alignment: begin (left/top), center, or end (right/bottom) (default: center)'
    )

    parser.add_argument(
        '--background', '-b',
        type=parse_color,
        default=DEFAULT_BACKGROUND,
        help="Background color as R,G,B or R,G,B,A (0-255, clamped) or 'transparent' (default: 255,255,255,255)"
    )

    args = parser.parse_args()

    # Validate at least 2 images
    if len(args.images) < 2:
        parser.error('At least 2 images are required')

    return args


def load_images(image_paths: List[str]) -> List[Image.Image]:
    """Load images from file paths."""
    images = []
    for path in image_paths:
        try:
            img = Image.open(path)
            images.append(img.convert('RGBA'))  # Convert to RGBA for consistency
        except FileNotFoundError:
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error loading {path}: {e}", file=sys.stderr)
            sys.exit(1)

    return images


def calculate_canvas_size(
    images: List[Image.Image],
    orientation: Orientation,
    spacing: int
) -> Tuple[int, int]:
    """Calculate the size of the final canvas."""
    if orientation == 'vertical':
        width = max(img.width for img in images)
        height = sum(img.height for img in images) + spacing * (len(images) - 1)
    else:  # horizontal
        width = sum(img.width for img in images) + spacing * (len(images) - 1)
        height = max(img.height for img in images)

    return width, height


def calculate_position(
    img: Image.Image,
    canvas_width: int,
    canvas_height: int,
    offset: int,
    orientation: Orientation,
    alignment: Alignment
) -> Tuple[int, int]:
    """Calculate the position to paste an image on the canvas."""
    if orientation == 'vertical':
        y = offset
        if alignment == 'begin':
            x = 0
        elif alignment == 'center':
            x = (canvas_width - img.width) // 2
        else:  # end
            x = canvas_width - img.width
        return x, y
    else:  # horizontal
        x = offset
        if alignment == 'begin':
            y = 0
        elif alignment == 'center':
            y = (canvas_height - img.height) // 2
        else:  # end
            y = canvas_height - img.height
        return x, y


def concatenate_images(
    images: List[Image.Image],
    orientation: Orientation,
    spacing: int,
    alignment: Alignment,
    background: Color = DEFAULT_BACKGROUND
) -> Image.Image:
    """Concatenate images according to the specified parameters."""
    canvas_width, canvas_height = calculate_canvas_size(images, orientation, spacing)

    canvas = Image.new('RGBA', (canvas_width, canvas_height), background)

    offset = 0
    for img in images:
        x, y = calculate_position(
            img, canvas_width, canvas_height, offset, orientation, alignment
        )
        canvas.paste(img, (x, y), img)

        if orientation == 'vertical':
            offset += img.height + spacing
        else:  # horizontal
            offset += img.width + spacing

    return canvas


def main() -> None:
    """Main function."""
    args = parse_arguments()

    print(f"Loading {len(args.images)} images...")
    images = load_images(args.images)

    print(f"Concatenating images ({args.orientation}, spacing={args.space}, align={args.align}, bg={args.background})...")
    result = concatenate_images(images, args.orientation, args.space, args.align, args.background)

    # Convert back to RGB for saving (if output format doesn't support alpha)
    output_path = Path(args.output)
    if output_path.suffix.lower() in ['.jpg', '.jpeg']:
        result = result.convert('RGB')

    print(f"Saving to {args.output}...")
    result.save(args.output)

    print(f"Done! Output saved to {args.output}")
    print(f"Final size: {result.width}x{result.height}")


if __name__ == '__main__':
    main()
