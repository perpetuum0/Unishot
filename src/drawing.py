from PySide6.QtWidgets import QWidget, QLabel, QTextEdit
from PySide6.QtCore import Qt, QRect, QLineF, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPixmap, QPainterPath, QPen, QColor, QWheelEvent

from utils import mapPointToRect, expandRect
from typings import DrawTools, Drawing


class DrawTextEdit(QTextEdit):
    lostFocus = Signal()

    def __init__(self, parent: QWidget, color=QColor("red"), fontSize=12):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: rgba(0,0,0,0); border: 1px dotted white; padding: 0px")
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTextColor(color)
        self.setFontPointSize(fontSize)

    def upFontSize(self):
        if self.fontPointSize() < 96:
            self.setFontSize(self.fontPointSize()+2)

    def downFontSize(self):
        if self.fontPointSize() > 8:
            self.setFontSize(self.fontPointSize()-2)

    def setFontSize(self, size: float):
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

    active: bool
    tool: Tools
    penWidth: int
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

    def start(self, tool: Tools):
        self.tool = tool
        self.active = True
        self.brushPoints = []

        self.textEdit.hide()
        self.setTransparent(False)

    def stop(self):
        self.active = False
        self.stopTextEdit()
        self.setTransparent(True)

    def setCanvas(self, rect: QRect):
        self.penWidth = 5
        self.color = QColor("red")
        self.drawings = []

        self.setGeometry(rect)
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
        elif len(self.drawings) > 0:
            self.drawings.pop()

        # Append for any tool except Text, and if text check for input length
        if (self.tool is not self.Tools.Text) or (len(self.textEdit.toPlainText()) > 0):
            self.drawings.append(self.getDrawing())

        self.updatePreview()

    def getDrawing(self) -> Drawing:
        margin = self.penWidth*2.5  # Prevent cropping drawings

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
                font = self.textEdit.font()
                font.setPointSize(self.textEdit.fontPointSize())
                painter.setFont(font)
                painter.drawText(localRect, self.textEdit.toPlainText())

        return Drawing(selectionRect, pixmap)

    def startTextEdit(self) -> None:
        self.editingText = True
        self.textEdit.lostFocus.connect(self.stopTextEdit)
        self.textEdit.setGeometry(
            expandRect(
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
        self.doDrawing()

    def setPenWidth(self, width: int) -> None:
        self.penWidth = width
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
            self.drawings.pop()
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

    def setTransparent(self, transparent: bool):
        self.setAttribute(self.attribute, on=transparent)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.active:
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

    def keyPressEvent(self, event) -> None:
        # Stop text editing on hitting ESC
        if event.key() == 16777216 and self.editingText:
            self.stopTextEdit()
            event.accept()
        else:
            event.ignore()
