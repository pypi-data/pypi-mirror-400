# -*- coding: utf-8 -*-
"""
CHLOROS+ Deep Denoiser Training Script

Train your own Topaz-style denoiser for MAPIR multispectral images.

USAGE:
======
1. Quick start with pre-trained model:
   python train_denoiser.py --test-pretrained

2. Train on your paired data:
   python train_denoiser.py --clean-dir path/to/clean --noisy-dir path/to/noisy

3. Fine-tune pre-trained model:
   python train_denoiser.py --clean-dir path/to/clean --noisy-dir path/to/noisy --pretrained

DATA COLLECTION GUIDE:
======================
To create training pairs like Topaz AI:

Option A: Multi-Frame Averaging (Recommended)
- Mount camera on tripod pointing at static scene
- Capture 16-32 frames at your typical settings
- Average all frames = CLEAN image
- Single frame = NOISY image
- Repeat for 20-50 different scenes

Option B: ISO Pairs
- Capture same scene at lowest ISO (clean)
- Capture same scene at typical/high ISO (noisy)
- Need tripod and static scenes

Option C: Calibration Target Method
- Use your MAPIR calibration targets
- Multiple exposures averaged = clean reference
- Single exposures = noisy samples

@author: MAPIR, Inc
"""

import os
import sys
import argparse
import numpy as np

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_pretrained():
    """Test the NAFNet model infrastructure."""
    from mip.deep_denoise import create_untrained_model, DEFAULT_MODEL_DIR
    import cv2

    print("=" * 60)
    print("CHLOROS+ Deep Denoiser - Infrastructure Test")
    print("=" * 60)

    # For MAPIR sensors, training from scratch is recommended
    # The pre-trained SIDD model is for smartphone images
    # Your sensor's NIR noise characteristics are unique
    print("\n[1] Creating NAFNet model...")
    print("    (Training from scratch recommended for your sensor)")
    denoiser = create_untrained_model()
    model_type = "untrained"

    if not denoiser.is_ready():
        print("ERROR: Failed to create model")
        return False

    print(f"    Model type: {model_type}")
    print(f"    Device: {denoiser.device}")

    # Create a test image with synthetic noise
    print("\n[2] Creating test image (512x512)...")
    test_img = np.random.randint(30000, 50000, (512, 512, 3), dtype=np.uint16)
    noise = np.random.randn(512, 512, 3) * 2000
    noisy_img = np.clip(test_img + noise, 0, 65535).astype(np.uint16)

    print("\n[3] Running denoising inference...")
    import time
    t0 = time.time()
    denoised = denoiser.denoise(noisy_img, strength=1.0)
    t1 = time.time()

    # Check results
    noise_before = np.std(noisy_img.astype(float) - test_img.astype(float))
    noise_after = np.std(denoised.astype(float) - test_img.astype(float))

    print(f"\n[4] Results:")
    print(f"    Inference time: {(t1-t0)*1000:.1f} ms")
    print(f"    Noise level before: {noise_before:.1f}")
    print(f"    Noise level after:  {noise_after:.1f}")

    if model_type == "pre-trained":
        reduction = 100 * (1 - noise_after/noise_before)
        print(f"    Noise reduction: {reduction:.1f}%")
    else:
        print("    (Untrained model - no noise reduction expected)")

    print("\n" + "=" * 60)
    print("Infrastructure test PASSED!")
    print("=" * 60)

    if model_type == "untrained":
        print(f"""
NEXT STEPS to get Topaz-style denoising:

Option A: Download pre-trained NAFNet weights
  1. Go to: https://github.com/megvii-research/NAFNet
  2. Download 'NAFNet-SIDD-width32.pth' from their Google Drive
  3. Save to: {DEFAULT_MODEL_DIR}/nafnet_denoise_sidd.pth

Option B: Train your own model (recommended for best results)
  1. Collect training data (see below)
  2. Run: python train_denoiser.py --clean-dir data/clean --noisy-dir data/noisy

DATA COLLECTION - How to create training pairs:
  Method 1: Multi-frame averaging
    - Mount camera on tripod, capture 16-32 frames of static scene
    - Average all frames = CLEAN reference
    - Single frame = NOISY sample
    - Repeat for 20-50 different scenes

  Method 2: ISO pairs
    - Same scene at lowest ISO (clean) vs typical ISO (noisy)
    - Need tripod and static scenes
""")

    return True


