import struct
import io
from typing import List, Optional
from .record import HwpRecord, RecordParser
from .defs import HwpTag

class ParaHeader:
    """
    HWPTAG_PARA_HEADER (Paragraph Header)
    """
    def __init__(self):
        self.text_len = 0 # Characters count
        self.control_mask = 0
        self.para_shape_id = 0
        self.style_id = 0
        self.divide_sort = 0
        self.char_shape_count = 0
        self.range_tag_count = 0
        self.align_type = 0
        self.instance_id = 0
        
    def parse(self, data: bytes):
        # Based on HWP 5.0 Spec:
        # text_len (DWORD), control_mask (DWORD), para_shape_id (WORD), style_id (BYTE), 
        # divide_sort (BYTE), char_shape_count (WORD), range_tag_count (WORD), 
        # align_type (WORD), instance_id (DWORD), etc.
        # Total size usually varies but minimal is important.
        if len(data) < 16:
            # Fallback or partial
            return
            
        unpacked = struct.unpack('<IIHBBHHI', data[:20]) # reading 20 bytes
        self.text_len = unpacked[0]
        self.control_mask = unpacked[1]
        self.para_shape_id = unpacked[2]
        self.style_id = unpacked[3]
        self.divide_sort = unpacked[4]
        self.char_shape_count = unpacked[5]
        self.range_tag_count = unpacked[6]
        self.instance_id = unpacked[7]

class CharShapePointer:
    """
    Maps a range of text to a CharShape ID.
    """
    def __init__(self, pos: int, shape_id: int):
        self.pos = pos
        self.shape_id = shape_id

class Paragraph:
    """
    Represents a single Paragraph.
    """
    def __init__(self):
        self.header = ParaHeader()
        self.text = ""
        self.char_shape_pointers: List[CharShapePointer] = []
        self.controls = [] # List of controls (Tables, Pictures, etc)

    def set_text(self, data: bytes):
        """
        Parses HWPTAG_PARA_TEXT.
        Text is compressed unicode (sometimes) or standard UTF-16LE.
        Usually standard UTF-16LE in HWP 5.0.
        """
        # "Special" HWP unicode transformation might apply for control chars
        # But mostly utf-16le.
        try:
            self.text = data.decode('utf-16le', errors='replace')
            # Remove null terminator if present
            if self.text and self.text[-1] == '\x00':
                self.text = self.text[:-1]
        except:
            self.text = "[Decoding Error]"

    def set_char_shape(self, data: bytes):
        """
        Parses HWPTAG_PARA_CHAR_SHAPE.
        List of (Position, ShapeID).
        """
        # Structure: Pos(DWORD), ShapeId(DWORD) repeated?
        # Check spec. Usually Pos(UINT), ShapeId(UINT).
        count = len(data) // 8
        for i in range(count):
            pos, shape_id = struct.unpack('<II', data[i*8 : (i+1)*8])
            self.char_shape_pointers.append(CharShapePointer(pos, shape_id))

from .control import ControlParser, ControlTable, ControlPicture, ControlEquation, HwpControl, ControlLine, ControlRect, ControlEllipse, ControlPolygon

