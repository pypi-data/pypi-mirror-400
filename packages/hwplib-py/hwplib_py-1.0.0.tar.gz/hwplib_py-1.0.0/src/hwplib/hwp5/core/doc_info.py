import struct
import io
from typing import List, Optional
from .record import HwpRecord, RecordParser
from .defs import HwpTag, HwpUnit, ColorRef

class FaceName:
    """
    HWPTAG_FACE_NAME (Font)
    """
    def __init__(self, name: str):
        self.name = name

class BorderFill:
    """
    HWPTAG_BORDER_FILL
    """
    def __init__(self):
        self.property_brush = 0
        # Placeholder for complex border/fill properties
        
class CharShape:
    """
    HWPTAG_CHAR_SHAPE (Character Shape)
    """
    def __init__(self):
        self.height = HwpUnit(1000) # Default 10pt
        self.font_ids = [0, 0, 0, 0, 0, 0, 0] # Hangul, Latin, Hanja, Japanese, Crypto, Symbol, User
        self.ratio = [100] * 7
        self.spacing = [0] * 7
        self.offset = [0] * 7
        self.text_color: ColorRef = ColorRef(0, 0, 0)
        self.shade_color: ColorRef = ColorRef(255, 255, 255) # None/Transparent usually
        self.shadow_color: ColorRef = ColorRef(192, 192, 192)
        # Bold, Italic, etc are in a property bitmask

class ParaShape:
    """
    HWPTAG_PARA_SHAPE (Paragraph Shape)
    """
    def __init__(self):
        self.left_margin = HwpUnit(0)
        self.right_margin = HwpUnit(0)
        self.align_type = 0 # Left, Center, Right...
        self.line_spacing = 160 # %
        self.border_fill_id = 0

class DocInfo:
    """
    Container for all Document Information resources.
    """
    def __init__(self):
        self.face_names: List[FaceName] = []
        self.border_fills: List[BorderFill] = []
        self.char_shapes: List[CharShape] = []
        self.para_shapes: List[ParaShape] = []
        self.styles: List[any] = []
        
        self.id_mappings = {} # Tag -> Count or List

    def parse(self, stream: io.BytesIO) -> None:
        """
        Parses the DocInfo stream records.
        """
        parser = RecordParser(stream)
        for record in parser.parse_records():
            self._process_record(record)

    def _process_record(self, record: HwpRecord):
        if record.tag_id == HwpTag.HWPTAG_FACE_NAME:
            self._parse_face_name(record)
        elif record.tag_id == HwpTag.HWPTAG_BORDER_FILL:
            self._parse_border_fill(record)
        elif record.tag_id == HwpTag.HWPTAG_CHAR_SHAPE:
            self._parse_char_shape(record)
        elif record.tag_id == HwpTag.HWPTAG_PARA_SHAPE:
            self._parse_para_shape(record)
        elif record.tag_id == HwpTag.HWPTAG_DOCUMENT_PROPERTIES:
            # First record usually
            pass
            
    def _parse_face_name(self, record: HwpRecord):
        # HWP FaceName Record usually contains the font name.
        # Structure varies by version but simply decoding might reveal the name.
        try:
            # Attempt to decode content to find the font name
            # HWP text is often utf-16le.
            name = record.content.decode('utf-16le', errors='ignore').strip()
            # If name is empty or weird, fallback
            name = name.replace('\x00', '')
            if not name: name = "Unknown Font"
            self.face_names.append(FaceName(name))
        except:
             self.face_names.append(FaceName("Parse Error"))

    def _parse_border_fill(self, record: HwpRecord):
        self.border_fills.append(BorderFill())

    def _parse_char_shape(self, record: HwpRecord):
        self.char_shapes.append(CharShape())

    def _parse_para_shape(self, record: HwpRecord):
        self.para_shapes.append(ParaShape())