def train_model(args):
    """Train a custom denoiser on user data."""
    from mip.deep_denoise import (
        DenoisingDataset, DenoiseTrainer, train_denoiser,
        get_pretrained_model, download_pretrained_weights
    )
    import cv2

    print("=" * 60)
    print("CHLOROS+ Deep Denoiser - Training")
    print("=" * 60)

    # Load images
    print(f"\n[1] Loading images from:")
    print(f"    Clean: {args.clean_dir}")
    print(f"    Noisy: {args.noisy_dir}")

    clean_images = []
    noisy_images = []

    extensions = {'.tif', '.tiff', '.png', '.jpg', '.jpeg'}

    clean_files = sorted([f for f in os.listdir(args.clean_dir)
                          if os.path.splitext(f)[1].lower() in extensions])
    noisy_files = sorted([f for f in os.listdir(args.noisy_dir)
                          if os.path.splitext(f)[1].lower() in extensions])

    if len(clean_files) != len(noisy_files):
        print(f"WARNING: Mismatched file counts - clean:{len(clean_files)}, noisy:{len(noisy_files)}")
        print("Files must be in matching order (same scene, same name)")

    for clean_f, noisy_f in zip(clean_files, noisy_files):
        clean_path = os.path.join(args.clean_dir, clean_f)
        noisy_path = os.path.join(args.noisy_dir, noisy_f)

        clean_img = cv2.imread(clean_path, cv2.IMREAD_UNCHANGED)
        noisy_img = cv2.imread(noisy_path, cv2.IMREAD_UNCHANGED)

        if clean_img is not None and noisy_img is not None:
            if len(clean_img.shape) == 2:
                clean_img = cv2.cvtColor(clean_img, cv2.COLOR_GRAY2RGB)
                noisy_img = cv2.cvtColor(noisy_img, cv2.COLOR_GRAY2RGB)
            else:
                clean_img = cv2.cvtColor(clean_img, cv2.COLOR_BGR2RGB)
                noisy_img = cv2.cvtColor(noisy_img, cv2.COLOR_BGR2RGB)

            clean_images.append(clean_img)
            noisy_images.append(noisy_img)
            print(f"    Loaded: {clean_f} <-> {noisy_f}")

    print(f"\n    Total pairs loaded: {len(clean_images)}")

    if len(clean_images) == 0:
        print("ERROR: No images found!")
        return False

    # Create dataset
    print("\n[2] Creating training dataset...")

    # Split for validation (10%)
    val_count = max(1, len(clean_images) // 10)

    train_dataset = DenoisingDataset(
        clean_images=clean_images[val_count:],
        noisy_images=noisy_images[val_count:],
        patch_size=args.patch_size,
        augment=True
    )

    val_dataset = DenoisingDataset(
        clean_images=clean_images[:val_count],
        noisy_images=noisy_images[:val_count],
        patch_size=args.patch_size,
        augment=False
    )

    print(f"    Training samples: {len(train_dataset.clean_images)}")
    print(f"    Validation samples: {len(val_dataset.clean_images)}")

    # Prepare output directory
    output_dir = args.output_dir or os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'chloros_denoiser.pth')

    # Get pretrained weights for fine-tuning or resume checkpoint
    pretrained_path = None
    if args.resume:
        print(f"\n[3] Resuming from checkpoint: {args.resume}")
        pretrained_path = args.resume
    elif args.pretrained:
        print("\n[3] Downloading pre-trained weights for fine-tuning...")
        pretrained_path = download_pretrained_weights('nafnet_denoise_sidd')

    # Train
    step_num = '4' if (args.pretrained or args.resume) else '3'
    print(f"\n[{step_num}] Training model...")
    print(f"    Epochs: {args.epochs}")
    print(f"    Batch size: {args.batch_size}")
    print(f"    Model blocks: {args.num_blocks}")
    print(f"    Learning rate: {args.learning_rate}")
    print(f"    Save path: {save_path}")

    try:
        denoiser = train_denoiser(
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            epochs=args.epochs,
            batch_size=args.batch_size,
            save_path=save_path,
            pretrained_path=pretrained_path,
            num_blocks=args.num_blocks,
            learning_rate=args.learning_rate
        )

        print("\n" + "=" * 60)
        print(f"Training complete! Model saved to: {save_path}")
        print("=" * 60)

        # Auto-encrypt the model for distribution
        print("\n[ENCRYPT] Creating encrypted model for distribution...")
        from mip.model_crypto import encrypt_model_file
        encrypted_path = encrypt_model_file(save_path)
        print(f"[ENCRYPT] Encrypted model: {encrypted_path}")
        print("[ENCRYPT] Use the .pth.enc file for distribution builds.")

    except Exception as e:
        import traceback
        print("\n" + "=" * 60)
        print("ERROR DURING TRAINING:")
        print("=" * 60)
        traceback.print_exc()
        print("\nModel checkpoints may have been saved to 'models/' directory.")
        return False

    return True


