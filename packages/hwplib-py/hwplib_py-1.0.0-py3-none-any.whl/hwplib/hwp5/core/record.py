import struct
from typing import BinaryIO, Generator, Tuple

class HwpRecord:
    """
    Represents a single HWP Record.
    """
    def __init__(self, tag_id: int, level: int, size: int, content: bytes):
        self.tag_id = tag_id
        self.level = level
        self.size = size
        self.content = content

class RecordParser:
    """
    Parses a stream of HWP Records.
    Logic:
        Header (4 bytes):
            Tag ID (10 bits)
            Level (10 bits)
            Size (12 bits)
    """
    def __init__(self, stream: BinaryIO):
        self.stream = stream

    def parse_records(self) -> Generator[HwpRecord, None, None]:
        while True:
            header_bytes = self.stream.read(4)
            if len(header_bytes) < 4:
                break # EOF

            header_val = struct.unpack('<I', header_bytes)[0]
            
            tag_id = header_val & 0x3FF
            level = (header_val >> 10) & 0x3FF
            size = (header_val >> 20) & 0xFFF
            
            # 4095 (0xFFF) means size is > 4095 bytes.
            # In this case, 4 bytes follow specifying the real size.
            if size == 0xFFF:
                size_bytes = self.stream.read(4)
                if len(size_bytes) < 4:
                    raise EOFError("Unexpected EOF reading extended record size")
                size = struct.unpack('<I', size_bytes)[0]
            
            content = self.stream.read(size)
            if len(content) < size:
                raise EOFError(f"Unexpected EOF reading record content (Tag: {tag_id}, Size: {size})")
            
            yield HwpRecord(tag_id, level, size, content)
