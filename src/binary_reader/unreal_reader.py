from typing import Dict, Any
from .base_reader import BinaryReader

class UnrealAssetReader(BinaryReader):
    MAGIC = 0xC1832A9E

    def read_header(self) -> Dict[str, Any]:
        magic = self.read_uint32()
        if magic != self.MAGIC:
            raise ValueError("Not a valid .uasset file")

        return {
            'magic': hex(magic),
            'legacy_version': self.read_uint32(),
            'legacy_ue3_version': self.read_uint32(),
            'file_version_ue4': self.read_uint32(),
            'file_size': self.read_uint32()
        }

    def read_metadata(self) -> Dict[str, Any]:
        # Read bulk data flags
        flags = self.read_uint32()
        
        # Read element count
        element_count = self.read_uint32()
        
        # Read bulk data size
        bulk_data_size = self.read_uint32()
        
        return {
            'flags': flags,
            'element_count': element_count,
            'bulk_data_size': bulk_data_size
        }

    def read_name_table(self) -> list[str]:
        names_count = self.read_int32()
        names = []
        
        for _ in range(names_count):
            name = self.read_string()
            names.append(name)
            
        return names