def train_bayer_model(args):
    """Train a denoiser on raw Bayer data for pre-debayer denoising."""
    from mip.deep_denoise import (
        BayerDenoisingDataset, DenoiseTrainer, train_denoiser,
        TextureAwareDenoiser, optimize_denoising_params
    )
    import numpy as np

    print("=" * 60)
    print("CHLOROS+ Bayer Denoiser - Training")
    print("=" * 60)

    # Load Bayer data
    print(f"\n[1] Loading Bayer data from:")
    print(f"    Clean: {args.clean_dir}")
    print(f"    Noisy: {args.noisy_dir}")

    clean_bayers = []
    noisy_bayers = []

    clean_files = sorted([f for f in os.listdir(args.clean_dir) if f.endswith('.npy')])
    noisy_files = sorted([f for f in os.listdir(args.noisy_dir) if f.endswith('.npy')])

    if len(clean_files) != len(noisy_files):
        print(f"WARNING: Mismatched file counts - clean:{len(clean_files)}, noisy:{len(noisy_files)}")

    for clean_f, noisy_f in zip(clean_files, noisy_files):
        clean_path = os.path.join(args.clean_dir, clean_f)
        noisy_path = os.path.join(args.noisy_dir, noisy_f)

        clean_bayer = np.load(clean_path)
        noisy_bayer = np.load(noisy_path)

        if clean_bayer is not None and noisy_bayer is not None:
            clean_bayers.append(clean_bayer)
            noisy_bayers.append(noisy_bayer)
            print(f"    Loaded: {clean_f} <-> {noisy_f} ({clean_bayer.shape})")

    print(f"\n    Total Bayer pairs loaded: {len(clean_bayers)}")

    if len(clean_bayers) == 0:
        print("ERROR: No Bayer data found! Run process_bayer_training.py first.")
        return False

    # Create dataset
    print("\n[2] Creating Bayer training dataset...")

    val_count = max(1, len(clean_bayers) // 10)

    train_dataset = BayerDenoisingDataset(
        clean_images=clean_bayers[val_count:],
        noisy_images=noisy_bayers[val_count:],
        patch_size=args.patch_size,
        augment=True
    )

    val_dataset = BayerDenoisingDataset(
        clean_images=clean_bayers[:val_count],
        noisy_images=noisy_bayers[:val_count],
        patch_size=args.patch_size,
        augment=False
    )

    print(f"    Training scenes: {len(train_dataset.clean_bayers)}")
    print(f"    Validation scenes: {len(val_dataset.clean_bayers)}")

    # Prepare output
    output_dir = args.output_dir or os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'chloros_bayer_denoiser.pth')

    # Resume or pretrained
    pretrained_path = None
    if args.resume:
        print(f"\n[3] Resuming from checkpoint: {args.resume}")
        pretrained_path = args.resume

    # Train
    step_num = '4' if args.resume else '3'
    print(f"\n[{step_num}] Training Bayer denoiser...")
    print(f"    Epochs: {args.epochs}")
    print(f"    Batch size: {args.batch_size}")
    print(f"    Model blocks: {args.num_blocks}")
    print(f"    Learning rate: {args.learning_rate}")
    print(f"    Save path: {save_path}")

    try:
        denoiser = train_denoiser(
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            epochs=args.epochs,
            batch_size=args.batch_size,
            save_path=save_path,
            pretrained_path=pretrained_path,
            num_blocks=args.num_blocks,
            learning_rate=args.learning_rate
        )

        print("\n" + "=" * 60)
        print(f"Training complete! Model saved to: {save_path}")
        print("=" * 60)

        # Run optimization if target images provided
        if args.target_dir and os.path.exists(args.target_dir):
            print("\n" + "=" * 60)
            print("Running Parameter Optimization on Target Images...")
            print("=" * 60)

            # Load target images for optimization
            target_files = [f for f in os.listdir(args.target_dir) if f.endswith('.npy')]
            if target_files:
                # Use first target image
                target_bayer = np.load(os.path.join(args.target_dir, target_files[0]))

                # Separate Bayer for testing
                r = target_bayer[0::2, 0::2]
                g1 = target_bayer[0::2, 1::2]
                b = target_bayer[1::2, 1::2]
                test_rgb = np.stack([r, g1, b], axis=-1)

                # Define test regions (center crop as flat region proxy)
                h, w = test_rgb.shape[:2]
                margin = min(h, w) // 4
                test_regions = [(margin, margin, w - 2*margin, h - 2*margin)]

                # Run optimization
                denoiser_test = TextureAwareDenoiser(model_path=save_path)
                if denoiser_test.is_ready():
                    results = optimize_denoising_params(
                        denoiser_test,
                        test_rgb,
                        test_regions,
                        param_grid={
                            'strength': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
                            'passes': [1, 2, 3]
                        }
                    )

                    print("\n" + "=" * 60)
                    print("OPTIMIZATION RESULTS:")
                    print("=" * 60)
                    print(f"  Best strength: {results['best']['strength']}")
                    print(f"  Best passes: {results['best']['passes']}")
                    print(f"  Noise reduction: {results['best']['noise_reduction_pct']:.1f}%")
                    print("=" * 60)

        # Copy to main model location
        main_model_path = os.path.join(output_dir, 'chloros_denoiser.pth')
        import shutil
        shutil.copy(save_path, main_model_path)
        print(f"\nCopied to: {main_model_path}")

        # Auto-encrypt the model for distribution
        print("\n[ENCRYPT] Creating encrypted model for distribution...")
        from mip.model_crypto import encrypt_model_file
        encrypted_path = encrypt_model_file(main_model_path)
        print(f"[ENCRYPT] Encrypted model: {encrypted_path}")
        print("[ENCRYPT] Use the .pth.enc file for distribution builds.")

    except Exception as e:
        import traceback
        print("\n" + "=" * 60)
        print("ERROR DURING BAYER TRAINING:")
        print("=" * 60)
        traceback.print_exc()
        return False

    return True


