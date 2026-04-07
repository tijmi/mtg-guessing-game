import os
from tqdm import tqdm
import json
import re
from pathlib import Path

class dataimport:
    def __init__(self,data_path: str = "data/unprocessed",json_path: str = "data_labels.json"):
        self.data_path = data_path
        self.json_path = json_path
        self.datainfo = {}
        
    def label_data(self):
        if len(self.data_path) == 0:
            raise ValueError("Data path is empty.")
        for root, dirs, files in os.walk(self.data_path):
                for file in tqdm(files):
                    if file.endswith('.jpg') or file.endswith('.png'):
                        image_path = os.path.join(root, file)
                        filename = Path(file)
                        new_filename = file.replace(" ", "-")
                        os.rename(image_path, os.path.join(root, new_filename))
                        name =  filename.with_suffix('')
                        self.datainfo[os.path.join(root, new_filename)] = {"cardname": str(name), "path": os.path.join(root, new_filename)}

        with open(self.json_path, 'r+') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("data_labels.json must contain a JSON object.")
            data.update(self.datainfo)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            

if __name__ == "__main__":
    data_path = "data/unprocessed"
    json_path = "data_labels.json"
    data_importer = dataimport(data_path, json_path)
    data_importer.label_data()