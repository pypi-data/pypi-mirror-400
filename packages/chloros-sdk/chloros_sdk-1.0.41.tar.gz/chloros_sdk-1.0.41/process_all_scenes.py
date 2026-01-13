# -*- coding: utf-8 -*-
"""
Process all numbered scene folders into training pairs.
Each folder = one scene (all frames averaged for clean)
"""

import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from process_training_data import load_image, find_companion_jpg


def process_scene_folder(folder_path, scene_name, output_clean_dir, output_noisy_dir, max_frames=32):
    """Process a single scene folder."""
    print(f"\n{'='*60}")
    print(f"Processing: {scene_name}")
    print(f"{'='*60}")

    # Find all RAW files
    raw_files = sorted([f for f in os.listdir(folder_path) if f.upper().endswith('.RAW')])

    if len(raw_files) < 4:
        print(f"  Skipping: only {len(raw_files)} RAW files (need at least 4)")
        return False

    print(f"  Found {len(raw_files)} RAW files")

    # Limit frames
    raw_files = raw_files[:max_frames]
    print(f"  Using {len(raw_files)} frames for averaging")

    # Load all frames
    loaded_frames = []
    for fname in raw_files:
        raw_path = os.path.join(folder_path, fname)
        print(f"    Loading: {fname}")
        img = load_image(raw_path)
        if img is not None:
            loaded_frames.append(img.astype(np.float64))

    if len(loaded_frames) < 4:
        print(f"  Skipping: only {len(loaded_frames)} frames loaded successfully")
        return False

    print(f"  Averaging {len(loaded_frames)} frames...")

    # Average for clean reference
    clean = np.mean(loaded_frames, axis=0)

    # First frame as noisy sample
    noisy = loaded_frames[0]

    # Convert back to uint16
    clean = np.clip(clean, 0, 65535).astype(np.uint16)
    noisy = np.clip(noisy, 0, 65535).astype(np.uint16)

    # Save
    clean_path = os.path.join(output_clean_dir, f"{scene_name}.tif")
    noisy_path = os.path.join(output_noisy_dir, f"{scene_name}.tif")

    cv2.imwrite(clean_path, cv2.cvtColor(clean, cv2.COLOR_RGB2BGR))
    cv2.imwrite(noisy_path, cv2.cvtColor(noisy, cv2.COLOR_RGB2BGR))

    print(f"  Saved: {scene_name}.tif ({len(loaded_frames)} frames averaged)")

    return True


def main():
    base_dir = r'D:\Image_Processing\TESTING\Debayer Noise'
    output_clean = os.path.join(base_dir, 'clean')
    output_noisy = os.path.join(base_dir, 'noisy')

    # Create output directories
    os.makedirs(output_clean, exist_ok=True)
    os.makedirs(output_noisy, exist_ok=True)

    # Clear old files
    for d in [output_clean, output_noisy]:
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))

    # Find numbered folders
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and f.isdigit()]
    folders.sort(key=int)

    print("=" * 60)
    print("CHLOROS+ Batch Scene Processor")
    print("=" * 60)
    print(f"\nBase directory: {base_dir}")
    print(f"Found {len(folders)} scene folders")
    print(f"Output clean: {output_clean}")
    print(f"Output noisy: {output_noisy}")

    # Process each folder
    successful = 0
    for folder_name in folders:
        folder_path = os.path.join(base_dir, folder_name)
        scene_name = f"scene_{int(folder_name):03d}"

        if process_scene_folder(folder_path, scene_name, output_clean, output_noisy):
            successful += 1

    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"  Scenes processed: {successful}/{len(folders)}")
    print(f"  Clean images: {output_clean}")
    print(f"  Noisy images: {output_noisy}")
    print("=" * 60)

    if successful > 0:
        print(f"""
NEXT STEP - Train the model:

  python train_denoiser.py --clean-dir "{output_clean}" --noisy-dir "{output_noisy}" --epochs 100
""")


if __name__ == '__main__':
    main()
