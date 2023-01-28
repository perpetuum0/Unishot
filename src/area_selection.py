from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import QRect


class AreaSelection(QWidget):
    screenshot: QPixmap
    selectionLabel: QLabel
    selectionArea: QRect
    borderWidth: int = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__()
        self.setParent(parent)
        self.move(0, 0)

        self.selectionLabel = QLabel(self)
        self.selectionLabel.setStyleSheet(
            f"border: {self.borderWidth}px dotted white")
        self.selectionLabel.show()

        # tools menu here...

        self.show()

    def start(self, newShot: QPixmap) -> None:
        self.screenshot = newShot
        self.setFixedSize(newShot.size())
        self.selectionArea = QRect(0, 0, 0, 0)
        self.selectionLabel.clear()
        self.updatePreview()

    def updatePreview(self) -> None:
        self.selectionLabel.setGeometry(self.selectionArea.normalized())

        # Adjust to border width
        self.selectionLabel.move(
            self.selectionLabel.pos().x()-self.borderWidth,
            self.selectionLabel.pos().y()
        )

        self.selectionLabel.setPixmap(
            self.screenshot.copy(self.selectionArea.normalized())
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.selectionArea.moveTo(event.pos())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.selectionArea.setCoords(
            self.selectionArea.x(), self.selectionArea.y(),
            event.pos().x(), event.pos().y()
        )

        self.updatePreview()
        event.accept()
