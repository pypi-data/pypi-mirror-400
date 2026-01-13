#!/usr/bin/env python3
"""
detect_occlusion_regions.py

Detects potential occlusion regions in images using OCR and optional grid overlay.
This script helps Claude generate accurate coordinates for image occlusion cards
without relying on LLM coordinate estimation (which is notoriously inaccurate).

Usage:
    python3 detect_occlusion_regions.py <image_path> [options]

Options:
    --grid          Generate a gridded version of the image for manual selection
    --json          Output results as JSON only (no human-readable summary)
    --output DIR    Directory to save output files (default: same as input image)
    --min-conf N    Minimum OCR confidence threshold 0-100 (default: 60)
    --preview       Generate a preview image with detected regions highlighted

Examples:
    # Basic OCR detection
    python3 detect_occlusion_regions.py heart_anatomy.jpg
    
    # With grid overlay for unlabeled images
    python3 detect_occlusion_regions.py europe_map.png --grid
    
    # JSON output for programmatic use
    python3 detect_occlusion_regions.py diagram.jpg --json
    
    # Generate preview with bounding boxes
    python3 detect_occlusion_regions.py anatomy.jpg --preview
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import pytesseract


def get_image_dimensions(image_path: str) -> tuple[int, int]:
    """Get image width and height."""
    with Image.open(image_path) as img:
        return img.size  # (width, height)


def detect_text_regions(image_path: str, min_confidence: int = 60) -> list[dict]:
    """
    Use Tesseract OCR to detect text regions and their bounding boxes.
    
    Returns a list of detected regions with:
    - text: The detected text
    - confidence: OCR confidence score (0-100)
    - left, top, width, height: Normalized coordinates (0-1)
    - pixel_left, pixel_top, pixel_width, pixel_height: Absolute pixel coordinates
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # Get detailed OCR data including bounding boxes
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    regions = []
    n_boxes = len(ocr_data['text'])
    
    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()
        conf = int(ocr_data['conf'][i])
        
        # Skip empty text or low confidence detections
        if not text or conf < min_confidence:
            continue
        
        # Get pixel coordinates
        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        w = ocr_data['width'][i]
        h = ocr_data['height'][i]
        
        # Skip tiny detections (likely noise)
        if w < 10 or h < 10:
            continue
        
        # Convert to normalized coordinates (0-1)
        regions.append({
            'text': text,
            'confidence': conf / 100.0,
            'left': round(x / width, 4),
            'top': round(y / height, 4),
            'width': round(w / width, 4),
            'height': round(h / height, 4),
            'pixel_left': x,
            'pixel_top': y,
            'pixel_width': w,
            'pixel_height': h,
            'source': 'ocr'
        })
    
    return regions


def merge_adjacent_regions(regions: list[dict], 
                          vertical_threshold: float = 0.06,
                          horizontal_threshold: float = 0.15) -> list[dict]:
    """
    Merge text regions that are likely part of the same label.
    
    For example, "Left" and "Atrium" on separate lines should become "Left Atrium".
    
    Uses a more aggressive merging strategy:
    - Vertically: regions within 6% of image height are candidates
    - Horizontally: regions within 15% horizontal distance are candidates
    """
    if not regions:
        return regions
    
    # Keep merging until no more merges are possible
    merged = True
    current_regions = [r.copy() for r in regions]
    
    while merged:
        merged = False
        new_regions = []
        used = set()
        
        # Sort by position for consistent processing
        current_regions = sorted(current_regions, key=lambda r: (r['top'], r['left']))
        
        for i, r1 in enumerate(current_regions):
            if i in used:
                continue
            
            current = r1.copy()
            
            for j, r2 in enumerate(current_regions):
                if j <= i or j in used:
                    continue
                
                # Calculate centers
                r1_center_x = current['left'] + current['width'] / 2
                r1_center_y = current['top'] + current['height'] / 2
                r2_center_x = r2['left'] + r2['width'] / 2
                r2_center_y = r2['top'] + r2['height'] / 2
                
                # Check horizontal alignment (centers within threshold)
                horizontal_distance = abs(r1_center_x - r2_center_x)
                
                # Check vertical proximity
                vertical_gap = abs(r2['top'] - (current['top'] + current['height']))
                
                # Also check if one is directly below the other
                horizontally_aligned = horizontal_distance < horizontal_threshold
                vertically_close = vertical_gap < vertical_threshold
                
                if horizontally_aligned and vertically_close:
                    # Merge: expand bounding box and concatenate text
                    new_left = min(current['left'], r2['left'])
                    new_top = min(current['top'], r2['top'])
                    new_right = max(current['left'] + current['width'], r2['left'] + r2['width'])
                    new_bottom = max(current['top'] + current['height'], r2['top'] + r2['height'])
                    
                    # Determine text order (top one first)
                    if current['top'] < r2['top']:
                        current['text'] = current['text'] + ' ' + r2['text']
                    else:
                        current['text'] = r2['text'] + ' ' + current['text']
                    
                    current['left'] = round(new_left, 4)
                    current['top'] = round(new_top, 4)
                    current['width'] = round(new_right - new_left, 4)
                    current['height'] = round(new_bottom - new_top, 4)
                    current['confidence'] = min(current['confidence'], r2['confidence'])
                    
                    used.add(j)
                    merged = True
            
            new_regions.append(current)
            used.add(i)
        
        current_regions = new_regions
    
    return current_regions


