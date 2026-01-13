# -*- coding: utf-8 -*-
"""
CHLOROS+ Training Data Processor

Processes RAW+JPG image pairs into clean/noisy training pairs for denoising.

WORKFLOW:
1. Capture bursts of 16-32 images of each scene (same exposure)
2. Place all images in the training_data folder
3. Run this script to automatically group by timestamp and create pairs
4. Train with: python train_denoiser.py --clean-dir ... --noisy-dir ...

@author: MAPIR, Inc
"""

import os
import sys
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import cv2

# Add project root for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def get_image_timestamp(path):
    """Extract timestamp from image EXIF data."""
    from PIL import Image
    from PIL.ExifTags import TAGS

    try:
        # Try JPG first (has EXIF)
        jpg_path = path
        if path.lower().endswith('.raw'):
            jpg_path = path[:-4] + '.JPG'
            if not os.path.exists(jpg_path):
                jpg_path = path[:-4] + '.jpg'

        if os.path.exists(jpg_path):
            img = Image.open(jpg_path)
            exif = img.getexif()
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTime' or tag == 'DateTimeOriginal':
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"  Warning: Could not read EXIF from {path}: {e}")

    # Fallback to file modification time
    return datetime.fromtimestamp(os.path.getmtime(path))


def find_companion_jpg(raw_path):
    """Find the companion JPG for a RAW file."""
    directory = os.path.dirname(raw_path)
    raw_basename = os.path.basename(raw_path)
    raw_name = os.path.splitext(raw_basename)[0]

    # Try exact name match first
    for ext in ['.JPG', '.jpg']:
        jpg_path = os.path.join(directory, raw_name + ext)
        if os.path.exists(jpg_path):
            return jpg_path

    # Try finding JPG with next sequence number (MAPIR pattern)
    # e.g., RAW is _015.RAW, JPG might be _016.JPG
    parts = raw_name.rsplit('_', 1)
    if len(parts) == 2 and parts[1].isdigit():
        prefix = parts[0]
        seq_num = int(parts[1])

        # Check +1 and -1 sequence numbers
        for offset in [1, -1]:
            next_seq = f"{prefix}_{seq_num + offset:03d}"
            for ext in ['.JPG', '.jpg']:
                jpg_path = os.path.join(directory, next_seq + ext)
                if os.path.exists(jpg_path):
                    return jpg_path

    # Try finding any JPG with similar timestamp
    raw_timestamp = raw_name[:17]  # e.g., "2025_1230_222517"
    for f in os.listdir(directory):
        if f.lower().endswith('.jpg') and f.startswith(raw_timestamp[:15]):
            return os.path.join(directory, f)

    return None


