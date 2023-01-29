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
