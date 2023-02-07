from PySide6.QtWidgets import QWidget, QLabel, QToolTip
from PySide6.QtGui import QPixmap, QMouseEvent, Qt, QCursor
from PySide6.QtCore import QRect, QPoint, QPointF, Signal

from typings import ResizePointAlignment
from utils import isPointOnScreen


class SelectionPreview(QLabel):
    moveStart = Signal()
    moved = Signal(QPoint)
    moveEnd = Signal()

    screenshot: QPixmap
    borderWidth: int
    dragPoint: QPointF

    def __init__(self, parent: QWidget, borderWidth: int) -> None:
        super().__init__(parent)
        self.parent = parent
        self.borderWidth = borderWidth

        self.setStyleSheet(
            f"border: {borderWidth}px dashed white")
        self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))

    def start(self, screenshot) -> None:
        self.screenshot = screenshot
        self.setSelection(QRect(0, 0, 0, 0))

    def setSelection(self, newSelection: QRect) -> None:
        areaNormalized = newSelection.normalized()

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
        self.moveStart.emit()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.moved.emit(QPoint(
            event.globalPos().x()-self.dragPoint.x(),
            event.globalPos().y()-self.dragPoint.y()
        ))

        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.moveEnd.emit()
        event.accept()


class SelectionResizePoint(QLabel):
    dragStart = Signal()
    drag = Signal(tuple)
    dragEnd = Signal()
    alignment: ResizePointAlignment
    borderWidth: int

    def __init__(self, parent: QWidget, alignWith: QWidget, alignment: ResizePointAlignment):
        super().__init__(parent)
        self.alignment = alignment
        self.alignObj = alignWith
        self.offset = 3

        self.setFixedSize(8, 8)
        self.setStyleSheet("background-color: white")

        match alignment:
            case ResizePointAlignment.TopLeft | ResizePointAlignment.BottomRight:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)

            case ResizePointAlignment.Top | ResizePointAlignment.Bottom:
                self.setCursor(Qt.CursorShape.SizeVerCursor)

            case ResizePointAlignment.BottomLeft | ResizePointAlignment.TopRight:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)

            case ResizePointAlignment.CenterLeft | ResizePointAlignment.CenterRight:
                self.setCursor(Qt.CursorShape.SizeHorCursor)

    def align(self) -> None:
        frame = self.alignObj.geometry()
        center = frame.center()

        geom = self.geometry()
        match self.alignment:
            case ResizePointAlignment.TopLeft:
                p = frame.topLeft()
                geom.moveCenter(
                    QPoint(p.x()-self.offset, p.y()-self.offset)
                )

            case ResizePointAlignment.Top:
                p = frame.topLeft()
                geom.moveCenter(
                    QPoint(center.x(), p.y()-self.offset)
                )

            case ResizePointAlignment.TopRight:
                p = frame.topRight()
                geom.moveCenter(
                    QPoint(p.x()+self.offset, p.y()-self.offset)
                )

            case ResizePointAlignment.CenterLeft:
                p = frame.topLeft()
                geom.moveCenter(
                    QPoint(p.x()-self.offset, center.y())
                )

            case ResizePointAlignment.CenterRight:
                p = frame.topRight()
                geom.moveCenter(
                    QPoint(p.x()+self.offset, center.y())
                )

            case ResizePointAlignment.BottomLeft:
                p = frame.bottomLeft()
                geom.moveCenter(
                    QPoint(p.x()-self.offset, p.y()+self.offset)
                )

            case ResizePointAlignment.Bottom:
                p = frame.bottomLeft()
                geom.moveCenter(
                    QPoint(center.x(), p.y()+self.offset)
                )

            case ResizePointAlignment.BottomRight:
                p = frame.bottomRight()
                geom.moveCenter(
                    QPoint(p.x()+self.offset, p.y()+self.offset)
                )
        self.setGeometry(geom)

    def mousePressEvent(self, event) -> None:
        self.dragStart.emit()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.drag.emit((self.alignment, event.globalPos()))
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self.dragEnd.emit()
        event.accept()


