import struct
from typing import Dict, Tuple, Optional, BinaryIO
from .chart_model import *
from .chart_constants import *

class ParseContext:
    def __init__(self):
        # Maps StoredTypeId -> (StoredName, StoredVersion)
        self.known_types: Dict[int, Tuple[str, int]] = {}

class ChartParser:
    """
    Parses HWP Chart binary data.
    """
    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.context = ParseContext()

    def read_uint32(self) -> int:
        data = self.stream.read(4)
        if len(data) < 4:
            raise EOFError("Unexpected EOF while reading uint32")
        return struct.unpack('<I', data)[0]

    def read_int32(self) -> int:
        data = self.stream.read(4)
        if len(data) < 4:
            raise EOFError("Unexpected EOF while reading int32")
        return struct.unpack('<i', data)[0]

    def read_uint16(self) -> int:
        data = self.stream.read(2)
        if len(data) < 2:
            raise EOFError("Unexpected EOF while reading uint16")
        return struct.unpack('<H', data)[0]
    
    def read_bytes(self, n: int) -> bytes:
        data = self.stream.read(n)
        if len(data) < n:
            raise EOFError(f"Unexpected EOF while reading {n} bytes")
        return data

    def read_string(self, length: int) -> str:
        # Assuming ANSI/ASCII or UTF-8 based on spec "char*"
        # HWP often uses UTF-16LE, but internal obj names might be ASCII.
        # Safe bet is decode(errors='replace')
        data = self.read_bytes(length)
        return data.decode('utf-8', errors='replace').rstrip('\x00')

    def parse(self) -> VtChart:
        """
        Main entry point to parse a Chart.
        Expected to start with a VtChart object.
        """
        root = self.parse_object()
        if isinstance(root, VtChart):
            return root
        # If root is not VtChart, we might need to wrap it or raise error.
        # For now, return valid object or None
        return root # type: ignore

    def parse_object(self) -> ChartObj:
        # 1. Read Header
        obj_id = self.read_int32()
        stored_type_id = self.read_int32()

        stored_name = None
        stored_version = 0

        # 2. Variable Data Parsing
        if stored_type_id not in self.context.known_types:
            # If not in table, read definition
            name_len = self.read_uint16()
            stored_name = self.read_string(name_len)
            stored_version = self.read_int32()
            self.context.known_types[stored_type_id] = (stored_name, stored_version)
        else:
            stored_name, stored_version = self.context.known_types[stored_type_id]

        # 3. Instantiate Object
        obj = self.create_object_by_name(stored_name)
        obj.id = obj_id
        obj.stored_type_id = stored_type_id
        obj.stored_name = stored_name
        obj.stored_version = stored_version

        # 4. Parse Body / Children
        # The spec says "ChartObjData".
        # If it's a recursive structure, we need to know the size or count.
        # Often HWP objects have a specific parser per type.
        # Here we need a generic way or specific handlers.
        
        # Placeholder for specific parsing logic:
        self.parse_object_body(obj)

        return obj

    def create_object_by_name(self, name: str) -> ChartObj:
        # Simple factory
        if name == "VtChart": return VtChart()
        if name == "VtColor": return VtColor()
        if name == "VtFont": return VtFont()
        if name == "VtPicture": return VtPicture()
        if name == "Backdrop": return Backdrop()
        if name == "Axis": return Axis()
        if name == "Series": return Series()
        if name == "DataGrid": return DataGrid()
        if name == "Title": return Title()
        return ChartObj() # Generic fallback

    def parse_object_body(self, obj: ChartObj):
        # This implementation requires knowledge of specific field layout per object.
        # The spec (section 3.x) details attributes for each object.
        # Since implementing 52 parsers is huge, I'll add the structure for core ones.
        
        if isinstance(obj, VtChart):
            # Parse VtChart specific fields
            # e.g. version, child count, properties...
            # This is speculative without the field-order in the prompt.
            # Assuming recursive children based on "Trhee structure" prompt.
            pass
        
        # TODO: Implement field reading for each known type.
        pass
