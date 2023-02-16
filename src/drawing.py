from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QRect, QPoint, QLineF
from PySide6.QtGui import QMouseEvent, QPainter, QPixmap, QPainterPath, QPen, QShortcut, QKeySequence

from utils import mapPointToRect
from typings import DrawTools, Drawing


class Draw(QLabel):
    Tools = DrawTools
    attribute = Qt.WidgetAttribute.WA_TransparentForMouseEvents

    tool: Tools
    preview: QPixmap
    drawings: list[Drawing]

    newDrawing: bool
    brushPath: QPainterPath

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.undoShortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        self.undoShortcut.activated.connect(self.undo)
        self.setCursor(Qt.CursorShape.UpArrowCursor)  # Debug
        self.setTransparent(True)

    def start(self, tool: Tools, width: int = 5):
        self.setTransparent(False)
        self.tool = tool
        self.penWidth = width
        self.brushPoints = []

    def stop(self):
        self.setTransparent(True)

    def setCanvas(self, rect: QRect):
        self.drawings = []
        self.setGeometry(rect)
        self.updatePreview()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.startPoint = event.globalPos()
        self.brushPath = QPainterPath(self.startPoint)
        self.newDrawing = True
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.endPoint = event.globalPos()
        self.doDrawing()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.endPoint = event.globalPos()
        self.doDrawing()
        event.accept()

    def doDrawing(self) -> None:
        if self.tool is self.Tools.Brush:
            self.brushPath.lineTo(self.endPoint)

        if not self.newDrawing:
            self.drawings.pop()
        else:
            self.newDrawing = False

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
        margin = self.penWidth  # Prevent cropping drawings
        tmp = QRect(self.startPoint, self.endPoint).normalized()
        selectionRect = QRect(
            QPoint(tmp.topLeft().x()-margin,
                   tmp.topLeft().y()-margin),
            QPoint(tmp.bottomRight().x()+margin,
                   tmp.bottomRight().y()+margin)
        ) if not self.tool is self.Tools.Brush \
            else self.geometry()

        localStartPoint = mapPointToRect(self.startPoint, selectionRect)
        localEndPoint = mapPointToRect(self.endPoint, selectionRect)
        localRect = QRect(localStartPoint, localEndPoint).normalized()

        pixmap = QPixmap(selectionRect.size())
        pixmap.fill("transparent")

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen("red")
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
                painter.drawText(
                    localRect, "Hello, world! To be implemented."
                )

        return Drawing(selectionRect, pixmap)

    def undo(self) -> None:
        try:
            self.drawings.pop()
            self.updatePreview()
        except IndexError:
            pass  # Play warning Windows sound

    def updatePreview(self) -> None:
        self.preview = self.drawPixmap()
        self.setPixmap(self.preview)

    def setTransparent(self, transparent: bool):
        self.setAttribute(self.attribute, on=transparent)
