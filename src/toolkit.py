from PySide6.QtWidgets import QWidget, QLabel, QGraphicsBlurEffect, QHBoxLayout, QVBoxLayout, QPushButton
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtCore import QSize, Signal

from typings import ToolkitButtons, ToolkitOrientation, DrawTools


class ToolkitBackground(QLabel):
    def __init__(self, parent: QWidget, size: QSize) -> None:
        super().__init__(parent)

        self.setFixedSize(size)

        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 235)")

        blur = QGraphicsBlurEffect(self)
        self.setGraphicsEffect(blur)


class ToolkitButton(QPushButton):
    buttonType: ToolkitButtons
    clickedT = Signal(ToolkitButtons, QPushButton)

    def __init__(self, parent: QWidget, buttonType: ToolkitButtons, size: QSize = None):
        super().__init__(parent)
        self.buttonType = buttonType

        iconSize = QSize(
            size.height() - 10, size.height() - 10
        )

        self.setFlat(True)
        self.setIconSize(iconSize)
        self.setFixedSize(size)

        label, icon = None, None
        match buttonType:
            # TODO: load resources from .qrc file
            case ToolkitButtons.Save:
                label = "Save to..."
                icon = QPixmap("../images/saveIcon.png")
            case ToolkitButtons.Copy:
                label = "Copy to Clipboard"
                icon = QPixmap("../images/copy.png")
            case ToolkitButtons.Close:
                label = "Close"
                icon = QPixmap("../images/close.png")
            case ToolkitButtons.DrawPencil |\
                    ToolkitButtons.DrawLine |\
                    ToolkitButtons.DrawArrow |\
                    ToolkitButtons.DrawSquare |\
                    ToolkitButtons.DrawEllipse:
                self.setCheckable(True)
                label = buttonType.value.value
                icon = QPixmap("../images/close.png")

        self.setToolTip(label)
        self.setIcon(icon)
        self.clicked.connect(lambda: self.clickedT.emit(buttonType, self))


class Toolkit(QWidget):
    Button = ToolkitButtons
    Orientation = ToolkitOrientation
    action = Signal(Button)

    buttons: list[ToolkitButton]
    selectedTool: ToolkitButton = None

    def __init__(self, parent: QWidget, buttons: list[Button], orientation: Orientation) -> None:
        super().__init__(parent)
        if orientation == orientation.Horizontal:
            self.setFixedSize(QSize(300, 30))
            buttonSize = QSize(self.height(), self.height())

            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        else:
            self.setFixedSize(QSize(30, 200))
            buttonSize = QSize(self.width(), self.width())

            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.setContentsMargins(0, 0, 0, 0)

        self.backgroundLabel = ToolkitBackground(self, self.size())

        self.buttons = []
        for btnType in buttons:
            btn = ToolkitButton(self, btnType, buttonSize)
            btn.clickedT.connect(self.buttonClicked)
            layout.addWidget(btn)
            self.buttons.append(btn)

    def buttonClicked(self, buttonType: Button, button: ToolkitButton = None) -> None:
        if self.selectedTool == button:
            # Double clicking tool stops drawing
            self.clearTool()
        else:
            # If button is tool
            if type(buttonType.value) is DrawTools:
                if self.selectedTool:
                    self.selectedTool.setChecked(False)
                self.selectedTool = button

            self.action.emit(buttonType)

    def keyPressEvent(self, event) -> None:
        # Hide on hitting ESC
        if event.key() == 16777216 and \
                self.selectedTool and \
                self.selectedTool.buttonType is not self.Button.Cursor:
            self.clearTool()
            event.accept()
        else:
            event.ignore()

    def hideEvent(self, event) -> None:
        self.clearTool()

    def clearTool(self) -> None:
        if self.selectedTool:
            self.selectedTool.setChecked(False)
            self.selectedTool = None
        # TODO: Make cursor checked...
        self.action.emit(self.Button.Cursor)
