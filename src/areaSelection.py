from PySide6.QtWidgets import QWidget, QLabel, QToolTip
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import QRect, QPoint, QPointF
from toolkit import Toolkit


class AreaPreviewLabel(QLabel):
    screenshot: QPixmap
    borderWidth: int
    dragPoint: QPointF

    def __init__(self, parent: QWidget, borderWidth: int) -> None:
        super().__init__(parent)
        self.parent = parent
        self.borderWidth = borderWidth
        self.move(0, 0)

        self.setStyleSheet(
            f"border: {borderWidth}px dotted white")

    def start(self, screenshot) -> None:
        self.screenshot = screenshot
        self.setArea(QRect(0, 0, 0, 0))

    def setArea(self, newArea: QRect) -> None:
        areaNormalized = newArea.normalized()

        self.setGeometry(areaNormalized)

        # Adjust to border width
        self.move(
            self.pos().x()-self.borderWidth,
            self.pos().y()
        )

        self.setPixmap(
            self.screenshot.copy(areaNormalized)
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.dragPoint = event.localPos()
        self.parent.hideToolkit()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.parent.moveSelectionArea(
            QPoint(
                event.globalPos().x()-self.dragPoint.x(),
                event.globalPos().y()-self.dragPoint.y()
            )
        )
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.parent.showToolkit()
        event.accept()


class AreaSelection(QWidget):
    screenshot: QPixmap
    areaPreview: AreaPreviewLabel
    selection: QRect
    borderWidth: int = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setParent(parent)
        self.move(0, 0)

        self.areaPreview = AreaPreviewLabel(self, 2)
        self.areaPreview.show()

        self.toolkit = Toolkit(self)

        self.show()

    def start(self, newShot: QPixmap) -> None:
        self.screenshot = newShot
        self.setFixedSize(newShot.size())

        self.selection = QRect(0, 0, 0, 0)
        self.hideToolkit()

        self.areaPreview.start(newShot)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.moveSelectionArea(event.pos())
        self.hideToolkit()
        QToolTip.showText(event.pos(),
                          f"{abs(self.selection.width())}x{abs(self.selection.height())}"
                          )
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.selection.setCoords(
            self.selection.x(), self.selection.y(),
            event.x(), event.y()
        )
        self.areaPreview.setArea(self.selection)
        QToolTip.showText(event.pos(),
                          f"{abs(self.selection.width())}x{abs(self.selection.height())}"
                          )
        # self.toolTip
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.showToolkit()
        event.accept()

    def moveSelectionArea(self, moveTo: QPoint):
        self.selection.moveTo(moveTo)
        self.areaPreview.setArea(self.selection)

    def showToolkit(self):
        # TODO: adjust to screen corners
        self.toolkit.move(self.selection.x(), self.selection.y()-35)
        self.toolkit.show()

    def hideToolkit(self):
        self.toolkit.hide()
