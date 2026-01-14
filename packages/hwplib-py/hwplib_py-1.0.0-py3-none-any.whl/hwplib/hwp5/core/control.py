import struct
from .defs import HwpUnit

class HwpControl:
    """
    Base class for all HWP Controls.
    """
    def __init__(self, ctrl_id: str):
        self.ctrl_id = ctrl_id  # e.g., 'tbl', 'pic', 'eq '
        self.properties = {} # Generic properties container

class Cell:
    """
    Represents a Table Cell.
    Effectively a mini-document containing Paragraphs.
    """
    def __init__(self):
        self.paragraphs = [] # List of Paragraphs
        self.col_index = 0
        self.row_index = 0
        self.col_span = 1
        self.row_span = 1
        self.width = 0
        self.height = 0

class Row:
    """
    Represents a Table Row.
    """
    def __init__(self):
        self.cells: list[Cell] = []

class ControlTable(HwpControl):
    """
    Table Control (ctrl_id='tbl')
    """
    def __init__(self):
        super().__init__('tbl')
        self.row_count: int = 0
        self.col_count: int = 0
        self.cell_spacing: int = 0
        self.rows: list[Row] = [] # List of Rows

    def get_text(self) -> str:
        """
        Recursively extract text from all cells.
        """
        lines = []
        for row in self.rows:
            row_texts = []
            for cell in row.cells:
                cell_text = "\n".join([p.text for p in cell.paragraphs])
                row_texts.append(cell_text)
            lines.append("\t".join(row_texts)) # Tab separation for cells
        return "\n".join(lines)

class ControlPicture(HwpControl):
    """
    Picture Control (ctrl_id='pic')
    """
    def __init__(self):
        super().__init__('pic')
        self.width = HwpUnit(0)
        self.height = HwpUnit(0)
        self.bin_item_id = 0 # Link to BinData

class ControlEquation(HwpControl):
    """
    Equation Control (ctrl_id='eq ')
    """
    def __init__(self):
        super().__init__('eq ')
        self.script: str = "" # The equation script
        self.version: str = ""

    def get_text(self) -> str:
        """
        Returns the equation script.
        """
        return self.script

class ControlHeader(HwpControl):
    """
    Header (Head) Control
    """
    def __init__(self):
        super().__init__('head')
        self.paragraphs = []

class ControlFooter(HwpControl):
    """
    Footer (Foot) Control
    """
    def __init__(self):
        super().__init__('foot')
        self.paragraphs = []

class ControlLine(HwpControl):
    """
    Line GSO (ctrl_id='lin')
    """
    def __init__(self):
        super().__init__('lin')
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

class ControlRect(HwpControl):
    """
    Rectangle GSO (ctrl_id='rec')
    """
    def __init__(self):
        super().__init__('rec')
        self.width = 0
        self.height = 0
        self.attr = 0

class ControlEllipse(HwpControl):
    """
    Ellipse GSO (ctrl_id='ell')
    """
    def __init__(self):
        super().__init__('ell')
        self.axis_x = 0
        self.axis_y = 0

class ControlPolygon(HwpControl):
    """
    Polygon GSO (ctrl_id='pol')
    """
    def __init__(self):
        super().__init__('pol')
        self.points = []


class ControlParser:
    """
    Factory validation logic for controls.
    """
    @staticmethod
    def parse_header(data: bytes):
        """
        Parses common control header (4 bytes ID).
        """
        if len(data) < 4:
            return None
        # Tag ID is reversed in binary usually? e.g. "tbl " -> 0x206c6274
        # Or standard string.
        # HWP spec says Control ID is 4 bytes.
        ctrl_id = data[:4].decode('ascii', errors='ignore')[::-1].strip()
        return ctrl_id
