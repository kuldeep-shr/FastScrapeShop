import json
import os

class JSONStorageStrategy:
    def __init__(self, file_path="data/products.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save(self, data: list):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data successfully saved to {self.file_path}")
