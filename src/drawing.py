from PySide6.QtWidgets import QWidget, QLabel, QTextEdit
from PySide6.QtCore import Qt, QRect, QLineF, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPixmap, QPainterPath, QPen, QColor, QWheelEvent, QTransform

import utils
from typings import DrawTools, Drawing


class PostEffects():
    class Flip:
        x: int = 1
        y: int = 1

    __angle: int
    __flip: Flip

    def __init__(self, angle=0, flip=Flip()) -> None:
        self.__angle = angle
        self.__flip = flip

    def angle(self) -> int:
        return self.__angle

    def setAngle(self, angle: int) -> None:
        self.__angle = angle % 360

    def flip(self) -> Flip:
        return self.__flip

    def setFlip(self, flip: Flip) -> None:
        self.__flip = flip

    def toggleFlip(self, x=False, y=False) -> None:
        if x:
            self.__flip.x = -1 if self.__flip.x == 1 else 1
        if y:
            self.__flip.y = -1 if self.__flip.y == 1 else 1

    def clear(self) -> None:
        self.__angle = 0
        self.__flip.x = 1
        self.__flip.y = 1

    def apply(self, pixmap: QPixmap) -> QPixmap:
        return QPixmap(pixmap).transformed(
            QTransform()
            .scale(
                self.__flip.x,
                self.__flip.y
            )
            .rotate(self.__angle)
        )


class DrawTextEdit(QTextEdit):
    lostFocus = Signal()

    def __init__(self, parent: QWidget, fontSize=12) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: rgba(0,0,0,0); border: 1px dotted white; padding: 0px")
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFontPointSize(fontSize)

    def upFontSize(self) -> None:
        if self.fontPointSize() < 96:
            self.setFontSize(self.fontPointSize()+2)

    def downFontSize(self) -> None:
        if self.fontPointSize() > 8:
            self.setFontSize(self.fontPointSize()-2)

    def setFontSize(self, size: float) -> None:
        cur = self.textCursor()
        self.selectAll()
        self.setFontPointSize(size)
        self.setTextCursor(cur)

    def focusOutEvent(self, e) -> None:
        self.lostFocus.emit()
        e.accept()


