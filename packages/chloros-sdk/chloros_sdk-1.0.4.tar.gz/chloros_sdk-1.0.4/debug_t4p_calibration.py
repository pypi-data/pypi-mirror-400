#!/usr/bin/env python3
"""
T4P Calibration Target Diagnostic Script
=========================================
This script analyzes T4P calibration targets to identify why NDVI values
are compressed (0-0.4 instead of expected 0.2-0.9).

Author: MAPIR, Inc
"""

import os
import sys
import cv2
import numpy as np

# Add the mip module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mip.spectra import (
    target_reflectance_spectra_t3,
    target_reflectance_spectra_t4,
    filter_transmission_spectra,
    T3_ARUCO_IDS,
    T4P_ARUCO_IDS,
    T3_PANEL_NAMES,
    T4P_PANEL_NAMES,
    get_target_type
)
from mip.Calibration_Utils import refvalues_lut
from mip.Calibration_Target import (
    detect_calibration_targets,
    calibration_target_polys,
    calibration_target_values,
    target_dimensions
)

def analyze_reflectance_spectra():
    """Compare T3 vs T4 reflectance spectra"""
    print("\n" + "="*80)
    print("ANALYSIS 1: Comparing T3 vs T4 Reflectance Spectra")
    print("="*80)
    
    # T3 colors
    t3_colors = ['white', 'light_grey', 'silver_grey', 'dark_grey']
    print("\nT3 Target Reflectance (mean values across spectrum):")
    for color in t3_colors:
        spectrum = target_reflectance_spectra_t3[color]
        print(f"  {color:15s}: {np.mean(spectrum):.4f} (min: {np.min(spectrum):.4f}, max: {np.max(spectrum):.4f})")
    
    # T4 colors
    t4_colors = ['pft_94', 'pft_80', 'pft_50', 'pft_18']
    print("\nT4 Target Reflectance (mean values across spectrum):")
    for color in t4_colors:
        spectrum = target_reflectance_spectra_t4[color]
        print(f"  {color:15s}: {np.mean(spectrum):.4f} (min: {np.min(spectrum):.4f}, max: {np.max(spectrum):.4f})")
    
    print("\n" + "-"*80)
    print("Key Differences:")
    print("-"*80)
    
    # Compare equivalent panels
    comparisons = [
        ('white', 'pft_94', 'Brightest panel'),
        ('light_grey', 'pft_80', 'Second brightest'),
        ('silver_grey', 'pft_50', 'Third panel'),
        ('dark_grey', 'pft_18', 'Darkest panel'),
    ]
    
    for t3_name, t4_name, desc in comparisons:
        t3_mean = np.mean(target_reflectance_spectra_t3[t3_name])
        t4_mean = np.mean(target_reflectance_spectra_t4[t4_name])
        diff = t4_mean - t3_mean
        ratio = t4_mean / t3_mean if t3_mean > 0 else 0
        print(f"  {desc:20s}: T3 {t3_name:12s} = {t3_mean:.4f}, T4 {t4_name:8s} = {t4_mean:.4f}")
        print(f"                       Difference: {diff:+.4f}, Ratio: {ratio:.4f}")

def analyze_refvalues_lut():
    """Analyze the reference values LUT for T3 vs T4P targets"""
    print("\n" + "="*80)
    print("ANALYSIS 2: Comparing refvalues_lut for T3 vs T4P targets")
    print("="*80)
    
    # Use centralized ArUco ID definitions
    t3_ids = T3_ARUCO_IDS
    t4p_ids = T4P_ARUCO_IDS
    
    print("\nT3 Target Reference Values (RGN filter - Red channel):")
    for aruco_id in t3_ids:
        if aruco_id in refvalues_lut:
            vals = refvalues_lut[aruco_id]["660/550/850"][0]  # Red channel
            print(f"  Aruco {aruco_id}: {vals}")
    
    print("\nT4P Target Reference Values (RGN filter - Red channel):")
    for aruco_id in t4p_ids:
        if aruco_id in refvalues_lut:
            vals = refvalues_lut[aruco_id]["660/550/850"][0]  # Red channel
            print(f"  Aruco {aruco_id}: {vals}")
    
    print("\n" + "-"*80)
    print("Expected Panel Order (from brightest to darkest):")
    print("-"*80)
    print("  T3:  white (0.85) -> light_grey (0.66) -> silver_grey (0.37) -> dark_grey (0.22)")
    print("  T4P: pft_94 (0.96) -> pft_80 (0.84) -> pft_50 (0.50) -> pft_18 (0.18)")
    
    print("\n" + "-"*80)
    print("CRITICAL CHECK: Are refvalues in the correct order?")
    print("-"*80)
    
    # Check T4P values
    for aruco_id in t4p_ids:
        if aruco_id in refvalues_lut:
            vals = refvalues_lut[aruco_id]["660/550/850"][0]
            is_descending = all(vals[i] > vals[i+1] for i in range(len(vals)-1))
            print(f"  Aruco {aruco_id}: Values descending? {is_descending}")
            if not is_descending:
                print(f"    ⚠️  WARNING: Values are NOT in descending order!")
                print(f"    Expected order: pft_94 > pft_80 > pft_50 > pft_18")
                print(f"    Actual values: {vals}")

