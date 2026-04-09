import os
from tqdm import tqdm
import json
from pathlib import Path
import requests
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2

class dataimport:
    def __init__(self,data_path: str = "data/unprocessed",json_path: str = "data_labels.json"):
        self.data_path = data_path
        self.json_path = json_path
        self.min_width, self.min_height = float("inf"), float("inf")
        self.datainfo = {}
        self.HEADERS = {
            "User-Agent": "MTGGUESSINGGAME-1.0",
            "Accept": "application/json",
        }
        self.BASE_URL = "https://api.scryfall.com"
        
    
    def crop_images(self):
        self.min_width, self.min_height = float("inf"), float("inf")

        for root, dirs, files in os.walk(self.data_path):
            for file in tqdm(files, desc="Finding smallest image", unit="img"):
                image_path = os.path.join(root, file)
                img = cv2.imread(image_path)
                if img is None:
                    continue
                h, w = img.shape[:2]
                self.min_width = min(self.min_width, w)
                self.min_height = min(self.min_height, h)

        if self.min_width == float("inf") or self.min_height == float("inf"):
            raise ValueError("No readable images found.")

        self.min_width = int(self.min_width)
        self.min_height = int(self.min_height)
        print(f"Minimum width: {self.min_width}, Minimum height: {self.min_height}")

        for root, dirs, files in os.walk(self.data_path):
            for file in tqdm(files, desc="Cropping images", unit="img"):
                image_path = os.path.join(root, file)
                image = cv2.imread(image_path)
                if image is None:
                    continue

                h, w = image.shape[:2]  # important: recompute per image
                left = max((w - self.min_width) // 2, 0)
                top = max((h - self.min_height) // 2, 0)

                cropped = image[top:top + self.min_height, left:left + self.min_width]
                cv2.imwrite(image_path, cropped)  # overwrite original file in its own folder
                        
    
    def fetch_scryfall_image(self,imagepath:str):
        print(f"Fetching Scryfall data for: {imagepath} with data info: {self.datainfo[imagepath]}")
        params = {
            "fuzzy": self.datainfo[imagepath]["cardname"],
            "format": "image",
            "version": "art_crop",
        }
        
        if self.datainfo[imagepath]["set"]:
            params["set"] = self.datainfo[imagepath]["set"]  # e.g. "lea", "m21", "mh3"

        response = requests.get(
            "https://api.scryfall.com/cards/named",
            headers=self.HEADERS,
            params=params,
            stream=True
        )
        response.raise_for_status()

        os.makedirs(r"data/scryfall_images", exist_ok=True)
        safe_name = self.datainfo[imagepath]["cardname"].lower().replace(" ", "_")
        ext = "png"
        filepath = f"data/scryfall_images/{safe_name}_scryfall.{ext}"

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        self.datainfo[imagepath]["scryfall_image"] = filepath
        print(f"Saved: {filepath}")
    
    def label_data(self):
        if len(self.data_path) == 0:
            raise ValueError("Data path is empty.")
        fig = None
        ax = None
        try:
            plt.ion()
            for root, dirs, files in os.walk(self.data_path):
                    for file in tqdm(files, desc="Labeling images", unit="img"):
                        if file.endswith('.jpg') or file.endswith('.png'):
                            image_path = os.path.join(root, file)

                            if fig is None:
                                fig, ax = plt.subplots()
                                plt.show(block=False)

                            image_data = mpimg.imread(image_path)
                            ax.clear()
                            ax.imshow(image_data)
                            ax.axis("off")
                            ax.set_title(file)
                            fig.canvas.draw_idle()
                            plt.pause(0.001)

                            filename = Path(file)
                            name = filename.with_suffix('')
                            name = str(name).replace("-", " ")
                            new_filename = file.replace(" ", "-")
                            new_image_path = os.path.join(root, new_filename)
                            if new_image_path != image_path:
                                os.rename(image_path, new_image_path)
                            set = input("Enter the set code for this card: ")
                            self.datainfo[new_image_path] = {"cardname": str(name), "path": new_image_path, "set": set}
                            self.fetch_scryfall_image(new_image_path)
                            
        finally:
            if fig is not None:
                plt.close(fig)
            plt.ioff()
                        
        with open(self.json_path, 'r+') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("data_labels.json must contain a JSON object.")
            data.update(self.datainfo)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            
    def newdata(self):
        self.crop_images()
        self.scale_images()
        self.label_data()
        self.augementor = dataaugmentation.DataAugmentation(data_labels_path=self.json_path, output_dir="data/processed_images")
        self.augementor.augment_data()
        

if __name__ == "__main__":
    data_path = "data/unprocessed"
    json_path = "data_labels.json"
    data_importer = dataimport(data_path, json_path)
    data_importer.crop_images()
    data_importer.label_data()