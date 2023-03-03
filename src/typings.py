from typing import NamedTuple
from enum import Enum

from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPixmap


class Screenshot(NamedTuple):
    Geometry: QRect
    Pixmap: QPixmap


class Drawing(NamedTuple):
    Position: QPoint
    Pixmap: QPixmap


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
    Cursor = "cursor"
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
    RotateLeft = "rotate_left"
    RotateRight = "rotate_right"
    FlipVer = "flip_ver"
    FlipHor = "flip_hor"
    Color = "color"
    Cursor = "cursor"
    DrawBrush = DrawTools.Brush
    DrawLine = DrawTools.Line
    DrawArrow = DrawTools.Arrow
    DrawSquare = DrawTools.Square
    DrawEllipse = DrawTools.Ellipse
    DrawText = DrawTools.Text
