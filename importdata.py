import os
from tqdm import tqdm

class dataimport:
    def __init__(self,data_path):
        self.data_path = data_path
        
    def label_data(self):
        for root, dirs, files in os.walk(self.input_dir):
                for file in tqdm(files):
                    if file.endswith('.jpg') or file.endswith('.png'):
                        image_path = os.path.join(root, file)
                        label = os.path.basename(root)
                        self.data.append((image_path, label))
