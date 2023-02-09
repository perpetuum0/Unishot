from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QMouseEvent

from typings import DrawTools


class Draw(QWidget):
    Tools = DrawTools

    active: bool
    tool: Tools
    drawings: list

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.UpArrowCursor)  # Debug
        self.stop()

    def start(self, tool: Tools):
        self.active = True
        self.tool = tool
        self.show()

    def stop(self):
        self.active = True
        self.hide()

    def setCanvas(self, rect: QRect):
        self.setGeometry(rect)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        event.accept()
