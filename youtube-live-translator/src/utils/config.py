"""
配置管理模組
"""

import json
import os
from pathlib import Path

class Config:
    """應用程式配置管理"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".youtube_live_translator"
        self.config_file = self.config_dir / "config.json"
        
        # 確保配置目錄存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 預設配置
        self.defaults = {
            "whisper": {
                "model_size": "turbo",
                "device": "auto",
                "language": "en"
            },
            "gemma": {
                "model_name": "google/gemma-2b-it",
                "device": "auto",
                "target_language": "zh"
            },
            "overlay": {
                "font_size": 24,
                "font_color": [255, 255, 255],
                "bg_color": [0, 0, 0, 180],
                "shadow_enabled": True,
                "shadow_strength": 5,
                "position": 80
            },
            "stream": {
                "chunk_duration": 3,
                "buffer_size": 5
            },
            "ui": {
                "theme": "default",
                "window_geometry": {
                    "x": 100,
                    "y": 100,
                    "width": 800,
                    "height": 600
                }
            }
        }
        
        # 載入配置
        self.config = self.load()
        
    def load(self):
        """載入配置檔案"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                # 合併使用者配置和預設配置
                config = self.defaults.copy()
                self._deep_update(config, user_config)
                return config
                
            except Exception as e:
                print(f"Error loading config: {e}")
                
        return self.defaults.copy()
        
    def save(self):
        """儲存配置到檔案"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key_path, default=None):
        """
        獲取配置值
        
        Args:
            key_path: 配置路徑，例如 "whisper.model_size"
            default: 預設值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    def set(self, key_path, value):
        """
        設定配置值
        
        Args:
            key_path: 配置路徑
            value: 值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 導航到父節點
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        # 設定值
        config[keys[-1]] = value
        
        # 自動儲存
        self.save()
        
    def _deep_update(self, base_dict, update_dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
                
    def reset(self):
        """重置為預設配置"""
        self.config = self.defaults.copy()
        self.save()