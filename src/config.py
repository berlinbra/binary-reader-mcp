import os
from typing import Dict, Any

class Config:
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    MAX_FILE_SIZE: int = 1024 * 1024 * 100  # 100MB
    
    SUPPORTED_FORMATS: Dict[str, Any] = {
        "unreal": {
            "extensions": [".uasset"],
            "magic": bytes.fromhex('C1832A9E')
        }
    }