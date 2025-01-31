from typing import BinaryIO, Dict, Any
import os

def get_file_size(file_path: str) -> int:
    """Get the size of a file in bytes."""
    return os.path.getsize(file_path)

def read_file_header(file: BinaryIO, size: int = 16) -> bytes:
    """Read the first n bytes of a file."""
    current_pos = file.tell()
    file.seek(0)
    header = file.read(size)
    file.seek(current_pos)
    return header

def detect_file_format(header: bytes) -> str:
    """Detect file format based on magic numbers/headers."""
    if len(header) < 4:
        return "unknown"
        
    # Unreal Engine .uasset
    if header[:4] == bytes.fromhex('C1832A9E'):
        return "unreal"
        
    # Add more format detection here
    
    return "unknown"