class Section:
    """
    Represents a Section (Stream).
    Contains a list of Paragraphs.
    """
    def __init__(self):
        self.paragraphs: List[Paragraph] = []

    def parse(self, stream: io.BytesIO) -> None:
        """
        Iterates over records in the stream and builds a list of Paragraph objects.
        
        Args:
            stream (io.BytesIO): The binary stream containing body text records.
        """
        parser = RecordParser(stream)
        current_para: Optional[Paragraph] = None
        
        # State tracking for multi-record controls (like Tables)
        # In this linear parsing model, nested structures (like Table Cells)
        # are flattened into the paragraph list.
        # This preserves text order but does not populate hierarchical Control models deep properties.
        
        for record in parser.parse_records():
            if record.tag_id == HwpTag.HWPTAG_PARA_HEADER:
                # Start new paragraph
                current_para = Paragraph()
                current_para.header.parse(record.content)
                self.paragraphs.append(current_para)
                
            elif record.tag_id == HwpTag.HWPTAG_PARA_TEXT:
                if current_para:
                    current_para.set_text(record.content)
                    
            elif record.tag_id == HwpTag.HWPTAG_PARA_CHAR_SHAPE:
                if current_para:
                    current_para.set_char_shape(record.content)
            
            elif record.tag_id == HwpTag.HWPTAG_CTRL_HEADER:
                # Found a generic control header (e.g. "tbl ", "eq ", "pic ")
                if current_para:
                    ctrl_id = ControlParser.parse_header(record.content)
                    if ctrl_id:
                        # Instantiate generic wrapper first
                        ctrl = HwpControl(ctrl_id)
                        current_para.controls.append(ctrl)
            
            elif record.tag_id == HwpTag.HWPTAG_TABLE:
                # Found a Table property record
                if current_para and current_para.controls:
                    last_ctrl = current_para.controls[-1]
                    if last_ctrl.ctrl_id == 'tbl':
                        # upgrade to concrete class
                        tbl = ControlTable()
                        # TODO: parse specific table properties (row count etc) from record.content
                        current_para.controls[-1] = tbl # Replace generic with specific
            
            elif record.tag_id == HwpTag.HWPTAG_PICTURE: # or SHAPE_COMPONENT_PICTURE in some ver
                if current_para and current_para.controls:
                    last_ctrl = current_para.controls[-1]
                    if last_ctrl.ctrl_id == 'pic':
                        pic = ControlPicture()
                        current_para.controls[-1] = pic
                        
            elif record.tag_id == HwpTag.HWPTAG_EQEDIT:
                if current_para and current_para.controls:
                    last_ctrl = current_para.controls[-1]
                    if last_ctrl.ctrl_id == 'eq ':
                         eq = ControlEquation()
                         # Parse script from content
                         # eq.script = ...
                         current_para.controls[-1] = eq

            elif record.tag_id == HwpTag.HWPTAG_LIST_HEADER:
                # 1. Parse List Header Properties
                # para_count (DWORD), property (DWORD), text_width (DWORD), text_height (DWORD)
                # min size 16 bytes
                if len(record.content) >= 16:
                     para_count, prop, width, height = struct.unpack('<IIII', record.content[:16])
                     # We must consume exactly 'para_count' paragraphs from the *following* records.
                     # However, RecordParser yields records sequentially.
                     # Since this structure is flat in the stream (ListHeader -> Para1 -> Para2 ... -> ParaHeader -> ...),
                     # we can just continue parsing. The *logical* grouping is what matters.
                     # For a simple 'get_text' linear extraction, adding them to self.paragraphs is acceptable,
                     # as they appear in reading order.
                     # For a strict structural parse, we would capture them into a list.
                     
                     # Let's perform a "Logical Grouping" by creating a special Paragraph container?
                     # Or simpler: Just acknowledge we are entering a list.
                     pass
                     
                # Note: In a robust implementation, we would pass a 'limit' to a recursive parse call.
                # But since RecordParser is an iterator, we can't easily 'fork' it without buffering.
                # Existing behavior (appending to self.paragraphs) actually preserves READ ORDER,
                # so 'get_text()' will return cell text in order of appearance.
                # This meets the requirement for "Text Extraction".
                
            # Drawing Objects (GSO)
            elif record.tag_id == HwpTag.HWPTAG_SHAPE_COMPONENT_LINE:
                if current_para and current_para.controls and current_para.controls[-1].ctrl_id == 'lin':
                    current_para.controls[-1] = ControlLine()

            elif record.tag_id == HwpTag.HWPTAG_SHAPE_COMPONENT_RECTANGLE:
                if current_para and current_para.controls and current_para.controls[-1].ctrl_id == 'rec':
                    current_para.controls[-1] = ControlRect()

            elif record.tag_id == HwpTag.HWPTAG_SHAPE_COMPONENT_ELLIPSE:
                if current_para and current_para.controls and current_para.controls[-1].ctrl_id == 'ell':
                    current_para.controls[-1] = ControlEllipse()

            elif record.tag_id == HwpTag.HWPTAG_SHAPE_COMPONENT_POLYGON:
                if current_para and current_para.controls and current_para.controls[-1].ctrl_id == 'pol':
                    current_para.controls[-1] = ControlPolygon()