class AreaSelection(QWidget):
    transformStart = Signal()
    transformEnd = Signal(QRect)

    resizePoints: list[SelectionResizePoint]
    selectionPreview: SelectionPreview
    selection: QRect
    borderWidth: int = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.selection = QRect(0, 0, 0, 0)
        self.borderWidth = 2

        self.setCursor(Qt.CursorShape.CrossCursor)

        self.selectionPreview = SelectionPreview(self, self.borderWidth)
        self.selectionPreview.show()

        self.selectionPreview.moveStart.connect(self.startTransorm)
        self.selectionPreview.moved.connect(self.moveSelection)
        self.selectionPreview.moveEnd.connect(self.endTransform)

        self.resizePoints = []
        for alignment in ResizePointAlignment:
            point = SelectionResizePoint(
                self, self.selectionPreview, alignment)
            self.resizePoints.append(point)

            point.dragStart.connect(self.startTransorm)
            point.dragEnd.connect(self.endTransform)
            point.drag.connect(
                lambda tup: self.resizeSelection(tup[0], tup[1])
            )

    def start(self, newShot: QPixmap) -> None:
        self.setFixedSize(newShot.size())
        self.hideResizePoints()
        self.selectionPreview.start(newShot)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.startTransorm()
        self.setSelection(0, 0, 0, 0)
        self.moveSelection(event.pos())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.setSelection(
            self.selection.x(), self.selection.y(),
            event.x(), event.y()
        )
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.endTransform()
        event.accept()

    def setSelection(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.selection.setCoords(x1, y1, x2, y2)
        self.showTooltip()
        self.selectionChanged()

    def moveSelection(self, moveTo: QPoint) -> None:
        # TODO this can be done better in future
        prevPos = self.selection.topLeft()

        self.selection.moveTo(moveTo)

        newPoints = [self.selection.topLeft(), self.selection.topRight(),
                     self.selection.bottomLeft(), self.selection.bottomRight()]

        for p in newPoints:
            if not isPointOnScreen(p):
                self.selection.moveTo(prevPos)

        self.selectionChanged()

    def resizeSelection(self, alignment: ResizePointAlignment, point: QPoint) -> None:
        match alignment:
            case ResizePointAlignment.TopLeft:
                self.selection.setTopLeft(point)

            case ResizePointAlignment.Top:
                self.selection.setTop(point.y())

            case ResizePointAlignment.TopRight:
                self.selection.setTopRight(point)

            case ResizePointAlignment.CenterLeft:
                self.selection.setLeft(point.x())

            case ResizePointAlignment.CenterRight:
                self.selection.setRight(point.x())

            case ResizePointAlignment.BottomLeft:
                self.selection.setBottomLeft(point)

            case ResizePointAlignment.Bottom:
                self.selection.setBottom(point.y())

            case ResizePointAlignment.BottomRight:
                self.selection.setBottomRight(point)
        self.showTooltip()
        self.selectionChanged()

    def selectionChanged(self) -> None:
        # Call this method after any change of self.selection
        self.selectionPreview.setSelection(self.selection)
        self.alignResizePoints()
        self.showResizePoints()

    def alignResizePoints(self) -> None:
        for point in self.resizePoints:
            point.show()
            point.align()

    def showResizePoints(self) -> None:
        for point in self.resizePoints:
            point.show()

    def hideResizePoints(self) -> None:
        for point in self.resizePoints:
            point.hide()

    def showTooltip(self) -> None:
        QToolTip.showText(
            QCursor.pos(),
            f"{abs(self.selection.width())}x{abs(self.selection.height())}"
        )

    def startTransorm(self) -> None:
        self.selection = self.selection.normalized()
        self.transformStart.emit()

    def endTransform(self) -> None:
        self.selection = self.selection.normalized()
        self.transformEnd.emit(self.selection)