class Draw(QLabel):
    Tools = DrawTools
    attribute = Qt.WidgetAttribute.WA_TransparentForMouseEvents

    textEdit: DrawTextEdit

    __active: bool
    tool: Tools
    color: QColor
    penWidth: int
    drawings: list[Drawing]
    preview: QPixmap

    undoHistory: list[Drawing]
    editingText: bool
    isDrawing: bool
    newDrawing: bool
    brushPath: QPainterPath

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.__active = False
        self.editingText = False
        self.newDrawing = False
        self.isDrawing = False
        self.textEdit = DrawTextEdit(self)
        self.textEdit.hide()
        self.color = QColor("red")  # default

        self.setCursor(Qt.CursorShape.UpArrowCursor)  # Debug
        self.setTransparent(True)

    def start(self, tool: Tools) -> None:
        self.tool = tool
        self.__active = True
        self.brushPoints = []

        self.textEdit.hide()
        self.setTransparent(False)

    def stop(self) -> None:
        self.__active = False
        self.stopTextEdit()
        self.setTransparent(True)

    def setCanvas(self, geometry: QRect) -> None:
        self.penWidth = 5
        self.drawings = []
        self.undoHistory = []

        self.screenOffset = geometry.topLeft()
        self.resize(geometry.size())
        self.updatePreview()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.stopTextEdit()

        self.isDrawing = True
        self.newDrawing = True
        self.startPoint = utils.QDiff(event.globalPos(), self.screenOffset)
        self.brushPath = QPainterPath(self.startPoint)

        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.endPoint = utils.QDiff(event.globalPos(), self.screenOffset)
        self.toolAction()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.endPoint = utils.QDiff(event.globalPos(), self.screenOffset)
        self.toolAction()
        self.isDrawing = False
        event.accept()

    def toolAction(self) -> None:
        if self.tool is self.Tools.Brush:
            self.brushPath.lineTo(self.endPoint)
        if self.tool is self.Tools.Text:
            self.startTextEdit()
        else:
            self.doDrawing()

    def doDrawing(self) -> None:
        if self.newDrawing:
            self.newDrawing = False
        elif len(self.drawings) > 0:
            self.drawings.pop()

        # Append for any tool except Text, and if text check for input length
        if (self.tool is not self.Tools.Text) or (len(self.textEdit.toPlainText()) > 0):
            self.drawings.append(self.getDrawing())

        self.updatePreview()

    def getDrawing(self) -> Drawing:
        margin = self.penWidth*2.5  # Prevent cropping drawings

        selectionRect = utils.expandRect(
            QRect(self.startPoint, self.endPoint), margin
        ) if not self.tool is self.Tools.Brush else self.geometry()

        localStartPoint = utils.mapPointToRect(self.startPoint, selectionRect)
        localEndPoint = utils.mapPointToRect(self.endPoint, selectionRect)
        localRect = QRect(localStartPoint, localEndPoint).normalized()

        pixmap = QPixmap(selectionRect.size())
        pixmap.fill("transparent")

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(self.color)
        pen.setWidth(self.penWidth)
        painter.setPen(pen)

        match self.tool:
            case self.Tools.Brush:
                painter.drawPath(self.brushPath)
            case self.Tools.Square:
                painter.drawRect(localRect)
            case self.Tools.Ellipse:
                painter.drawEllipse(localRect)
            case self.Tools.Arrow:
                line = QLineF(localStartPoint, localEndPoint)
                line.setLength(line.length()-self.penWidth)
                painter.drawLine(line)

                arrowLine = QLineF(localEndPoint, localStartPoint)
                arrowLine.setLength(self.penWidth*2.25)
                ang = arrowLine.angle()

                arrowLine.setAngle(ang-45)
                painter.drawLine(arrowLine)
                arrowLine.setAngle(ang+45)
                painter.drawLine(arrowLine)
            case self.Tools.Line:
                painter.drawLine(localStartPoint, localEndPoint)
            case self.Tools.Text:
                font = self.textEdit.font()
                font.setPointSize(self.textEdit.fontPointSize())
                painter.setFont(font)
                painter.drawText(localRect, self.textEdit.toPlainText())

        return Drawing(selectionRect, pixmap)

    def startTextEdit(self) -> None:
        self.editingText = True
        self.textEdit.lostFocus.connect(self.stopTextEdit)
        self.textEdit.setGeometry(
            utils.expandRect(
                QRect(self.startPoint,
                      self.endPoint), 5  # 5 is default QTextEdit padding
            )
        )
        self.textEdit.show()
        self.textEdit.setFocus()

    def stopTextEdit(self) -> None:
        if self.editingText:
            self.editingText = False
            self.textEdit.lostFocus.disconnect()
            self.doDrawing()

            self.textEdit.hide()
            self.textEdit.clear()
            self.parent().setFocus()

    def setColor(self, color: QColor) -> None:
        self.color = color
        self.textEdit.setTextColor(color)

    def setPenWidth(self, width: int) -> None:
        self.penWidth = width
        if self.isDrawing:
            self.doDrawing()

    def upPenWidth(self, multiplier=1) -> int:
        if self.penWidth < 50:
            self.setPenWidth(self.penWidth + 2*multiplier)
        return self.penWidth

    def downPenWidth(self, multiplier=1) -> int:
        if self.penWidth >= 2:
            self.setPenWidth(self.penWidth - 2*multiplier)
        return self.penWidth

    def undo(self) -> None:
        try:
            self.undoHistory.append(self.drawings.pop())
            self.updatePreview()
        except IndexError:
            pass  # TODO: Play warning Windows sound

    def redo(self) -> None:
        try:
            self.drawings.append(self.undoHistory.pop())
            self.updatePreview()
        except IndexError:
            pass  # TODO: Play warning Windows sound

    def updatePreview(self) -> None:
        self.preview = self.drawPixmap()
        self.setPixmap(self.preview)

    def drawPixmap(self) -> QPixmap:
        pixmap = QPixmap(self.size())
        pixmap.fill("transparent")
        painter = QPainter(pixmap)

        for p, dr in self.drawings:
            painter.drawPixmap(p, dr)
        painter.end()

        return pixmap

    def setTransparent(self, transparent: bool) -> None:
        self.setAttribute(self.attribute, on=transparent)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.__active:
            delta = event.angleDelta().y()
            if delta > 0:
                if self.editingText:
                    self.textEdit.upFontSize()
                else:
                    self.upPenWidth()
            elif delta < 0:
                if self.editingText:
                    self.textEdit.downFontSize()
                else:
                    self.downPenWidth()
            event.accept()
        else:
            event.ignore()

    def active(self) -> bool:
        return self.__active

    def keyPressEvent(self, event) -> None:
        # Stop text editing on hitting ESC
        if event.key() == Qt.Key.Key_Escape and self.editingText:
            self.stopTextEdit()
            event.accept()
        else:
            event.ignore()
