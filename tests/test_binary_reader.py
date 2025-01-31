import pytest
import os
from src.binary_reader import UnrealAssetReader, BinaryReader

@pytest.fixture
def test_unreal_asset_file(tmp_path):
    # Create a mock .uasset file for testing
    file_path = tmp_path / "test.uasset"
    with open(file_path, "wb") as f:
        # Write magic number
        f.write(bytes.fromhex('C1832A9E'))
        # Write mock version numbers
        f.write(int(1).to_bytes(4, 'little'))  # legacy_version
        f.write(int(2).to_bytes(4, 'little'))  # legacy_ue3_version
        f.write(int(3).to_bytes(4, 'little'))  # file_version_ue4
        f.write(int(100).to_bytes(4, 'little'))  # file_size
        # Write mock metadata
        f.write(int(1).to_bytes(4, 'little'))  # flags
        f.write(int(10).to_bytes(4, 'little'))  # element_count
        f.write(int(1000).to_bytes(4, 'little'))  # bulk_data_size
    return file_path

def test_unreal_asset_reader_header(test_unreal_asset_file):
    with UnrealAssetReader(test_unreal_asset_file) as reader:
        header = reader.read_header()
        assert header['magic'] == '0xc1832a9e'
        assert header['legacy_version'] == 1
        assert header['legacy_ue3_version'] == 2
        assert header['file_version_ue4'] == 3
        assert header['file_size'] == 100

def test_unreal_asset_reader_metadata(test_unreal_asset_file):
    with UnrealAssetReader(test_unreal_asset_file) as reader:
        # Skip header
        reader.read_header()
        metadata = reader.read_metadata()
        assert metadata['flags'] == 1
        assert metadata['element_count'] == 10
        assert metadata['bulk_data_size'] == 1000

def test_invalid_unreal_asset_file(tmp_path):
    file_path = tmp_path / "invalid.uasset"
    with open(file_path, "wb") as f:
        f.write(b"invalid data")
    
    with pytest.raises(ValueError, match="Not a valid .uasset file"):
        with UnrealAssetReader(file_path) as reader:
            reader.read_header()