def train_bayer2rgb_model(args):
    """Train combined Bayer→RGB model (denoise + debayer in one step)."""
    from mip.deep_denoise import (
        BayerToRGBDataset, NAFNetBayerToRGB, DenoiseTrainer
    )
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader

    # Get filter name for model naming
    filter_name = args.filter.upper() if args.filter else 'UNIVERSAL'

    print("=" * 60)
    print(f"CHLOROS+ Bayer→RGB Model Training - {filter_name} Filter")
    print("=" * 60)
    print("\nThis model learns to denoise AND debayer in one step.")
    print("Input: Noisy Bayer (4 channels, half-res)")
    print("Output: Clean RGB (3 channels, full-res)")
    print(f"Filter: {filter_name}")

    # Load data
    print(f"\n[1] Loading training data:")
    print(f"    Noisy Bayer: {args.noisy_bayer_dir}")
    print(f"    Clean RGB: {args.clean_rgb_dir}")

    # Create datasets
    all_dataset = BayerToRGBDataset(
        noisy_bayer_dir=args.noisy_bayer_dir,
        clean_rgb_dir=args.clean_rgb_dir,
        patch_size=args.patch_size,
        augment=True
    )

    if len(all_dataset.noisy_bayers) == 0 or len(all_dataset.clean_rgbs) == 0:
        print("ERROR: No training data found!")
        print("Run prepare_bayer2rgb_training.py first to create clean RGB targets.")
        return False

    if len(all_dataset.noisy_bayers) != len(all_dataset.clean_rgbs):
        print(f"ERROR: Mismatched counts - {len(all_dataset.noisy_bayers)} Bayers, {len(all_dataset.clean_rgbs)} RGBs")
        return False

    # Split for validation
    val_count = max(1, len(all_dataset.noisy_bayers) // 10)

    train_dataset = BayerToRGBDataset(
        noisy_bayers=all_dataset.noisy_bayers[val_count:],
        clean_rgbs=all_dataset.clean_rgbs[val_count:],
        patch_size=args.patch_size,
        augment=True
    )

    val_dataset = BayerToRGBDataset(
        noisy_bayers=all_dataset.noisy_bayers[:val_count],
        clean_rgbs=all_dataset.clean_rgbs[:val_count],
        patch_size=args.patch_size,
        augment=False
    )

    print(f"\n[2] Dataset created:")
    print(f"    Training scenes: {len(train_dataset.noisy_bayers)}")
    print(f"    Validation scenes: {len(val_dataset.noisy_bayers)}")

    # Create model
    print(f"\n[3] Creating NAFNetBayerToRGB model...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = NAFNetBayerToRGB(width=32, num_blocks=args.num_blocks).to(device)

    # Count parameters
    param_count = sum(p.numel() for p in model.parameters())
    print(f"    Parameters: {param_count:,}")
    print(f"    Device: {device}")

    # Setup training
    optimizer = optim.AdamW(model.parameters(), lr=args.learning_rate)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    l1_loss = nn.L1Loss()

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, num_workers=0)

    # Prepare output with filter-specific naming
    output_dir = args.output_dir or os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(output_dir, exist_ok=True)

    # Use filter-specific model name
    model_name = f'chloros_denoiser_{filter_name.lower()}.pth'
    save_path = os.path.join(output_dir, model_name)

    # Early stopping settings
    early_stop_patience = args.early_stop if hasattr(args, 'early_stop') and args.early_stop else 50
    epochs_without_improvement = 0

    # Keep system awake during training
    try:
        import ctypes
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        print(f"    Keep-alive enabled")
    except:
        pass

    print(f"\n[4] Training for {args.epochs} epochs...")
    print(f"    Batch size: {args.batch_size}")
    print(f"    Learning rate: {args.learning_rate}")
    print(f"    Save path: {save_path}")

    best_loss = float('inf')

    try:
        for epoch in range(args.epochs):
            # Training
            model.train()
            train_loss = 0
            for noisy, clean in train_loader:
                noisy = noisy.to(device)  # [B, 4, H/2, W/2]
                clean = clean.to(device)  # [B, 3, H, W]

                optimizer.zero_grad()
                output = model(noisy)  # [B, 3, H, W]
                loss = l1_loss(output, clean)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                train_loss += loss.item()

            train_loss /= len(train_loader)

            # Validation
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for noisy, clean in val_loader:
                    noisy = noisy.to(device)
                    clean = clean.to(device)
                    output = model(noisy)
                    val_loss += l1_loss(output, clean).item()
            val_loss /= len(val_loader)

            scheduler.step()

            # Log progress
            if epoch % 10 == 0 or epoch == args.epochs - 1:
                print(f"    Epoch {epoch}/{args.epochs}: train_loss={train_loss:.6f}, val_loss={val_loss:.6f}")

            # Save best and track early stopping
            if val_loss < best_loss:
                best_loss = val_loss
                epochs_without_improvement = 0
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'model_type': 'bayer2rgb',
                    'num_blocks': args.num_blocks,
                    'width': 32,
                    'filter': filter_name
                }, save_path)
            else:
                epochs_without_improvement += 1
                if epochs_without_improvement >= early_stop_patience:
                    print(f"\n    Early stopping: no improvement for {early_stop_patience} epochs")
                    break

        print(f"\n" + "=" * 60)
        print(f"Training complete! Best val_loss: {best_loss:.6f}")
        print(f"Model saved to: {save_path}")
        print(f"Filter: {filter_name}")
        print("=" * 60)

        # Auto-encrypt
        print("\n[ENCRYPT] Creating encrypted model for distribution...")
        from mip.model_crypto import encrypt_model_file
        encrypted_path = encrypt_model_file(save_path)
        print(f"[ENCRYPT] Encrypted model: {encrypted_path}")
        print(f"[ENCRYPT] Use this model with the '{filter_name}' filter.")

    except Exception as e:
        import traceback
        print("\n" + "=" * 60)
        print("ERROR DURING TRAINING:")
        print("=" * 60)
        traceback.print_exc()
        return False
    finally:
        # Reset keep-alive
        try:
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        except:
            pass

    return True


