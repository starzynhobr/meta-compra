import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_file = Path.home() / ".meta_compra_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "db_path": None,
            "show_purchased": True
        }
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
    
    def get_db_path(self):
        return self.config.get("db_path")
    
    def set_db_path(self, path):
        self.config["db_path"] = str(path)
        self.save_config()
    
    def get_show_purchased(self):
        return self.config.get("show_purchased", True)
    
    def set_show_purchased(self, value):
        self.config["show_purchased"] = value
        self.save_config()
