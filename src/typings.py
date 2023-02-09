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
    Pencil = "Pencil"
    Line = "Line"
    Arrow = "Arrow"
    Square = "Square"
    Ellipse = "Ellipse"


class ToolkitButtons(Enum):
    Save = "Save"
    Copy = "Copy"
    Close = "Close"
    Cursor = "Cursor"
    DrawPencil = DrawTools.Pencil
    DrawLine = DrawTools.Line
    DrawArrow = DrawTools.Arrow
    DrawSquare = DrawTools.Square
    DrawEllipse = DrawTools.Ellipse
