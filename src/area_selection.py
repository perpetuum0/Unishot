from PySide6.QtWidgets import QWidget, QLabel, QToolTip
from PySide6.QtGui import QPixmap, QMouseEvent, Qt, QCursor, QTransform
from PySide6.QtCore import QRect, QPoint, QPointF, Signal

import utils
from typings import ResizePointAlignment, PostEffects


class SelectionPreview(QLabel):
    moveStart = Signal()
    moved = Signal(QPoint)
    moveEnd = Signal()

    screenshot: QPixmap
    effects: PostEffects
    borderWidth: int
    dragPoint: QPointF

    def __init__(self, parent: QWidget, borderWidth: int) -> None:
        super().__init__(parent)
        self.parent = parent
        self.borderWidth = borderWidth
        self.effects = PostEffects()

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
            self.postprocess(self.screenshot.copy(areaNormalized))
        )

        # Do preview post processing here...
        # TODO update here

    def setEffects(self, newEffects: PostEffects):
        self.effects = newEffects
        self.move(
            self.pos().x()+self.borderWidth,
            self.pos().y()
        )
        self.setSelection(self.geometry())

    def postprocess(self, pixmap: QPixmap) -> QPixmap:
        pixmap = QPixmap(pixmap).transformed(
            QTransform().scale(
                self.effects.flip.x,
                self.effects.flip.y
            )
        )
        return pixmap

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
    screenOffset: QPoint
    borderWidth: int = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.selection = QRect(0, 0, 0, 0)
        self.screenOffset = QPoint(0, 0)
        self.borderWidth = 2

        self.setCursor(Qt.CursorShape.CrossCursor)

        self.selectionPreview = SelectionPreview(self, self.borderWidth)
        self.selectionPreview.show()

        self.selectionPreview.moveStart.connect(self.startTransform)
        self.selectionPreview.moved.connect(self.moveSelection)
        self.selectionPreview.moveEnd.connect(self.endTransform)

        self.resizePoints = []
        for alignment in ResizePointAlignment:
            point = SelectionResizePoint(
                self, self.selectionPreview, alignment)
            self.resizePoints.append(point)

            point.dragStart.connect(self.startTransform)
            point.dragEnd.connect(self.endTransform)
            point.drag.connect(
                lambda tup: self.resizeSelection(tup[0], tup[1])
            )

    def start(self, newShot: QPixmap, offset: QPoint) -> None:
        self.screenOffset = offset
        self.setFixedSize(newShot.size())
        self.hideResizePoints()
        self.selectionPreview.start(newShot)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.startTransform()
        self.setSelection(QRect(0, 0, 0, 0))
        self.selection.moveTo(event.pos())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # TODO fix bug
        self.setSelection(
            QRect(
                QPoint(self.selection.x(), self.selection.y()),
                QPoint(event.x(), event.y())
            )
        )
        self.showTooltip()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.endTransform()
        event.accept()

    def setSelection(self, newSelection: QRect) -> None:
        self.startTransform()
        self.selection = newSelection
        self.selectionChanged()
        self.endTransform()

    def moveSelection(self, moveTo: QPoint) -> None:
        # TODO this can be done better in future
        moveTo = utils.QDiff(moveTo, self.screenOffset)
        prevPos = self.selection.topLeft()

        self.selection.moveTo(moveTo)

        newPoints = [self.selection.topLeft(), self.selection.topRight(),
                     self.selection.bottomLeft(), self.selection.bottomRight()]

        for p in newPoints:
            p = utils.QSum(p, self.screenOffset)
            if not utils.isPointOnScreen(p):
                self.selection.moveTo(prevPos)

        self.selectionChanged()

    def resizeSelection(self, alignment: ResizePointAlignment, point: QPoint) -> None:
        point = utils.QDiff(point, self.screenOffset)
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

    def startTransform(self) -> None:
        self.selection = self.selection.normalized()
        self.transformStart.emit()

    def endTransform(self) -> None:
        self.selection = self.selection.normalized()
        self.transformEnd.emit(self.selection)
