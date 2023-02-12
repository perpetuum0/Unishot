from enum import Enum

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPixmap


class Screenshot:
    Pixmap: QPixmap
    Position: QPoint

    def __init__(self, pixmap: QPixmap, position: QPoint) -> None:
        super().__init__()
        self.Pixmap = pixmap
        self.Position = position

    def __iter__(self):
        return iter([self.Pixmap, self.Position])


class ResizePointAlignment(Enum):
    TopLeft = 1
    Top = 2
    TopRight = 3
    CenterLeft = 4
    CenterRight = 5
    BottomLeft = 6
    Bottom = 7
    BottomRight = 8


class ToolkitOrientation(Enum):
    Horizontal = 0
    Vertical = 1


class DrawTools(Enum):
    # Values represent icon names
    Brush = "brush"
    Line = "line"
    Arrow = "arrow"
    Square = "square"
    Ellipse = "circle"
    Text = "text"


class ToolkitButtons(Enum):
    # Values represent icon names or corresponding DrawTool
    Save = "save"
    Copy = "copy"
    Close = "close"
    Cursor = "cursor"
    DrawBrush = DrawTools.Brush
    DrawLine = DrawTools.Line
    DrawArrow = DrawTools.Arrow
    DrawSquare = DrawTools.Square
    DrawEllipse = DrawTools.Ellipse
    DrawText = DrawTools.Text
