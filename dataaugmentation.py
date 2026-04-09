from pathlib import Path
import os
import cv2
import json
from tqdm import tqdm
import shutil


class DataAugmentation:
    def __init__(self, data_labels_path:str = "data_labels.json",output_dir:str = "data/processed_images"):
        self.data_labels_path = data_labels_path
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        with open(self.data_labels_path, 'r') as f:
            self.data_labels = json.load(f)
    
    def saturate_image(self, image_path:str, levels:int = 10):
        image = cv2.imread(image_path)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        scales = [round(i * (3.0 / levels), 2) for i in range(1, levels + 1)]
        for i,scale in enumerate(scales, 1):
            s = cv2.multiply(s, scale)
            s = cv2.min(s, 255).astype(hsv.dtype)
            hsv = cv2.merge((h, s, v))
            saturated_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            filename = rf"{self.output_dir}/{Path(image_path).name}_saturated_{i}.png"
            cv2.imwrite(filename, saturated_image)
            self.data_labels[image_path]["augmented_images"].append(filename)
            self.pbar.set_postfix_str(f"Saved {filename}")
        
    
    def blur_image(self, image_path:str, base_ksize:int = 10, levels:int = 10,base_image :str = None):
        image = cv2.imread(image_path)
        for i in range(1, levels + 1):
            ksize = base_ksize * i 
            if ksize % 2 == 0:
                ksize += 1          
            blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
            filename = rf"{self.output_dir}/{Path(image_path).name}_blurred_{i}.png"
            cv2.imwrite(filename, blurred)
            self.data_labels[image_path]["augmented_images"].append(filename)
            self.pbar.set_postfix_str(f"Saved {filename}")
        
    def augment_data(self):
        with tqdm(total=len(self.data_labels), desc="bluring images", unit="img") as self.pbar:
            for image_path in self.data_labels.keys():
                self.data_labels[image_path]["augmented_images"] = []
                self.blur_image(image_path)
                self.pbar.update(1)
                shutil.copy(image_path, self.output_dir)
                self.data_labels[image_path]["augmented_images"].append(rf"{self.output_dir}/{Path(image_path).name}")
                for file in self.data_labels[image_path]["augmented_images"]:
                    self.saturate_image(file)
                    self.pbar.update(1)
            
            
                    
                
            # self.blur_image(image_path)
        with open(self.data_labels_path, 'w') as f:
            json.dump(self.data_labels, f, indent=4)
            
if __name__ == "__main__":
    augmenter = DataAugmentation()
    augmenter.augment_data()