def synthetic_train(args):
    """Train on clean images with synthetic noise (no pairs needed)."""
    from mip.deep_denoise import (
        create_training_dataset_synthetic, train_denoiser,
        download_pretrained_weights
    )
    import cv2

    print("=" * 60)
    print("CHLOROS+ Deep Denoiser - Synthetic Noise Training")
    print("=" * 60)

    print(f"\n[1] Loading clean images from: {args.clean_dir}")

    clean_images = []
    extensions = {'.tif', '.tiff', '.png', '.jpg', '.jpeg'}

    for f in sorted(os.listdir(args.clean_dir)):
        if os.path.splitext(f)[1].lower() in extensions:
            path = os.path.join(args.clean_dir, f)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                clean_images.append(img)
                print(f"    Loaded: {f}")

    print(f"\n    Total images loaded: {len(clean_images)}")

    if len(clean_images) == 0:
        print("ERROR: No images found!")
        return False

    # Create dataset with synthetic noise
    print("\n[2] Creating synthetic noise dataset...")

    val_count = max(1, len(clean_images) // 10)

    train_dataset = create_training_dataset_synthetic(
        clean_images=clean_images[val_count:],
        patch_size=args.patch_size,
        noise_range=(0.01, 0.05)  # 1-5% noise
    )

    val_dataset = create_training_dataset_synthetic(
        clean_images=clean_images[:val_count],
        patch_size=args.patch_size,
        noise_range=(0.02, 0.04)
    )

    # Train
    output_dir = args.output_dir or os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'chloros_denoiser_synthetic.pth')

    pretrained_path = None
    if args.pretrained:
        print("\n[3] Downloading pre-trained weights...")
        pretrained_path = download_pretrained_weights('nafnet_denoise_sidd')

    print(f"\n[{'4' if args.pretrained else '3'}] Training...")

    denoiser = train_denoiser(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        save_path=save_path,
        pretrained_path=pretrained_path
    )

    print("\n" + "=" * 60)
    print(f"Training complete! Model saved to: {save_path}")
    print("=" * 60)

    return True


