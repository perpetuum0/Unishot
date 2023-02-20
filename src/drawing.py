from PySide6.QtWidgets import QWidget, QLabel, QTextEdit
from PySide6.QtCore import Qt, QRect, QPoint, QLineF, Signal, QSize
from PySide6.QtGui import QMouseEvent, QPainter, QPixmap, QPainterPath, QPen, QShortcut, QKeySequence, QColor

from utils import mapPointToRect, expandRect
from typings import DrawTools, Drawing


class DrawTextEdit(QTextEdit):
    lostFocus = Signal()

    def __init__(self, parent: QWidget, color=QColor("red")):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: rgba(0,0,0,0); border: 1px dotted white; padding: 0px")
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTextColor(color)

    def focusOutEvent(self, e) -> None:
        self.lostFocus.emit()
        e.accept()


class Draw(QLabel):
    Tools = DrawTools
    attribute = Qt.WidgetAttribute.WA_TransparentForMouseEvents

    active: bool
    tool: Tools
    color: QColor
    preview: QPixmap
    drawings: list[Drawing]
    textEdit: DrawTextEdit

    editingText: bool
    newDrawing: bool
    brushPath: QPainterPath

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.active = False
        self.editingText = False
        self.textEdit = DrawTextEdit(self)
        self.textEdit.hide()

        self.setCursor(Qt.CursorShape.UpArrowCursor)  # Debug
        self.setTransparent(True)

    def start(self, tool: Tools, color=QColor("red"), width: int = 5):
        self.active = True
        self.textEdit.hide()
        self.setTransparent(False)
        self.tool = tool
        self.color = color
        self.penWidth = width
        self.brushPoints = []

    def stop(self):
        self.active = False
        self.stopTextEdit()
        self.setTransparent(True)

    def setCanvas(self, rect: QRect):
        self.drawings = []
        self.setGeometry(rect)
        self.textEdit.resize(rect.size())
        self.updatePreview()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.stopTextEdit()

        self.newDrawing = True
        self.startPoint = event.globalPos()
        self.brushPath = QPainterPath(self.startPoint)

        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.endPoint = event.globalPos()
        self.toolAction()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.endPoint = event.globalPos()
        self.toolAction()
        event.accept()

    def toolAction(self):
        if self.tool is self.Tools.Brush:
            self.brushPath.lineTo(self.endPoint)
        if self.tool is self.Tools.Text:
            self.startTextEdit()
        else:
            self.doDrawing()

    def doDrawing(self) -> None:
        if self.newDrawing:
            self.newDrawing = False
        else:
            self.drawings.pop()

        # Append for any tool except Text, and if text check for input length
        if (self.tool is not self.Tools.Text) or (len(self.textEdit.toPlainText()) > 0):
            self.drawings.append(self.getDrawing())

        self.updatePreview()

    def drawPixmap(self) -> QPixmap:
        pixmap = QPixmap(self.size())
        pixmap.fill("transparent")
        painter = QPainter(pixmap)

        for p, dr in self.drawings:
            painter.drawPixmap(p, dr)
        painter.end()

        return pixmap

    def getDrawing(self) -> Drawing:
        margin = self.penWidth*2  # Prevent cropping drawings

        selectionRect = expandRect(
            QRect(self.startPoint, self.endPoint), margin
        ) if not self.tool is self.Tools.Brush else self.geometry()

        localStartPoint = mapPointToRect(self.startPoint, selectionRect)
        localEndPoint = mapPointToRect(self.endPoint, selectionRect)
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
                painter.drawText(localRect, self.textEdit.toPlainText())

        return Drawing(selectionRect, pixmap)

    def startTextEdit(self):
        self.editingText = True
        self.textEdit.lostFocus.connect(self.stopTextEdit)
        self.textEdit.setGeometry(
            expandRect(QRect(self.startPoint,
                             self.endPoint), 5)
        )
        self.textEdit.show()
        self.textEdit.setFocus()

    def stopTextEdit(self):
        if self.editingText:
            self.editingText = False
            self.textEdit.lostFocus.disconnect()
            self.doDrawing()

            self.textEdit.hide()
            self.textEdit.clear()
            self.parent().setFocus()

    def undo(self) -> None:
        try:
            self.drawings.pop()
            self.updatePreview()
        except IndexError:
            pass  # TODO: Play warning Windows sound

    def updatePreview(self) -> None:
        self.preview = self.drawPixmap()
        self.setPixmap(self.preview)

    def setTransparent(self, transparent: bool):
        self.setAttribute(self.attribute, on=transparent)

    def keyPressEvent(self, event) -> None:
        # Stop text editing on hitting ESC
        if event.key() == 16777216 and self.editingText:
            self.stopTextEdit()
            event.accept()
        else:
            event.ignore()
