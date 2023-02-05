from PySide6.QtWidgets import QWidget, QLabel, QGraphicsBlurEffect, QGridLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QPixmap, QColor, QPainter, Qt
from PySide6.QtCore import QSize, Signal

from typings import ToolkitButtons


class Toolkit(QWidget):
    action = Signal(ToolkitButtons)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setFixedSize(QSize(300, 30))

        self.backgroundLabel = ToolkitBackground(self, self.size())

        buttonSize = QSize(self.height(), self.height())

        self.saveButton = ToolkitButton(
            self, QPixmap("../images/saveIcon.png"), "Save to...", buttonSize)
        self.copyButton = ToolkitButton(
            self, QPixmap("../images/copy.png"), "Copy to Clipboard", buttonSize)

        self.saveButton.clicked.connect(
            lambda: self.action.emit(ToolkitButtons.Save)
        )
        self.copyButton.clicked.connect(
            lambda: self.action.emit(ToolkitButtons.Copy)
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.saveButton)
        layout.addWidget(self.copyButton)


class ToolkitButton(QPushButton):
    def __init__(self, parent: QWidget, icon: QPixmap, label="", size: QSize = None, iconSize: QSize = None):
        super().__init__(parent)
        size = parent.size() if not size else size
        iconSize = QSize(
            size.height()-10, size.height() - 10
        ) if not iconSize else iconSize

        self.setFlat(True)
        self.setToolTip(label)
        self.setIconSize(iconSize)
        self.setIcon(icon)
        self.setFixedSize(size)


class ToolkitBackground(QLabel):
    def __init__(self, parent: QWidget, size: QSize) -> None:
        super().__init__(parent)

        self.setFixedSize(size)

        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 235)")

        blur = QGraphicsBlurEffect(self)
        self.setGraphicsEffect(blur)
