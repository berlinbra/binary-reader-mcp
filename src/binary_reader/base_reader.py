from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any
import struct

class BinaryReader(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._file: BinaryIO | None = None
        self._position = 0

    def __enter__(self):
        self._file = open(self.file_path, 'rb')
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()
    
    def read_bytes(self, size: int) -> bytes:
        if not self._file:
            raise ValueError("File is not open")
        data = self._file.read(size)
        self._position += len(data)
        return data

    def read_uint32(self) -> int:
        return struct.unpack('<I', self.read_bytes(4))[0]

    def read_int32(self) -> int:
        return struct.unpack('<i', self.read_bytes(4))[0]

    def read_float(self) -> float:
        return struct.unpack('<f', self.read_bytes(4))[0]

    def read_string(self, encoding='utf-8') -> str:
        length = self.read_int32()
        if length == 0:
            return ""
        elif length < 0:
            length = abs(length)
            data = self.read_bytes(length * 2)
            return data.decode('utf-16-le').rstrip('\0')
        else:
            data = self.read_bytes(length)
            return data.decode(encoding).rstrip('\0')

    def seek(self, position: int) -> None:
        if not self._file:
            raise ValueError("File is not open")
        self._file.seek(position)
        self._position = position

    @property
    def position(self) -> int:
        return self._position

    @abstractmethod
    def read_header(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def read_metadata(self) -> Dict[str, Any]:
        pass