def load_raw_image(raw_path, jpg_path=None):
    """Load and debayer a RAW image using MAPIR's processing."""
    try:
        from mip.image import MCCImage

        # Find companion JPG if not provided
        if jpg_path is None:
            jpg_path = find_companion_jpg(raw_path)

        if jpg_path is None:
            print(f"  Warning: No companion JPG found for {os.path.basename(raw_path)}")

        # Create MCCImage and load data
        img = MCCImage(raw_path, jpgpath=jpg_path)
        data = img.data  # This triggers loading and debayering

        return data  # Returns HWC uint16 RGB

    except Exception as e:
        print(f"  Error loading {raw_path}: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_image(path):
    """Load any image file (RAW, TIFF, JPG)."""
    ext = os.path.splitext(path)[1].lower()

    if ext == '.raw':
        # Find companion JPG for EXIF
        jpg_path = path[:-4] + '.JPG'
        if not os.path.exists(jpg_path):
            jpg_path = path[:-4] + '.jpg'
        if not os.path.exists(jpg_path):
            jpg_path = None
        return load_raw_image(path, jpg_path)

    elif ext in ['.tif', '.tiff']:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    elif ext in ['.jpg', '.jpeg', '.png']:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Convert to uint16 if uint8
            if img.dtype == np.uint8:
                img = img.astype(np.uint16) * 257
        return img

    return None


def group_images_by_scene(image_files, max_gap_seconds=3):
    """
    Group images into scenes based on timestamp proximity.

    Images captured within max_gap_seconds of each other are considered
    part of the same burst/scene.
    """
    if not image_files:
        return []

    # Get timestamps for all images
    images_with_time = []
    for path in image_files:
        timestamp = get_image_timestamp(path)
        images_with_time.append((path, timestamp))

    # Sort by timestamp
    images_with_time.sort(key=lambda x: x[1])

    # Group by time proximity
    scenes = []
    current_scene = [images_with_time[0]]

    for i in range(1, len(images_with_time)):
        path, timestamp = images_with_time[i]
        prev_timestamp = current_scene[-1][1]

        gap = (timestamp - prev_timestamp).total_seconds()

        if gap <= max_gap_seconds:
            # Same scene
            current_scene.append((path, timestamp))
        else:
            # New scene
            if len(current_scene) >= 2:  # Need at least 2 for averaging
                scenes.append(current_scene)
            current_scene = [(path, timestamp)]

    # Don't forget the last scene
    if len(current_scene) >= 2:
        scenes.append(current_scene)

    return scenes


def process_scene(scene_images, scene_name, output_clean_dir, output_noisy_dir,
                  min_frames=4, max_frames=32):
    """
    Process a scene's images into clean/noisy pair.

    - Average all frames (up to max_frames) for CLEAN
    - Use first frame as NOISY
    """
    print(f"\n  Processing scene: {scene_name}")
    print(f"    Frames available: {len(scene_images)}")

    # Limit frames
    frames_to_use = scene_images[:max_frames]

    if len(frames_to_use) < min_frames:
        print(f"    Skipping: need at least {min_frames} frames")
        return False

    # Load all frames
    loaded_frames = []
    for path, timestamp in frames_to_use:
        print(f"    Loading: {os.path.basename(path)}")
        img = load_image(path)
        if img is not None:
            loaded_frames.append(img.astype(np.float64))

    if len(loaded_frames) < min_frames:
        print(f"    Skipping: only {len(loaded_frames)} frames loaded successfully")
        return False

    print(f"    Averaging {len(loaded_frames)} frames...")

    # Average for clean reference
    clean = np.mean(loaded_frames, axis=0)

    # First frame as noisy sample
    noisy = loaded_frames[0]

    # Convert back to uint16
    clean = np.clip(clean, 0, 65535).astype(np.uint16)
    noisy = np.clip(noisy, 0, 65535).astype(np.uint16)

    # Calculate noise reduction achieved
    # Compare variance in a flat region (center crop)
    h, w = clean.shape[:2]
    crop = slice(h//3, 2*h//3), slice(w//3, 2*w//3)

    noisy_std = np.std(noisy[crop].astype(float))
    clean_std = np.std(clean[crop].astype(float))

    theoretical_reduction = np.sqrt(len(loaded_frames))
    actual_reduction = noisy_std / max(clean_std, 1)

    print(f"    Noise reduction: {actual_reduction:.1f}x (theoretical: {theoretical_reduction:.1f}x)")

    # Save
    clean_path = os.path.join(output_clean_dir, f"{scene_name}.tif")
    noisy_path = os.path.join(output_noisy_dir, f"{scene_name}.tif")

    # Convert RGB to BGR for OpenCV saving
    cv2.imwrite(clean_path, cv2.cvtColor(clean, cv2.COLOR_RGB2BGR))
    cv2.imwrite(noisy_path, cv2.cvtColor(noisy, cv2.COLOR_RGB2BGR))

    print(f"    Saved: {scene_name}.tif")

    return True


def process_training_data(input_dir, output_dir=None, max_gap_seconds=3,
                          min_frames=4, max_frames=32):
    """
    Main processing function.

    Args:
        input_dir: Directory containing RAW+JPG image pairs
        output_dir: Output directory (default: input_dir parent)
        max_gap_seconds: Max time between frames to be considered same scene
        min_frames: Minimum frames needed per scene
        max_frames: Maximum frames to use for averaging
    """
    print("=" * 60)
    print("CHLOROS+ Training Data Processor")
    print("=" * 60)

    # Setup directories
    if output_dir is None:
        output_dir = os.path.dirname(input_dir)

    output_clean_dir = os.path.join(output_dir, 'clean')
    output_noisy_dir = os.path.join(output_dir, 'noisy')

    os.makedirs(output_clean_dir, exist_ok=True)
    os.makedirs(output_noisy_dir, exist_ok=True)

    print(f"\nInput directory: {input_dir}")
    print(f"Output clean: {output_clean_dir}")
    print(f"Output noisy: {output_noisy_dir}")

    # Find all RAW files (primary) or TIF files
    raw_files = []
    for f in os.listdir(input_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext == '.raw':
            raw_files.append(os.path.join(input_dir, f))
        elif ext in ['.tif', '.tiff'] and not raw_files:
            # Only use TIF if no RAW files found
            raw_files.append(os.path.join(input_dir, f))

    if not raw_files:
        print("\nERROR: No RAW or TIF files found in input directory")
        return False

    print(f"\nFound {len(raw_files)} image files")

    # Group by scene
    print(f"\nGrouping images (max {max_gap_seconds}s gap)...")
    scenes = group_images_by_scene(raw_files, max_gap_seconds)

    print(f"Found {len(scenes)} scenes:")
    for i, scene in enumerate(scenes):
        start_time = scene[0][1].strftime('%H:%M:%S')
        print(f"  Scene {i+1}: {len(scene)} frames starting at {start_time}")

    # Process each scene
    print("\n" + "-" * 60)
    print("Processing scenes...")
    print("-" * 60)

    successful = 0
    for i, scene in enumerate(scenes):
        scene_name = f"scene_{i+1:03d}"
        if process_scene(scene, scene_name, output_clean_dir, output_noisy_dir,
                        min_frames, max_frames):
            successful += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"  Scenes processed: {successful}/{len(scenes)}")
    print(f"  Clean images: {output_clean_dir}")
    print(f"  Noisy images: {output_noisy_dir}")
    print("=" * 60)

    if successful > 0:
        print(f"""
NEXT STEP - Train the model:

  python train_denoiser.py --clean-dir "{output_clean_dir}" --noisy-dir "{output_noisy_dir}" --epochs 100

For faster initial test (fewer epochs):

  python train_denoiser.py --clean-dir "{output_clean_dir}" --noisy-dir "{output_noisy_dir}" --epochs 20
""")

    return successful > 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Process RAW image bursts into clean/noisy training pairs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process images from default training_data folder
  python process_training_data.py

  # Process from custom folder
  python process_training_data.py --input "C:/path/to/images"

  # Adjust grouping parameters
  python process_training_data.py --max-gap 5 --min-frames 8
"""
    )

    default_input = r"C:\Users\MAPIR\Chloros Projects\training_data"

    parser.add_argument('--input', '-i', type=str, default=default_input,
                        help=f'Input directory with RAW+JPG pairs (default: {default_input})')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output directory (default: same as input parent)')
    parser.add_argument('--max-gap', type=float, default=3.0,
                        help='Max seconds between frames in same scene (default: 3)')
    parser.add_argument('--min-frames', type=int, default=4,
                        help='Minimum frames per scene (default: 4)')
    parser.add_argument('--max-frames', type=int, default=32,
                        help='Maximum frames to average (default: 32)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Input directory does not exist: {args.input}")
        print("\nCreate the directory and add your captured images, then run again.")
        return

    process_training_data(
        input_dir=args.input,
        output_dir=args.output,
        max_gap_seconds=args.max_gap,
        min_frames=args.min_frames,
        max_frames=args.max_frames
    )


if __name__ == '__main__':
    main()
