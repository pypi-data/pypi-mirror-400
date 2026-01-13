# -*- coding: utf-8 -*-
"""
Prepare training data for Bayer→RGB model.

Takes clean averaged Bayer data and debayers it to create clean RGB targets.
The noisy Bayer (single frames) becomes input, clean RGB becomes target.

@author: MAPIR, Inc
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mip.debayer import debayer_HighQuality


def process_bayer_to_rgb(bayer: np.ndarray) -> np.ndarray:
    """
    Debayer a raw Bayer image to RGB using high-quality algorithm.

    Args:
        bayer: Raw Bayer data [H, W] uint16

    Returns:
        RGB image [H, W, 3] uint16
    """
    # debayer_HighQuality returns [3, H, W] in BGR order
    color_chw = debayer_HighQuality(bayer)

    # Convert to [H, W, 3] RGB
    color_hwc = np.swapaxes(np.swapaxes(color_chw, 0, 2), 0, 1)

    # BGR to RGB
    import cv2
    color_rgb = cv2.cvtColor(color_hwc, cv2.COLOR_BGR2RGB)

    return color_rgb


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Prepare Bayer→RGB training data')
    parser.add_argument('--input', '-i', type=str,
                        default=r'D:\Image_Processing\TESTING\Debayer Noise',
                        help='Base directory with bayer_clean and bayer_noisy folders')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output directory (default: input/clean_rgb)')

    args = parser.parse_args()

    base_dir = args.input
    clean_bayer_dir = os.path.join(base_dir, 'bayer_clean')
    output_rgb_dir = args.output or os.path.join(base_dir, 'clean_rgb')

    # Create output directory
    os.makedirs(output_rgb_dir, exist_ok=True)

    print("=" * 60)
    print("CHLOROS+ Bayer→RGB Training Data Preparation")
    print("=" * 60)
    print(f"\nInput Bayer dir: {clean_bayer_dir}")
    print(f"Output RGB dir: {output_rgb_dir}")

    # Find all clean Bayer files
    bayer_files = sorted([f for f in os.listdir(clean_bayer_dir) if f.endswith('.npy')])
    print(f"\nFound {len(bayer_files)} Bayer files to process")

    # Process each file
    for i, fname in enumerate(bayer_files):
        print(f"\n[{i+1}/{len(bayer_files)}] Processing {fname}...")

        # Load clean Bayer
        bayer_path = os.path.join(clean_bayer_dir, fname)
        bayer = np.load(bayer_path)
        print(f"  Bayer shape: {bayer.shape}, dtype: {bayer.dtype}")

        # Debayer to RGB
        rgb = process_bayer_to_rgb(bayer)
        print(f"  RGB shape: {rgb.shape}, dtype: {rgb.dtype}")

        # Save as .npy (preserves uint16)
        output_path = os.path.join(output_rgb_dir, fname)
        np.save(output_path, rgb)
        print(f"  Saved: {output_path}")

    print("\n" + "=" * 60)
    print("Preparation complete!")
    print("=" * 60)
    print(f"\nTraining data ready:")
    print(f"  Noisy Bayer (input): {os.path.join(base_dir, 'bayer_noisy')}")
    print(f"  Clean RGB (target):  {output_rgb_dir}")
    print(f"\nNext step - train the Bayer→RGB model:")
    print(f'  python train_denoiser.py --bayer2rgb --noisy-bayer-dir "{os.path.join(base_dir, "bayer_noisy")}" --clean-rgb-dir "{output_rgb_dir}" --epochs 150')


if __name__ == '__main__':
    main()