def analyze_target_dimensions():
    """Analyze target dimensions for T4P targets"""
    print("\n" + "="*80)
    print("ANALYSIS 3: Target Dimensions")
    print("="*80)
    
    # Use centralized ArUco ID definitions
    t4p_ids = T4P_ARUCO_IDS
    t3_ids = T3_ARUCO_IDS
    
    print("\nT3 Target Dimensions:")
    for aruco_id in t3_ids:
        if aruco_id in target_dimensions:
            dims = target_dimensions[aruco_id]
            print(f"  Aruco {aruco_id}: size={dims['target_size']}, offset={dims['target_offset']}, sizemult={dims['sizemult']}")
    
    print("\nT4P Target Dimensions:")
    for aruco_id in t4p_ids:
        if aruco_id in target_dimensions:
            dims = target_dimensions[aruco_id]
            print(f"  Aruco {aruco_id}: size={dims['target_size']}, offset={dims['target_offset']}, sizemult={dims['sizemult']}")

def analyze_polygon_ordering():
    """Analyze how polygon ordering affects calibration"""
    print("\n" + "="*80)
    print("ANALYSIS 4: Polygon Ordering Issue")
    print("="*80)
    
    print("""
The current polygon reordering in calibration_target_polys():
    polys=[polys[2],polys[1],polys[3],polys[0]]

This reorders from physical layout to:
    [0] = brightest panel (white/pft_94)
    [1] = second brightest (light_grey/pft_80)
    [2] = third panel (silver_grey/pft_50)
    [3] = darkest panel (dark_grey/pft_18)

⚠️  POTENTIAL ISSUE: If T4P physical layout differs from T3, this ordering is WRONG!

For T3 targets, the physical layout (clockwise from ArUco marker) is:
    Panel A (top-left)     -> Polygon 0
    Panel B (top-right)    -> Polygon 1
    Panel C (bottom-right) -> Polygon 2
    Panel D (bottom-left)  -> Polygon 3

After reordering for T3:
    polys[2] = white     (brightest)
    polys[1] = light_grey
    polys[3] = silver_grey
    polys[0] = dark_grey (darkest)

If T4P has a different panel arrangement, the calibration will be completely wrong!
""")

