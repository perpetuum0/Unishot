from PySide6.QtWidgets import QWidget, QLabel, QGraphicsBlurEffect, QHBoxLayout, QVBoxLayout, QPushButton, QColorDialog, QLineEdit
from PySide6.QtGui import QPixmap, Qt, QColor
from PySide6.QtCore import QSize, Signal, QPoint
from math import floor

from typings import ToolkitButtons, ToolkitOrientation, DrawTools


class ToolkitBackground(QLabel):
    def __init__(self, parent: QWidget, size: QSize) -> None:
        super().__init__(parent)

        self.setFixedSize(size)

        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 235)")
        blur = QGraphicsBlurEffect(self)
        self.setGraphicsEffect(blur)


class ToolkitColorMenu(QColorDialog):
    DEFAULT_COLOR = QColor(255, 0, 0, 255)
    active: bool

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.active = False
        self.setWindowFlags(Qt.WindowType.Widget)

        children = self.children()
        for i, child in enumerate(children):
            if not (i in (0, 8, 9, 12)):
                child.hide()
        children[0].setSpacing(0)

        self.adjustSize()
        self.background = ToolkitBackground(self, self.size())
        self.background.lower()
        self.hide()

        self.setCurrentColor(self.DEFAULT_COLOR)

    def toggle(self, pos: QPoint):
        if self.active:
            self.active = False
            self.hide()
        else:
            self.active = True
            self.showAt(pos)

    def showAt(self, at: QPoint):
        self.alignTo(at)
        self.show()

    def alignTo(self, point: QPoint):
        pos = QPoint(
            point.x()-self.width()/2,
            point.y()-self.height()-10
        )

        self.move(pos)

    def deactivate(self):
        self.active = False
        self.hide()


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
            case ToolkitButtons.Save:
                label = "Save to..."
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtons.Copy:
                label = "Copy to Clipboard"
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtons.Close:
                label = "Close"
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtons.Color:
                label = "Tool color"
                icon = self.getColorIcon(
                    ToolkitColorMenu.DEFAULT_COLOR
                )
                self.setCheckable(True)
            case ToolkitButtons.Cursor:
                label = "Cursor"
                icon = QPixmap(":/icons/"+buttonType.value)
                self.setCheckable(True)
            case DrawTools:
                self.setCheckable(True)
                drawTool = buttonType.value
                label = drawTool.name
                icon = QPixmap(":/icons/"+drawTool.value)

        self.setToolTip(label)
        self.setIcon(icon)
        self.clicked.connect(lambda: self.clickedT.emit(buttonType, self))

    def getColorIcon(self, color: QColor):
        size = self.size().height()/1.75
        icon = QPixmap(QSize(floor(size), floor(size)))
        icon.fill(color)
        return icon

    def setColorIcon(self, color: QColor):
        self.setIcon(self.getColorIcon(color))


class Toolkit(QWidget):
    Button = ToolkitButtons
    Orientation = ToolkitOrientation
    action = Signal(Button, ToolkitButton)

    buttons: list[ToolkitButton]
    cursorButton: ToolkitButton = None
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

        self.background = ToolkitBackground(self, self.size())

        self.buttons = []
        for btnType in buttons:
            btn = ToolkitButton(self, btnType, buttonSize)
            btn.clickedT.connect(self.buttonClicked)
            layout.addWidget(btn)
            if btnType is self.Button.Cursor:
                self.cursorButton = btn
                self.cursorButton.setChecked(True)
            self.buttons.append(btn)

    def buttonClicked(self, buttonType: Button, button: ToolkitButton = None) -> None:
        # Double clicking tool also stops drawing
        if (buttonType is self.Button.Cursor) or (self.selectedTool == button):
            self.clearTool()
        else:
            # If button is tool
            if type(buttonType.value) is DrawTools:
                if self.cursorButton:
                    self.cursorButton.setChecked(False)
                if self.selectedTool:
                    self.selectedTool.setChecked(False)
                self.selectedTool = button

            self.action.emit(buttonType, button)

    def hideEvent(self, e) -> None:
        # Uncheck all buttons
        for btn in self.buttons:
            if btn.isCheckable():
                btn.setChecked(False)
        self.clearTool()

    def clearTool(self) -> None:
        if self.selectedTool:
            self.selectedTool.setChecked(False)
            self.selectedTool = None
        if self.cursorButton:
            self.cursorButton.setChecked(True)
        self.action.emit(self.Button.Cursor, self.cursorButton)
