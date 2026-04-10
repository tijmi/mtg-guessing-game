from pathlib import Path
import os
import cv2
import json
from tqdm import tqdm
import shutil
import numpy as np


class DataAugmentation:
    def __init__(self, data_labels_path:str = "data_labels.json",output_dir:str = "data/processed_images"):
        self.data_labels_path = data_labels_path
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        with open(self.data_labels_path, 'r') as f:
            self.data_labels = json.load(f)
    
    
    
    def saturate_image(self, image_path:str, levels:int = 10, base_image:str = None):
        image = cv2.imread(image_path)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        scales = [round(0.85 + i * (0.30 / max(levels - 1, 1)), 2) for i in range(levels)]
        with tqdm(total=len(scales), desc="sturation iteration", unit="img", position=0, leave=False) as blurbar:
            for i,scale in enumerate(scales, 1):
                s_scaled = np.clip(s.astype(np.float32) * scale, 0, 255).astype(hsv.dtype)
                hsv = cv2.merge((h, s_scaled, v))
                saturated_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                filename = rf"{self.output_dir}/{Path(image_path).name}_saturated_{i}.png"
                cv2.imwrite(filename, saturated_image)
                if base_image is None:
                        base_image = image_path
                self.data_labels[base_image]["augmented_images"].append(filename)
                self.inner_pbar.set_postfix_str(f"Saved {filename}")
                blurbar.update(1)
            
    
    def blur_image(self, image_path:str, base_ksize:int = 3, levels:int = 10,base_image :str = None):
        image = cv2.imread(image_path)
        with tqdm(total=levels, desc="Blurring iteration", unit="img", position=0, leave=False) as blurbar:
            for i in range(1, levels + 1):
                ksize = base_ksize + 2 * (i - 1)
                if ksize % 2 == 0:
                    ksize += 1          
                blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
                filename = rf"{self.output_dir}/{Path(image_path).name}_blurred_{i}.png"
                cv2.imwrite(filename, blurred)
                if base_image is None:
                        base_image = image_path
                self.data_labels[base_image]["augmented_images"].append(filename)
                self.pbar.set_postfix_str(f"Saved {filename}")
                blurbar.update(1)
                
    def flip_image(self, image_path:str, base_image:str = None):
        image = cv2.imread(image_path)
        flipped = cv2.flip(image, 1)
        filename = rf"{self.output_dir}/{Path(image_path).name}_flipped1.png"
        cv2.imwrite(filename, flipped)
        flipped = cv2.flip(image, 0)
        filename2 = rf"{self.output_dir}/{Path(image_path).name}_flipped2.png"
        cv2.imwrite(filename2, flipped)
        if base_image is None:
            base_image = image_path
        self.data_labels[base_image]["augmented_images"].append(filename)
        self.data_labels[base_image]["augmented_images"].append(filename2)

    def augment_data(self):
        with tqdm(total=len(self.data_labels), desc="Blurring images", unit="img", position=0, leave=True) as self.pbar:
            for image_path in self.data_labels.keys():
                self.data_labels[image_path]["augmented_images"] = []
                self.blur_image(image_path)
                self.pbar.update(1)
                shutil.copy(image_path, self.output_dir)
                self.data_labels[image_path]["augmented_images"].append(rf"{self.output_dir}/{Path(image_path).name}")
                blurred = self.data_labels[image_path]["augmented_images"].copy()
                with tqdm(total=len(blurred), desc="Saturating", unit="file", position=1, leave=False) as self.inner_pbar:
                    for file in blurred:
                        self.saturate_image(file, base_image=image_path)
                        self.inner_pbar.update(1)
                satureated = self.data_labels[image_path]["augmented_images"].copy()
                with tqdm(total=len(satureated), desc="Flipping", unit="file", position=2, leave=False) as flipbar:
                    for file in satureated:
                        self.flip_image(file, base_image=image_path)
                        flipbar.update(1)
                    
                
            # self.blur_image(image_path)
        with open(self.data_labels_path, 'w') as f:
            json.dump(self.data_labels, f, indent=4)
            
if __name__ == "__main__":
    augmenter = DataAugmentation()
    augmenter.augment_data()