def test_image_processing(image_path):
    """Process a test image and analyze calibration target values"""
    print(f"\n" + "="*80)
    print(f"ANALYSIS 5: Processing Test Image")
    print(f"="*80)
    print(f"Image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"  ⚠️  Image not found: {image_path}")
        return
    
    # Create a simple image object for testing
    class TestImage:
        def __init__(self, path):
            self.path = path
            self.fn = os.path.basename(path)
            self.jpgpath = path
            self.rawpath = path.replace('.JPG', '.RAW').replace('.jpg', '.RAW')
            self.ext = os.path.splitext(path)[1][1:].lower()
            self.data = None
            self.aruco_id = None
            self.aruco_corners = None
            self.is_calibration_photo = False
            self.calibration_target_polys = None
            self.calibration_poly_size = None
            self.target_sample_diameter = None
            
            # Detect camera model and filter from filename
            if 'RGN' in path.upper():
                self.camera_model = 'Survey3N'
                self.camera_filter = 'RGN'
            else:
                self.camera_model = 'Survey3W'
                self.camera_filter = 'RGN'  # Default
        
        def load(self):
            if self.ext in ['raw', 'tif', 'tiff']:
                import tifffile
                self.data = tifffile.imread(self.rawpath)
            else:
                self.data = cv2.imread(self.path)
    
    image = TestImage(image_path)
    
    # Try to detect calibration target
    print(f"\nDetecting calibration target...")
    try:
        detected = detect_calibration_targets(image)
        if detected:
            print(f"  ✅ Target detected!")
            print(f"  ArUco ID: {image.aruco_id}")
            
            # Load image data
            image.load()
            if image.data is not None:
                print(f"  Image shape: {image.data.shape}")
                print(f"  Image dtype: {image.data.dtype}")
                
                # Get calibration polygons
                calibration_target_polys(image)
                
                if image.calibration_target_polys is not None:
                    print(f"  Number of polygons: {len(image.calibration_target_polys)}")
                    
                    # Get target values
                    vals = calibration_target_values(image)
                    print(f"\n  Raw Target Values (per polygon, [R,G,B] or [R,G,NIR]):")
                    for i, val in enumerate(vals):
                        print(f"    Polygon {i}: {val}")
                    
                    # Analyze the values
                    print(f"\n  Expected Order (brightest to darkest):")
                    if get_target_type(image.aruco_id) == 't4p':
                        print(f"    pft_94 (~96%) > pft_80 (~84%) > pft_50 (~50%) > pft_18 (~18%)")
                    else:  # T3
                        print(f"    white (~85%) > light_grey (~66%) > silver_grey (~37%) > dark_grey (~22%)")
                    
                    # Check if values are in descending order
                    means = [np.mean(v) for v in vals]
                    is_descending = all(means[i] >= means[i+1] for i in range(len(means)-1))
                    print(f"\n  Mean values: {[f'{m:.1f}' for m in means]}")
                    print(f"  Values in descending order? {is_descending}")
                    
                    if not is_descending:
                        print(f"\n  ⚠️  WARNING: Polygon ordering appears to be WRONG for this target!")
                        print(f"  This could explain the compressed NDVI values!")
                        
                        # Suggest correct ordering
                        sorted_indices = np.argsort(means)[::-1]  # Descending order
                        print(f"\n  Suggested correct polygon order: {list(sorted_indices)}")
                else:
                    print(f"  ⚠️  Failed to get calibration polygons")
            else:
                print(f"  ⚠️  Failed to load image data")
        else:
            print(f"  ⚠️  No calibration target detected")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

def calculate_expected_ndvi_impact():
    """Calculate expected NDVI impact from calibration differences"""
    print("\n" + "="*80)
    print("ANALYSIS 6: Expected NDVI Impact from Calibration Errors")
    print("="*80)
    
    print("""
NDVI = (NIR - Red) / (NIR + Red)

For healthy vegetation:
- Red reflectance: ~5-10% (chlorophyll absorbs red)
- NIR reflectance: ~40-60% (leaf structure reflects NIR)

Expected NDVI for healthy vegetation:
    NDVI = (0.50 - 0.08) / (0.50 + 0.08) = 0.42 / 0.58 = 0.72

If calibration is wrong:
1. If Red is calibrated too HIGH (overcorrected):
   - Red appears brighter than it should
   - NDVI = (NIR - High_Red) / (NIR + High_Red) = LOWER NDVI
   
2. If NIR is calibrated too LOW (undercorrected):
   - NIR appears dimmer than it should
   - NDVI = (Low_NIR - Red) / (Low_NIR + Red) = LOWER NDVI

Your observed symptoms (NDVI 0-0.4 instead of 0.2-0.9):
- This suggests either Red is too high, NIR is too low, or BOTH
- This is consistent with WRONG polygon ordering!

If the polygon order is wrong, the calibration formula will:
- Use the WRONG reference reflectance for each panel
- Create a calibration curve that over/under-corrects channels

Example:
If polygon 0 is actually the 50% panel but calibration thinks it's the 96% panel:
- Calibration will think a dark pixel value = 96% reflectance
- This creates a calibration factor that's ~2x too high
- All pixel values will be scaled up incorrectly
""")

def main():
    print("="*80)
    print("T4P CALIBRATION TARGET DIAGNOSTIC TOOL")
    print("="*80)
    
    # Run analyses
    analyze_reflectance_spectra()
    analyze_refvalues_lut()
    analyze_target_dimensions()
    analyze_polygon_ordering()
    calculate_expected_ndvi_impact()
    
    # Test with sample images if provided
    test_dirs = [
        r"C:\Users\MAPIR\Desktop\Image_Processing\SAMPLES\MAPIR Office\t4p test\test t4p-r50",
        r"C:\Users\MAPIR\Desktop\Image_Processing\SAMPLES\MAPIR Office\t4p test\test t4p-r125",
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            # Find first JPG file
            for fn in os.listdir(test_dir):
                if fn.lower().endswith('.jpg'):
                    test_image_processing(os.path.join(test_dir, fn))
                    break
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

