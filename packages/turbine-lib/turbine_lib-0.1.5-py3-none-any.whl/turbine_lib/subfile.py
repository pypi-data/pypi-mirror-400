from enum import Enum

class FILE_TYPE(Enum):
    TEXT = '.text'
    JPG = '.jpg'
    DDS='.dds'
    WAV = '.wav'
    OGG = '.ogg'
    FONT = '.fontbin'
    UNKNOWN = '.unknown'

def file_type_from_string(ext):
    """Convert string extension to FILE_TYPE enum"""
    if ext == ".txt":
        return FILE_TYPE.TEXT
    elif ext == ".jpg":
        return FILE_TYPE.JPG
    elif ext == ".dds":
        return FILE_TYPE.DDS
    elif ext == ".wav":
        return FILE_TYPE.WAV
    elif ext == ".ogg":
        return FILE_TYPE.OGG
    elif ext == ".fontbin":
        return FILE_TYPE.FONT
    else:
        return FILE_TYPE.UNKNOWN

def file_type_from_file_contents(file_id, file_data):
    """Determine file type from file contents"""
    # Text check based on file_id
    if (file_id >> 24) == 0x25:
        return FILE_TYPE.TEXT

    # Font check based on file_id
    if (file_id >> 24) == 0x42:
        return FILE_TYPE.FONT

    # jpeg / dds check
    if (file_id >> 24) == 0x41:
        soi = file_data.to_number(2, 24)
        # long long marker = file_data.ToNumber<2>(26)

        # auto markerSize = header.ToNumber<short>(28)
        # auto four = header.ToNumber<int>(30)

        if soi == 0xD8FF:
            return FILE_TYPE.JPG
        return FILE_TYPE.DDS

    # Ogg and Wav check
    if len(file_data) > 11:
        if file_data[8] == 0x4F and file_data[9] == 0x67 and file_data[10] == 0x67 and file_data[11] == 0x53:
            return FILE_TYPE.OGG

        if file_data[8] == 0x52 and file_data[9] == 0x49 and file_data[10] == 0x46 and file_data[11] == 0x46:
            return FILE_TYPE.WAV

    return FILE_TYPE.UNKNOWN

def string_from_file_type(file_type):
    """Convert FILE_TYPE enum to string extension"""
    if file_type == FILE_TYPE.TEXT.value or file_type == FILE_TYPE.TEXT:
        return ".txt"
    elif file_type == FILE_TYPE.JPG.value or file_type == FILE_TYPE.JPG:
        return ".jpg"
    elif file_type == FILE_TYPE.DDS.value or file_type == FILE_TYPE.DDS:
        return ".dds"
    elif file_type == FILE_TYPE.WAV.value or file_type == FILE_TYPE.WAV:
        return ".wav"
    elif file_type == FILE_TYPE.OGG.value or file_type == FILE_TYPE.OGG:
        return ".ogg"
    elif file_type == FILE_TYPE.FONT.value or file_type == FILE_TYPE.FONT:
        return ".fontbin"
    else:
        return ".subfile"

# Template class for Subfile - will be implemented in specific subfile type files
class Subfile:
    """Base class for subfile processing"""
    
    @staticmethod
    def build_for_import(old_data, outer_data):
        raise NotImplementedError("Subclasses must implement this method")
    
    @staticmethod
    def build_for_export(inner_data):
        raise NotImplementedError("Subclasses must implement this method")