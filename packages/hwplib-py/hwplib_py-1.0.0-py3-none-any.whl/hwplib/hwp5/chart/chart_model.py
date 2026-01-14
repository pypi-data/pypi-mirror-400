from typing import List, Optional
from .chart_constants import *

class ChartObj:
    """
    Base class for all Chart objects.
    Corresponds to the binary structure with ID, StoredTypeId, etc.
    """
    def __init__(self):
        self.id: int = 0
        self.stored_type_id: int = 0
        self.stored_name: Optional[str] = None
        self.stored_version: int = 0
        self.children: List['ChartObj'] = []

class VtColor(ChartObj):
    """
    VtColor (3.2)
    Represents an RGB color.
    """
    def __init__(self):
        super().__init__()
        self.red: int = 0
        self.green: int = 0
        self.blue: int = 0
        self.alpha: int = 0 # Sometimes used?
        self.index: int = 0 # Color index in palette

class VtFont(ChartObj):
    """
    VtFont (3.3)
    Represents font attributes.
    """
    def __init__(self):
        super().__init__()
        self.name: str = "Arial"
        self.size: float = 10.0
        self.bold: bool = False
        self.italic: bool = False
        self.underline: bool = False
        self.strikeout: bool = False
        self.color: Optional[VtColor] = None

class VtPicture(ChartObj):
    """
    VtPicture (3.4)
    Represents an image/picture.
    """
    def __init__(self):
        super().__init__()
        self.path: str = ""
        self.type: PictureType = PictureType.Bitmap

class Brush(ChartObj):
    """
    Brush (3.13)
    Defines the fill style.
    """
    def __init__(self):
        super().__init__()
        self.style: BrushStyle = BrushStyle.Solid
        self.color: Optional[VtColor] = None
        self.pattern_color: Optional[VtColor] = None # For Hatch/Pattern

class Pen(ChartObj):
    """
    Pen (3.42)
    Defines line style.
    """
    def __init__(self):
        super().__init__()
        self.style: PenStyle = PenStyle.Solid
        self.width: int = 1
        self.color: Optional[VtColor] = None

class Backdrop(ChartObj):
    """
    Backdrop (3.11)
    Defines the background area styling (shadow, frame, fill).
    """
    def __init__(self):
        super().__init__()
        self.shadow_style: ShadowStyle = ShadowStyle.Drop
        self.frame_style: FrameStyle = FrameStyle.Flat
        self.fill_color: Optional[VtColor] = None

class AxisTitle(ChartObj):
    """
    AxisTitle (3.10)
    """
    def __init__(self):
        super().__init__()
        self.text: str = ""
        self.font: Optional[VtFont] = None
        self.orientation: Orientation = Orientation.Horizontal

class Axis(ChartObj):
    """
    Axis (3.7)
    Represents a chart axis (X, Y, Z).
    """
    def __init__(self):
        super().__init__()
        self.axis_id: AxisId = AxisId.AxisX
        self.title: Optional[AxisTitle] = None
        self.visible: bool = True
        self.pen: Optional[Pen] = None
        self.major_grid: Optional['AxisGrid'] = None
        self.minor_grid: Optional['AxisGrid'] = None
        self.scale: Optional['Scale'] = None

class AxisGrid(ChartObj):
    """
    AxisGrid (3.8)
    """
    def __init__(self):
        super().__init__()
        self.visible: bool = False
        self.pen: Optional[Pen] = None

class Scale(ChartObj):
    """
    Scale (3.9)
    """
    def __init__(self):
        super().__init__()
        self.log_base: float = 10.0
        self.min: float = 0.0
        self.max: float = 100.0
        self.type: ScaleType = ScaleType.Linear

class DataPoint(ChartObj):
    """
    DataPoint (3.20)
    """
    def __init__(self):
        super().__init__()
        self.uid: int = 0
        self.brush: Optional[Brush] = None
        self.pen: Optional[Pen] = None
        self.marker: Optional[ChartObj] = None # VtMarker

class View3D(ChartObj):
    """
    View3D (3.60)
    """
    def __init__(self):
        super().__init__()
        self.rotation: float = 0.0
        self.elevation: float = 0.0
        self.perspective: int = 0


class Series(ChartObj):
    """
    Series (3.49)
    Represents a data series.
    """
    def __init__(self):
        super().__init__()
        self.series_type: SeriesType = SeriesType.Bar
        self.name: str = ""
        self.pen: Optional[Pen] = None
        self.brush: Optional[Brush] = None

class DataGrid(ChartObj):
    """
    DataGrid (3.19)
    Holds the raw data for the chart.
    Row/Column oriented.
    """
    def __init__(self):
        super().__init__()
        self.rows: int = 0
        self.cols: int = 0
        self.data: List[List[float]] = []
        self.row_labels: List[str] = []
        self.col_labels: List[str] = []
        self.annotations: List[str] = []


class Title(ChartObj):
    """
    Chart Title
    """
    def __init__(self):
        super().__init__()
        self.text: str = ""
        self.font: Optional[VtFont] = None
        self.backdrop: Optional[Backdrop] = None
        self.location: Optional['Location'] = None

class Location(ChartObj):
    """
    Location (3.39)
    """
    def __init__(self):
        super().__init__()
        self.x: int = 0
        self.y: int = 0
        self.width: int = 0
        self.height: int = 0

class VtChart(ChartObj):
    """
    VtChart (3.1)
    Root object of the chart structure.
    """
    def __init__(self):
        super().__init__()
        self.chart_type: ChartType = ChartType.Bar
        self.title: Optional[Title] = None
        self.legend: Optional[ChartObj] = None # VtLegend to implemented
        self.data_grid: Optional[DataGrid] = None
        self.axes: List[Axis] = []
        self.series_collection: List[Series] = []
        self.backdrop: Optional[Backdrop] = None
        self.view3d: Optional[View3D] = None
        self.plot_base: Optional[ChartObj] = None # VtPlotBase


# Note: Many more classes to be implemented as per the 52 items list.
# This serves as the foundation.
