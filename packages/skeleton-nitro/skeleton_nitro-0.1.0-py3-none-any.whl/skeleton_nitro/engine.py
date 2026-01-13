import os
import sys
import torch
import torch.nn.functional as F
import cv2
import numpy as np
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse

class SkeletonNitro:
    def __init__(self, device="cuda", img_size=224, batch_size=100):
        """
        Initialize the Nitro Engine.
        :param device: 'cuda' for GPU or 'cpu'
        :param img_size: Resolution to resize images (default 224)
        :param batch_size: How many augmentations to process at once in VRAM
        """
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.img_size = img_size
        self.batch_size = batch_size
        
        if self.device.type == 'cuda':
            print(f" Nitro GPU Engine Active: {torch.cuda.get_device_name(0)}")
        else:
            print(" Nitro Engine Warning: CUDA not found, using CPU (Slow).")

    def _gpu_thinning(self, binary_tensor, iterations=3):
        """Perform morphological thinning using GPU convolutions."""
        kernel = torch.ones((1, 1, 3, 3), device=self.device)
        for _ in range(iterations):
            eroded = F.conv2d(binary_tensor, kernel, padding=1)
            binary_tensor = (eroded == 9).float() 
        return binary_tensor

    def process_image(self, img_path, output_dir, mode="skeleton", aug_count=1):
        """Process a single image and generate N augmentations."""
        try:
            # Read image safely (supports Unicode/Tamil paths)
            data = np.fromfile(str(img_path), dtype=np.uint8)
            raw = cv2.imdecode(data, 0)
            if raw is None: return

            # 1. Upload to GPU
            img_gpu = torch.from_numpy(raw).to(self.device).float().unsqueeze(0).unsqueeze(0)
            img_gpu = F.interpolate(img_gpu, size=(self.img_size, self.img_size))

            if mode == "grayscale":
                res = img_gpu.squeeze().cpu().numpy().astype(np.uint8)
                out_path = output_dir / f"{img_path.stem}_gray.png"
                cv2.imwrite(str(out_path), res)
                return

            # 2. Skeleton Mode
            binary_gpu = (img_gpu < 128).float()
            skel_gpu = self._gpu_thinning(binary_gpu)

            # 3. Batch Augmentation
            count = 0
            for _ in range(0, aug_count, self.batch_size):
                curr_batch = min(self.batch_size, aug_count - count)
                batch_tensors = skel_gpu.expand(curr_batch, -1, -1, -1)
                
                # Random Rotation/Shear in VRAM
                angles = (torch.rand(curr_batch, device=self.device) - 0.5) * 40
                mats = torch.zeros((curr_batch, 2, 3), device=self.device)
                cos_a, sin_a = torch.cos(angles * np.pi / 180), torch.sin(angles * np.pi / 180)
                mats[:, 0, 0], mats[:, 0, 1], mats[:, 1, 0], mats[:, 1, 1] = cos_a, -sin_a, sin_a, cos_a

                grid = F.affine_grid(mats, batch_tensors.size(), align_corners=False)
                augs = F.grid_sample(batch_tensors, grid, align_corners=False)
                
                cpu_batch = (augs.squeeze(1).cpu().numpy() * 255).astype(np.uint8)
                
                for i in range(curr_batch):
                    out_path = output_dir / f"{img_path.stem}_v{count}.png"
                    # Fast encode with no compression
                    _, buf = cv2.imencode(".png", cpu_batch[i], [cv2.IMWRITE_PNG_COMPRESSION, 0])
                    buf.tofile(str(out_path))
                    count += 1
                    
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

def fast_write(args):
    """Worker function for ThreadPool writing."""
    path, img = args
    _, buf = cv2.imencode(".png", img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    buf.tofile(str(path))

def main():
    parser = argparse.ArgumentParser(description="Skeleton-Nitro: High-Speed GPU Image Processor")
    parser.add_argument("--input", type=str, required=True, help="Input directory")
    parser.add_argument("--output", type=str, required=True, help="Output directory")
    parser.add_argument("--mode", type=str, default="skeleton", choices=["skeleton", "grayscale"])
    parser.add_argument("--aug", type=int, default=1, help="Augmentations per image")
    parser.add_argument("--batch", type=int, default=100, help="GPU batch size")
    
    args = parser.parse_args()
    
    engine = SkeletonNitro(batch_size=args.batch)
    in_path = Path(args.input)
    out_path = Path(args.output)
    
    # Supported formats
    extensions = ("*.png", "*.jpg", "*.jpeg", "*.bmp")
    files = []
    for ext in extensions:
        files.extend(list(in_path.rglob(ext)))
    
    if not files:
        print(f"No images found in {in_path}")
        return

    print(f"📂 Found {len(files)} images. Starting Nitro processing...")
    
    for f in tqdm(files, desc="Total Progress"):
        rel_dir = out_path / f.relative_to(in_path).parent
        rel_dir.mkdir(parents=True, exist_ok=True)
        engine.process_image(f, rel_dir, mode=args.mode, aug_count=args.aug)

    print(f"🎉 Success! Processed images are in: {out_path}")

if __name__ == "__main__":
    main()