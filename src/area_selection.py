from PySide6.QtWidgets import QWidget, QLabel, QToolTip, QApplication
from PySide6.QtGui import QPixmap, QMouseEvent, Qt, QCursor
from PySide6.QtCore import QRect, QPoint, QPointF, Signal, QLineF, QPointF, QRectF

import utils
from drawing import PostEffects
from typings import ResizePointAlignment


class SelectionPreview(QLabel):
    moveStart = Signal()
    moved = Signal(QPoint)
    moveEnd = Signal()

    screenshot: QPixmap
    selection: QRect
    effects: PostEffects
    borderWidth: int
    dragPoint: QPointF

    def __init__(self, parent: QWidget, borderWidth: int) -> None:
        super().__init__(parent)
        self.parent = parent
        self.borderWidth = borderWidth
        self.selection = QRect(0, 0, 0, 0)
        self.effects = PostEffects()

        self.setStyleSheet(
            f"border: {borderWidth}px dashed white")
        self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))

    def start(self, screenshot) -> None:
        self.screenshot = screenshot
        self.effects.clear()
        self.setSelection(QRect(0, 0, 0, 0))

    def setSelection(self, newSelection: QRect) -> None:
        self.selection = newSelection.normalized()

        self.setGeometry(self.selection)

        # Adjust to border width
        self.move(
            self.pos().x()-self.borderWidth,
            self.pos().y()
        )

        self.updatePreview()

    def setEffects(self, newEffects: PostEffects) -> None:
        self.effects = newEffects
        self.updatePreview()

    def updatePreview(self) -> None:
        self.setPixmap(
            self.effects.apply(self.screenshot.copy(self.selection))
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

    def __init__(self, parent: QWidget, alignWith: QWidget, alignment: ResizePointAlignment) -> None:
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
    transformEnd = Signal(QRectF)

    resizePoints: list[SelectionResizePoint]
    selectionPreview: SelectionPreview
    selection: QRectF
    screenOffset: QPoint
    borderWidth: int = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.selection = QRectF(0, 0, 0, 0)
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
        self.setSelection(QRectF(0, 0, 0, 0))
        self.selection.moveTo(event.pos())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        newSelection = QRectF()
        newSelection.setCoords(self.selection.x(), self.selection.y(),
                               event.x(), event.y())
        self.setSelection(
            newSelection
        )
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.endTransform()
        event.accept()

    def setSelection(self, newSelection: QRectF) -> None:
        self.showTooltip()
        self.selection = newSelection
        self.selectionChanged()

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
        modifiers = QApplication.keyboardModifiers()
        prevSel = QRectF(self.selection)

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            diag = QLineF()
            center = self.selection.center()
            match alignment.value:
                case "dx":
                    diag.setPoints(
                        self.selection.topLeft(),
                        self.selection.bottomRight()
                    )
                case "dy":
                    diag.setPoints(
                        self.selection.topRight(),
                        self.selection.bottomLeft()
                    )
                case "x":
                    diag.setPoints(
                        QPointF(self.selection.left(), center.y()),
                        QPointF(self.selection.right(), center.y())
                    )
                case "y":
                    diag.setPoints(
                        QPointF(center.x(), self.selection.top()),
                        QPointF(center.x(), self.selection.bottom())
                    )
            point = utils.closestPointToLine(point.toPointF(), diag)

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

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if alignment.value == "y":
                scale = self.selection.height() / prevSel.height()
                w = self.selection.width()
                diff = w*scale-w

                self.selection.setLeft(self.selection.left()-diff/2)
                self.selection.setRight(self.selection.right()+(diff/2))
            elif alignment.value == "x":
                scale = self.selection.width() / prevSel.width()
                h = self.selection.height()
                diff = h*scale-h

                self.selection.setTop(self.selection.top()-diff/2)
                self.selection.setBottom(self.selection.bottom()+(diff/2))

        self.selectionChanged()

    def selectionChanged(self) -> None:
        # Call this method after any change of self.selection
        self.selectionPreview.setSelection(self.selection.toRect())
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
            f"{round(abs(self.selection.width()))}x{round(abs(self.selection.height()))}"
        )

    def startTransform(self) -> None:
        self.selection = self.selection.normalized()
        self.transformStart.emit()

    def endTransform(self) -> None:
        self.selection = self.selection.normalized()
        self.transformEnd.emit(self.selection)
