from typing import NamedTuple
from enum import Enum
import aenum

from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPixmap


class Screenshot(NamedTuple):
    Geometry: QRect
    Pixmap: QPixmap


class Drawing(NamedTuple):
    Position: QPoint
    Pixmap: QPixmap


# Ignore duplicate values with aenum
class ResizePointAlignment(aenum.Enum):
    _settings_ = aenum.NoAlias

    TopLeft = "dx"
    Top = "y"
    TopRight = "dy"
    CenterLeft = "x"
    CenterRight = "x"
    BottomLeft = "dy"
    Bottom = "y"
    BottomRight = "dx"


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


class ToolkitButtonTypes(Enum):
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
    Separator = "separator"
    DrawBrush = DrawTools.Brush
    DrawLine = DrawTools.Line
    DrawArrow = DrawTools.Arrow
    DrawSquare = DrawTools.Square
    DrawEllipse = DrawTools.Ellipse
    DrawText = DrawTools.Text
