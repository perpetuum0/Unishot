from PySide6.QtWidgets import QWidget, QLabel, QGraphicsBlurEffect, QAbstractButton
from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import QSize


class Toolkit(QWidget):
    def __init__(self, parent: QWidget) -> None:
        ###
        # For debug purposes:
        # super().__init__()
        # self.show()
        ###
        super().__init__(parent)

        self.setFixedSize(QSize(300, 25))

        self.backgroundLabel = ToolkitBackground(self, self.size())

        self.saveButton = ToolkitButton(self, QPixmap(
            "../images/saveIcon.png"), QSize(self.height(), self.height()))
        # self.saveButton.clicked.connect() #TODO


class ToolkitButton(QAbstractButton):

    def __init__(self, parent: QWidget, icon: QPixmap, size: QSize):
        super().__init__(parent)
        self.resize(size)

        self.icon = icon

        self.background = QPixmap(size)
        self.background.fill(QColor("transparent"))
        self.backgroundHovered = QPixmap(size)
        self.backgroundHovered.fill(QColor(43, 117, 226, 100))
        self.backgroundPressed = QPixmap(size)
        self.backgroundPressed.fill(QColor(43, 117, 226, 180))

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        bg: QPixmap
        if (self.isDown()):
            bg = self.backgroundPressed
        elif (self.underMouse()):
            bg = self.backgroundHovered
        else:
            bg = self.background

        # TODO: make icons smaller than the button itself
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), bg)
        painter.drawPixmap(event.rect(), self.icon)
        painter.end()

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()


class ToolkitBackground(QLabel):
    def __init__(self, parent: QWidget, size: QSize) -> None:
        super().__init__(parent)

        self.setFixedSize(size)

        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 190)")

        blur = QGraphicsBlurEffect(self)
        self.setGraphicsEffect(blur)