def create_training_pairs(args):
    """Help user create training pairs from multi-frame captures."""
    import cv2

    print("=" * 60)
    print("CHLOROS+ - Training Pair Generator")
    print("=" * 60)

    print(f"\nProcessing captures from: {args.captures_dir}")

    # Expect subdirectories, each containing multiple frames of same scene
    output_clean = os.path.join(args.output_dir, 'clean')
    output_noisy = os.path.join(args.output_dir, 'noisy')
    os.makedirs(output_clean, exist_ok=True)
    os.makedirs(output_noisy, exist_ok=True)

    scene_dirs = [d for d in os.listdir(args.captures_dir)
                  if os.path.isdir(os.path.join(args.captures_dir, d))]

    extensions = {'.tif', '.tiff', '.png', '.jpg', '.jpeg', '.raw'}

    for scene in sorted(scene_dirs):
        scene_path = os.path.join(args.captures_dir, scene)
        frames = [f for f in os.listdir(scene_path)
                  if os.path.splitext(f)[1].lower() in extensions]

        if len(frames) < 2:
            print(f"  Skipping {scene}: need at least 2 frames")
            continue

        print(f"\n  Processing {scene} ({len(frames)} frames)...")

        # Load all frames
        loaded_frames = []
        for f in sorted(frames):
            path = os.path.join(scene_path, f)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                loaded_frames.append(img.astype(np.float64))

        if len(loaded_frames) < 2:
            continue

        # Average = clean reference
        clean = np.mean(loaded_frames, axis=0)

        # First frame = noisy sample
        noisy = loaded_frames[0]

        # Save
        clean_path = os.path.join(output_clean, f"{scene}.tif")
        noisy_path = os.path.join(output_noisy, f"{scene}.tif")

        if clean.dtype == np.float64:
            if clean.max() > 255:
                clean = np.clip(clean, 0, 65535).astype(np.uint16)
                noisy = np.clip(noisy, 0, 65535).astype(np.uint16)
            else:
                clean = np.clip(clean, 0, 255).astype(np.uint8)
                noisy = np.clip(noisy, 0, 255).astype(np.uint8)

        cv2.imwrite(clean_path, clean)
        cv2.imwrite(noisy_path, noisy)
        print(f"    Saved: {scene}.tif")

    print("\n" + "=" * 60)
    print(f"Training pairs created in: {args.output_dir}")
    print(f"  Clean images: {output_clean}")
    print(f"  Noisy images: {output_noisy}")
    print("\nNext step: Train with these pairs:")
    print(f"  python train_denoiser.py --clean-dir {output_clean} --noisy-dir {output_noisy}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='CHLOROS+ Deep Denoiser Training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test pre-trained model
  python train_denoiser.py --test-pretrained

  # Train on paired data
  python train_denoiser.py --clean-dir data/clean --noisy-dir data/noisy

  # Fine-tune pre-trained model (recommended)
  python train_denoiser.py --clean-dir data/clean --noisy-dir data/noisy --pretrained

  # Train with synthetic noise (no pairs needed)
  python train_denoiser.py --synthetic --clean-dir data/clean

  # Create training pairs from multi-frame captures
  python train_denoiser.py --create-pairs --captures-dir captures --output-dir data
"""
    )

    parser.add_argument('--test-pretrained', action='store_true',
                        help='Test the pre-trained NAFNet model')

    parser.add_argument('--clean-dir', type=str,
                        help='Directory with clean reference images')
    parser.add_argument('--noisy-dir', type=str,
                        help='Directory with corresponding noisy images')

    parser.add_argument('--synthetic', action='store_true',
                        help='Use synthetic noise (only clean-dir needed)')

    parser.add_argument('--pretrained', action='store_true',
                        help='Start from pre-trained weights (recommended)')
    parser.add_argument('--resume', type=str, default=None,
                        help='Path to checkpoint to resume training from')

    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs (default: 100)')
    parser.add_argument('--batch-size', type=int, default=8,
                        help='Training batch size (default: 8)')
    parser.add_argument('--patch-size', type=int, default=128,
                        help='Training patch size (default: 128)')
    parser.add_argument('--num-blocks', type=int, default=8,
                        help='Number of NAFNet blocks: 4=faster, 8=better quality (default: 8)')
    parser.add_argument('--learning-rate', type=float, default=1e-4,
                        help='Learning rate (default: 0.0001)')

    parser.add_argument('--output-dir', type=str,
                        help='Directory to save trained model')

    parser.add_argument('--create-pairs', action='store_true',
                        help='Create training pairs from multi-frame captures')
    parser.add_argument('--captures-dir', type=str,
                        help='Directory with capture subdirectories')

    # Bayer training options
    parser.add_argument('--bayer', action='store_true',
                        help='Train on raw Bayer data (for pre-debayer denoising)')
    parser.add_argument('--target-dir', type=str,
                        help='Directory with target images for optimization (optional)')

    # Bayer→RGB combined model (best quality)
    parser.add_argument('--bayer2rgb', action='store_true',
                        help='Train combined Bayer→RGB model (denoise + debayer in one step)')
    parser.add_argument('--noisy-bayer-dir', type=str,
                        help='Directory with noisy Bayer .npy files (for --bayer2rgb)')
    parser.add_argument('--clean-rgb-dir', type=str,
                        help='Directory with clean RGB .npy files (for --bayer2rgb)')

    # Filter-specific model training
    parser.add_argument('--filter', type=str, default=None,
                        help='Filter type for model naming (e.g., RGN, OCN, NGB, etc.)')
    parser.add_argument('--early-stop', type=int, default=50,
                        help='Early stopping patience (epochs without improvement, default: 50)')

    args = parser.parse_args()

    # Route to appropriate function
    if args.test_pretrained:
        test_pretrained()
    elif args.create_pairs:
        if not args.captures_dir or not args.output_dir:
            parser.error("--create-pairs requires --captures-dir and --output-dir")
        create_training_pairs(args)
    elif args.synthetic:
        if not args.clean_dir:
            parser.error("--synthetic requires --clean-dir")
        synthetic_train(args)
    elif args.bayer2rgb:
        if not args.noisy_bayer_dir or not args.clean_rgb_dir:
            parser.error("--bayer2rgb requires --noisy-bayer-dir and --clean-rgb-dir")
        train_bayer2rgb_model(args)
    elif args.bayer and args.clean_dir and args.noisy_dir:
        train_bayer_model(args)
    elif args.clean_dir and args.noisy_dir:
        train_model(args)
    else:
        parser.print_help()
        print("\n" + "=" * 60)
        print("Quick Start Guide:")
        print("=" * 60)
        print("""
1. TEST PRE-TRAINED MODEL:
   python train_denoiser.py --test-pretrained

2. COLLECT YOUR DATA:
   Create folders: data/clean and data/noisy

   For each scene, capture multiple frames:
   - Average all frames -> save to data/clean/scene1.tif
   - Single frame -> save to data/noisy/scene1.tif

   OR use --create-pairs with multi-frame captures

3. TRAIN YOUR MODEL:
   python train_denoiser.py --clean-dir data/clean --noisy-dir data/noisy --pretrained

4. USE IN CHLOROS:
   The trained model will be saved to models/chloros_denoiser.pth
   and automatically used by the Target Aware debayer method.
""")


if __name__ == '__main__':
    main()
