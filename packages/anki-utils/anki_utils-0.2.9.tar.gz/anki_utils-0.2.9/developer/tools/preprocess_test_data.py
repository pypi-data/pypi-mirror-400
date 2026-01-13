#!/usr/bin/env python3
"""
Preprocess test data JSON to convert image paths to base64 data URLs.

In an iframe using srcDoc, relative file paths cannot resolve because there's
no base URL context. This script converts image_path and photo_path fields
to image_data and photo_data fields containing base64 data URLs.

Usage:
    python3 preprocess_test_data.py <json_file> [base_dir]
    
    base_dir defaults to the directory containing the json file
    
Output:
    Prints modified JSON to stdout with paths converted to base64
"""

import sys
import os
import json
import base64
import mimetypes
from PIL import Image

def get_mime_type(file_path):
    """Get MIME type for a file based on extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # Default to PNG for images without a recognized extension
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
            ext = file_path.lower().split('.')[-1]
            mime_map = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'svg': 'image/svg+xml'
            }
            return mime_map.get(ext, 'image/png')
        return 'application/octet-stream'
    return mime_type

def file_to_base64_data_url(file_path):
    """Convert a file to a base64 data URL."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        mime_type = get_mime_type(file_path)
        b64 = base64.b64encode(data).decode('utf-8')
        return f"data:{mime_type};base64,{b64}"
    except FileNotFoundError:
        print(f"Warning: Image file not found: {file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Error reading {file_path}: {e}", file=sys.stderr)
        return None

def get_image_dimensions(file_path):
    """Get width and height of an image file."""
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except Exception as e:
        print(f"Warning: Could not get dimensions for {file_path}: {e}", file=sys.stderr)
        return None, None

def resolve_path(path, base_dir):
    """Resolve a path relative to base_dir."""
    if os.path.isabs(path):
        return path
    # Try multiple resolution strategies
    candidates = [
        os.path.join(base_dir, path),
        os.path.join(base_dir, '..', '..', path),  # From test-data to skill root
        path  # Absolute or already correct
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return os.path.join(base_dir, path)  # Default

def process_card(card, base_dir):
    """Process a single card, converting paths to base64 and extracting dimensions."""
    card = card.copy()  # Don't mutate original
    
    # Process image_path -> image_data + image_width/image_height
    if 'image_path' in card and card['image_path']:
        resolved_path = resolve_path(card['image_path'], base_dir)
        data_url = file_to_base64_data_url(resolved_path)
        if data_url:
            card['image_data'] = data_url
            # Extract dimensions for image-occlusion cards
            width, height = get_image_dimensions(resolved_path)
            if width and height:
                card['image_width'] = width
                card['image_height'] = height
    
    # Process photo_path -> photo_data
    if 'photo_path' in card and card['photo_path']:
        resolved_path = resolve_path(card['photo_path'], base_dir)
        data_url = file_to_base64_data_url(resolved_path)
        if data_url:
            card['photo_data'] = data_url
    
    return card

def process_json(data, base_dir):
    """Process the entire JSON structure."""
    data = data.copy()
    if 'cards' in data:
        data['cards'] = [process_card(card, base_dir) for card in data['cards']]
    return data

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 preprocess_test_data.py <json_file> [base_dir]", file=sys.stderr)
        sys.exit(1)
    
    json_file = sys.argv[1]
    base_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(json_file)
    
    # If base_dir is empty, use current directory
    if not base_dir:
        base_dir = '.'
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        sys.exit(1)
    
    processed = process_json(data, base_dir)
    
    # Output as single line for sed compatibility
    print(json.dumps(processed))

if __name__ == '__main__':
    main()
