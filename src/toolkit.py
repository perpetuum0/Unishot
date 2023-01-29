from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import QRect, QSize, QPoint


class Toolkit(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.setFixedSize(QSize(300, 25))

        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setFixedSize(self.size())
        blank = QPixmap(self.size())
        blank.fill("white")
        self.backgroundLabel.setPixmap(blank)
