from typing import NamedTuple
from enum import Enum

from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QPixmap


class PostEffects():
    class FlipAxis():
        x: int
        y: int

        def __init__(self) -> None:
            self.x = 1
            self.y = 1

    __angle: int
    flip: FlipAxis

    def __init__(self, angle=0, flip=FlipAxis()) -> None:
        self.__angle = angle
        self.flip = flip

    def setAngle(self, angle: int) -> None:
        self.__angle = angle % 360

    def angle(self) -> int:
        return self.__angle

    def clear(self) -> None:
        self.__angle = 0
        self.flip.x = 1
        self.flip.y = 1


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
    FlipVer = "flip_vertical"
    FlipHor = "flip_horizontal"
    Color = "color"
    Cursor = "cursor"
    DrawBrush = DrawTools.Brush
    DrawLine = DrawTools.Line
    DrawArrow = DrawTools.Arrow
    DrawSquare = DrawTools.Square
    DrawEllipse = DrawTools.Ellipse
    DrawText = DrawTools.Text
