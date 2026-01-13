# -*- coding: utf-8 -*-
"""
Process RAW files into Bayer training pairs (without debayering).

This creates clean/noisy pairs from raw Bayer data for training
a denoiser that works BEFORE the debayer step.

@author: MAPIR, Inc
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_raw_bayer(raw_path, jpg_path=None):
    """
    Load raw Bayer data without debayering.

    Returns single-channel uint16 Bayer pattern.
    Uses direct decoding without MCCImage dependency.
    """
    import copy

    try:
        # Read raw file and decode MAPIR 12-bit packed format
        # This is the same decoding logic from mip/image.py
        data = np.fromfile(raw_path, dtype=np.uint8)
        data = np.unpackbits(data)
        datsize = data.shape[0]
        data = data.reshape((int(datsize / 4), 4))

        # Switch even rows and odd rows
        temp = copy.deepcopy(data[0::2])
        temp2 = copy.deepcopy(data[1::2])
        data[0::2] = temp2
        data[1::2] = temp

        # Repack into image file
        udata = np.packbits(np.concatenate([
            data[0::3],
            np.zeros((12000000, 4), dtype=np.uint8),
            data[2::3],
            data[1::3]
        ], axis=1).reshape(192000000, 1)).tobytes()

        # Create uint16 Bayer image (3000x4000 for MAPIR Chloros+)
        img = np.frombuffer(udata, np.dtype('u2'), (4000 * 3000)).reshape((3000, 4000))

        return img

    except Exception as e:
        print(f"  Error loading {raw_path}: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_scene_folder_bayer(folder_path, scene_name, output_clean_dir, output_noisy_dir, max_frames=32):
    """Process a single scene folder into Bayer clean/noisy pair."""
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

    # Load all frames as raw Bayer
    loaded_frames = []
    for fname in raw_files:
        raw_path = os.path.join(folder_path, fname)
        print(f"    Loading Bayer: {fname}")
        bayer = load_raw_bayer(raw_path)
        if bayer is not None:
            loaded_frames.append(bayer.astype(np.float64))

    if len(loaded_frames) < 4:
        print(f"  Skipping: only {len(loaded_frames)} frames loaded successfully")
        return False

    print(f"  Averaging {len(loaded_frames)} Bayer frames...")

    # Average for clean reference (in Bayer space)
    clean = np.mean(loaded_frames, axis=0)

    # First frame as noisy sample
    noisy = loaded_frames[0]

    # Convert back to uint16
    clean = np.clip(clean, 0, 65535).astype(np.uint16)
    noisy = np.clip(noisy, 0, 65535).astype(np.uint16)

    # Save as numpy arrays (preserves exact Bayer pattern)
    clean_path = os.path.join(output_clean_dir, f"{scene_name}.npy")
    noisy_path = os.path.join(output_noisy_dir, f"{scene_name}.npy")

    np.save(clean_path, clean)
    np.save(noisy_path, noisy)

    print(f"  Saved: {scene_name}.npy (shape: {clean.shape}, {len(loaded_frames)} frames averaged)")

    # Calculate noise reduction achieved
    noisy_std = np.std(noisy.astype(float))
    clean_std = np.std(clean.astype(float))
    theoretical_reduction = np.sqrt(len(loaded_frames))

    print(f"  Noise std: {noisy_std:.1f} -> {clean_std:.1f} (theoretical: {noisy_std/theoretical_reduction:.1f})")

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process RAW files into Bayer training pairs')
    parser.add_argument('--input', '-i', type=str,
                        default=r'D:\Image_Processing\TESTING\Debayer Noise',
                        help='Base directory with numbered scene folders')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output directory (default: input/bayer_clean and input/bayer_noisy)')
    parser.add_argument('--max-frames', type=int, default=32,
                        help='Maximum frames to average per scene')

    args = parser.parse_args()

    base_dir = args.input
    output_dir = args.output or base_dir

    output_clean = os.path.join(output_dir, 'bayer_clean')
    output_noisy = os.path.join(output_dir, 'bayer_noisy')

    # Create output directories
    os.makedirs(output_clean, exist_ok=True)
    os.makedirs(output_noisy, exist_ok=True)

    # Clear old files
    for d in [output_clean, output_noisy]:
        for f in os.listdir(d):
            if f.endswith('.npy'):
                os.remove(os.path.join(d, f))

    # Find numbered folders
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and f.isdigit()]
    folders.sort(key=int)

    print("=" * 60)
    print("CHLOROS+ Bayer Training Data Processor")
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

        if process_scene_folder_bayer(folder_path, scene_name, output_clean, output_noisy, args.max_frames):
            successful += 1

    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"  Scenes processed: {successful}/{len(folders)}")
    print(f"  Clean Bayer: {output_clean}")
    print(f"  Noisy Bayer: {output_noisy}")
    print("=" * 60)

    if successful > 0:
        print(f"""
NEXT STEP - Train the Bayer denoiser:

  python train_denoiser.py --bayer --clean-dir "{output_clean}" --noisy-dir "{output_noisy}" --epochs 100

""")


if __name__ == '__main__':
    main()