def generate_grid_image(image_path: str, output_path: str, grid_size: int = 10) -> str:
    """
    Generate a version of the image with a labeled grid overlay.
    
    Grid uses:
    - Rows: A-J (or more for larger grids)
    - Columns: 1-10 (or more for larger grids)
    """
    img = Image.open(image_path).convert('RGBA')
    width, height = img.size
    
    # Create overlay for grid
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Grid line settings
    line_color = (0, 0, 0, 77)  # Black with ~30% opacity (0.3 * 255 ≈ 77)
    label_color = (0, 0, 0, 200)  # Darker for labels
    
    cell_width = width / grid_size
    cell_height = height / grid_size
    
    # Try to get a font, fall back to default if not available
    try:
        font_size = max(12, min(width, height) // 40)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()
    
    # Draw vertical lines and column numbers
    for i in range(grid_size + 1):
        x = int(i * cell_width)
        draw.line([(x, 0), (x, height)], fill=line_color, width=2)
        
        # Column labels (1-10) at top
        if i < grid_size:
            label = str(i + 1)
            label_x = int(i * cell_width + cell_width / 2 - font_size / 2)
            draw.text((label_x, 5), label, fill=label_color, font=font)
    
    # Draw horizontal lines and row letters
    row_labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i in range(grid_size + 1):
        y = int(i * cell_height)
        draw.line([(0, y), (width, y)], fill=line_color, width=2)
        
        # Row labels (A-J) at left
        if i < grid_size:
            label = row_labels[i]
            label_y = int(i * cell_height + cell_height / 2 - font_size / 2)
            draw.text((5, label_y), label, fill=label_color, font=font)
    
    # Composite the overlay onto the original image
    result = Image.alpha_composite(img, overlay)
    result = result.convert('RGB')
    result.save(output_path, quality=95)
    
    return output_path


def generate_preview_image(image_path: str, regions: list[dict], output_path: str) -> str:
    """
    Generate a preview image with detected regions highlighted.
    """
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    # Colors for different regions
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 128, 0),  # Orange
        (128, 0, 255),  # Purple
    ]
    
    try:
        font_size = max(10, min(width, height) // 50)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()
    
    for i, region in enumerate(regions):
        color = colors[i % len(colors)]
        
        # Convert normalized coords back to pixels
        x = int(region['left'] * width)
        y = int(region['top'] * height)
        w = int(region['width'] * width)
        h = int(region['height'] * height)
        
        # Draw rectangle
        draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
        
        # Draw label above the box
        label = f"{i+1}: {region['text']}"
        draw.text((x, max(0, y - font_size - 2)), label, fill=color, font=font)
    
    img.save(output_path, quality=95)
    return output_path


def grid_ref_to_coords(grid_ref: str, grid_size: int = 10) -> dict:
    """
    Convert a grid reference like "D4" or "D4-E5" to normalized coordinates.
    
    Single cell: "D4" -> coordinates for cell D4
    Range: "D4-E5" -> coordinates spanning from D4 to E5
    """
    grid_ref = grid_ref.upper().strip()
    
    if '-' in grid_ref:
        # Range reference like "D4-E5"
        start, end = grid_ref.split('-')
        start_coords = grid_ref_to_coords(start, grid_size)
        end_coords = grid_ref_to_coords(end, grid_size)
        
        return {
            'left': start_coords['left'],
            'top': start_coords['top'],
            'width': round(end_coords['left'] + end_coords['width'] - start_coords['left'], 4),
            'height': round(end_coords['top'] + end_coords['height'] - start_coords['top'], 4),
            'source': 'grid'
        }
    
    # Single cell reference like "D4"
    row_letter = grid_ref[0]
    col_number = int(grid_ref[1:])
    
    row_index = ord(row_letter) - ord('A')
    col_index = col_number - 1
    
    return {
        'left': round(col_index / grid_size, 4),
        'top': round(row_index / grid_size, 4),
        'width': round(1 / grid_size, 4),
        'height': round(1 / grid_size, 4),
        'source': 'grid'
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Detect occlusion regions in images using OCR and grid overlay.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('image_path', help='Path to the input image')
    parser.add_argument('--grid', action='store_true', 
                        help='Generate a gridded version of the image')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON only')
    parser.add_argument('--output', '-o', default=None,
                        help='Output directory (default: same as input)')
    parser.add_argument('--min-conf', type=int, default=60,
                        help='Minimum OCR confidence threshold 0-100 (default: 60)')
    parser.add_argument('--preview', action='store_true',
                        help='Generate preview image with detected regions highlighted')
    parser.add_argument('--grid-size', type=int, default=10,
                        help='Grid size NxN (default: 10)')
    
    args = parser.parse_args(argv)
    
    # Validate input
    if not os.path.exists(args.image_path):
        print(f"Error: Image not found: {args.image_path}", file=sys.stderr)
        return 1
    
    # Set up output directory
    image_path = Path(args.image_path)
    output_dir = Path(args.output) if args.output else image_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get image dimensions
    width, height = get_image_dimensions(args.image_path)
    
    # Detect text regions with OCR
    regions = detect_text_regions(args.image_path, args.min_conf)
    
    # Merge adjacent regions that are likely the same label
    regions = merge_adjacent_regions(regions)
    
    # Build result object
    result = {
        'image_path': str(image_path.absolute()),
        'image_width': width,
        'image_height': height,
        'detected_regions': regions,
        'detection_method': 'ocr',
        'ocr_min_confidence': args.min_conf / 100.0
    }
    
    # Generate grid image if requested
    if args.grid:
        grid_filename = f"{image_path.stem}_grid{image_path.suffix}"
        grid_path = output_dir / grid_filename
        generate_grid_image(args.image_path, str(grid_path), args.grid_size)
        result['grid_image_path'] = str(grid_path.absolute())
        result['grid_size'] = args.grid_size
    
    # Generate preview image if requested
    if args.preview and regions:
        preview_filename = f"{image_path.stem}_preview{image_path.suffix}"
        preview_path = output_dir / preview_filename
        generate_preview_image(args.image_path, regions, str(preview_path))
        result['preview_image_path'] = str(preview_path.absolute())
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"Image Occlusion Region Detection")
        print(f"{'='*60}")
        print(f"Image: {image_path.name}")
        print(f"Dimensions: {width} x {height} pixels")
        print(f"Detected {len(regions)} text region(s)")
        
        if regions:
            print(f"\n{'─'*60}")
            print("Detected Labels:")
            print(f"{'─'*60}")
            for i, region in enumerate(regions, 1):
                conf_pct = int(region['confidence'] * 100)
                print(f"\n  [{i}] \"{region['text']}\" (confidence: {conf_pct}%)")
                print(f"      Position: left={region['left']:.3f}, top={region['top']:.3f}")
                print(f"      Size: width={region['width']:.3f}, height={region['height']:.3f}")
        else:
            print("\n  No text labels detected.")
            print("  Consider using --grid flag for manual region selection.")
        
        if args.grid:
            print(f"\n{'─'*60}")
            print(f"Grid image saved to: {result['grid_image_path']}")
            print(f"Grid size: {args.grid_size}x{args.grid_size}")
            print("\nTo select regions by grid reference:")
            print("  - Single cell: 'D4'")
            print("  - Range: 'D4-E5'")
        
        if args.preview and regions:
            print(f"\n{'─'*60}")
            print(f"Preview image saved to: {result['preview_image_path']}")
        
        print(f"\n{'='*60}")
        print("JSON output (for programmatic use):")
        print(f"{'='*60}")
        print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
