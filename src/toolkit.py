from PySide6.QtWidgets import QWidget, QLabel, QGraphicsBlurEffect, QHBoxLayout, QVBoxLayout, QPushButton, QColorDialog
from PySide6.QtGui import QPixmap, Qt, QColor, QMouseEvent
from PySide6.QtCore import QSize, Signal, QPoint, QEvent
from math import floor

from typings import ToolkitButtonTypes, ToolkitOrientation, DrawTools


class ToolkitBackground(QLabel):
    def __init__(self, parent: QWidget, size: QSize) -> None:
        super().__init__(parent)

        self.setFixedSize(size)

        blur = QGraphicsBlurEffect(self)
        self.setGraphicsEffect(blur)
        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 235);border:none")


class ToolkitColorMenu(QColorDialog):
    activated = Signal()
    deactivated = Signal()

    DEFAULT_COLOR = QColor(255, 0, 0, 255)
    __active: bool

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.__active = False
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

    def toggle(self, pos: QPoint) -> None:
        if self.__active:
            self.deactivate()
        else:
            self.alignTo(pos)
            self.activate()

    def alignTo(self, point: QPoint) -> None:
        pos = QPoint(
            point.x()-self.width()/2,
            point.y()-self.height()-9
        )

        self.move(pos)

    def active(self) -> bool:
        return self.__active

    def activate(self) -> None:
        self.__active = True
        self.show()
        self.activated.emit()

    def deactivate(self) -> None:
        self.__active = False
        self.hide()
        self.deactivated.emit()


class ToolkitButton(QPushButton):
    clickedT = Signal(QMouseEvent, QPushButton)

    __buttonType: ToolkitButtonTypes

    def __init__(self, parent: QWidget, buttonType: ToolkitButtonTypes, size: QSize = None) -> None:
        super().__init__(parent)
        self.__buttonType = buttonType

        self.setFlat(True)
        if size:
            iconSize = QSize(
                size.height() - 10, size.height() - 10
            )
            self.setIconSize(iconSize)
            self.setFixedSize(size)

        label, icon = None, None
        match buttonType:
            case ToolkitButtonTypes.Save:
                label = "Save to..."
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtonTypes.Copy:
                label = "Copy to Clipboard"
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtonTypes.Close:
                label = "Close"
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtonTypes.Color:
                label = "Tool color"
                icon = self.getColorIcon(
                    ToolkitColorMenu.DEFAULT_COLOR
                )
                self.setCheckable(True)
            case ToolkitButtonTypes.Cursor:
                label = "Cursor"
                icon = QPixmap(":/icons/"+buttonType.value)
                self.setCheckable(True)
            case ToolkitButtonTypes.FlipVer:
                label = "Flip vertically"
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtonTypes.FlipHor:
                label = "Flip horizontally"
                icon = QPixmap(":/icons/"+buttonType.value)
            case ToolkitButtonTypes.RotateRight | ToolkitButtonTypes.RotateLeft:
                raise NotImplementedError
            case DrawTools:
                self.setCheckable(True)
                drawTool = buttonType.value
                label = drawTool.name
                icon = QPixmap(":/icons/"+drawTool.value)

        self.setToolTip(label)
        self.setIcon(icon)
        self.installEventFilter(self)

    def eventFilter(self, obj, event: QEvent) -> None:
        if event.type() is QEvent.Type.MouseButtonRelease:
            self.click()
            self.clickedT.emit(event, self)
            return True
        return super().eventFilter(obj, event)

    def getColorIcon(self, color: QColor) -> QPixmap:
        size = self.size().height()/1.75
        icon = QPixmap(QSize(floor(size), floor(size)))
        icon.fill(color)
        return icon

    def setColorIcon(self, color: QColor) -> None:
        self.setIcon(self.getColorIcon(color))

    def buttonType(self) -> ToolkitButtonTypes:
        return self.__buttonType


class Toolkit(QWidget):
    ButtonTypes = ToolkitButtonTypes
    Orientation = ToolkitOrientation
    action = Signal(ButtonTypes, ToolkitButton)
    moved = Signal(QPoint)

    buttons: list[ToolkitButton]
    groups: list[QWidget]
    cursorButton: ToolkitButton
    selectedTool: ToolkitButton

    def __init__(self, parent: QWidget, buttons: list[ButtonTypes | list[ButtonTypes]], orientation: Orientation) -> None:
        super().__init__(parent)
        self.selectedTool = None
        self.cursorButton = None
        self.buttons = []
        self.groups = []

        if orientation == orientation.Horizontal:
            self.setFixedHeight(30)
            self.setMinimumWidth(100)
            buttonSize = QSize(self.height(), self.height())

            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        else:
            self.setFixedWidth(30)
            self.setMinimumHeight(100)
            buttonSize = QSize(self.width(), self.width())

            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        for btnType in buttons:
            if type(btnType) is list:
                # Initialize group
                group = ToolkitGroup(parent, self, btnType)
                group.activated.connect(lambda gr: self.hideGroups([gr]))
                group.buttonClicked.connect(self.buttonClicked)
                layout.addWidget(group.mainButton)
                self.groups.append(group)
            else:
                # Init regular button
                btn = ToolkitButton(self, btnType, buttonSize)
                btn.clickedT.connect(self.buttonClicked)
                if btnType is self.ButtonTypes.Cursor:
                    self.cursorButton = btn
                    self.cursorButton.setChecked(True)
                layout.addWidget(btn)
                self.buttons.append(btn)
        self.adjustSize()

        self.background = ToolkitBackground(self, self.size())
        self.background.lower()

    def buttonClicked(self, event: QMouseEvent, button: ToolkitButton = None) -> None:
        buttonType = button.buttonType()
        # Double clicking tool also stops drawing
        if (buttonType is self.ButtonTypes.Cursor) or (self.selectedTool == button):
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

    def hideEvent(self, ev) -> None:
        # Uncheck all buttons
        for btn in self.buttons:
            if btn.isCheckable():
                btn.setChecked(False)
        self.hideGroups()
        self.clearTool()

    def hideGroups(self, exclude: list[QWidget] = []) -> None:
        for gr in self.groups:
            if not gr in exclude:
                gr.deactivate()

    def clearTool(self) -> None:
        if self.selectedTool:
            self.selectedTool.setChecked(False)
            self.selectedTool = None
        if self.cursorButton:
            self.cursorButton.setChecked(True)
            self.action.emit(self.ButtonTypes.Cursor, self.cursorButton)


class ToolkitGroup(QWidget):
    class ExpandButton(QPushButton):
        def __init__(self, parent: QWidget):
            super().__init__(parent)
            self.setIcon(QPixmap(":/icons/expand"))
            self.setIconSize(QSize(10, 10))
            self.setFixedSize(QSize(13, 13))
            self.setStyleSheet("""
            QPushButton {
                border-radius:5px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,185);
            }
            QPushButton:pressed {
                background-color: rgba(255,255,255,245);
            }
            """)

    ButtonTypes = ToolkitButtonTypes
    activated = Signal(QWidget)
    buttonClicked = Signal(QMouseEvent, ToolkitButton)

    buttons: list[ToolkitButtonTypes]
    mainButton: ToolkitButton
    __active: bool

    def __init__(self, parent: QWidget, parentToolkit: Toolkit, buttons: list[ButtonTypes]):
        super().__init__(parent)
        self.toolkit = parentToolkit
        self.__active = False
        self.buttons = []
        self.mainButton = None

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setDirection(QVBoxLayout.Direction.BottomToTop)

        for btnType in reversed(buttons):
            if btnType is self.ButtonTypes.Cursor:
                buttons.remove(btnType)
                print("ToolkitButtonType.Cursor is not supported in groups.")
                continue
            btn = ToolkitButton(self, btnType, QSize(30, 30))
            btn.clickedT.connect(self.buttonClickEvent)

            layout.addWidget(btn)
            self.buttons.append(btn)

        if len(self.buttons) <= 1:
            raise Exception("Group is empty or consists of only 1 button.")

        self.mainButton = self.buttons[-1]
        layout.removeWidget(self.mainButton)

        self.adjustSize()
        self.background = ToolkitBackground(self, self.size())
        self.background.lower()

        self.expandButton = self.ExpandButton(self)
        self.expandButton.clicked.connect(self.toggle)
        self.alignExpandButton()

    def setMainButton(self, button: ToolkitButton):
        layout = self.layout()
        toolkitLayout = self.toolkit.layout()
        index = toolkitLayout.indexOf(self.mainButton)

        layout.replaceWidget(button, self.mainButton)
        toolkitLayout.insertWidget(index, button)

        self.setLayout(layout)
        self.toolkit.setLayout(toolkitLayout)

        self.mainButton = button
        self.alignExpandButton()

    def align(self) -> None:
        # TODO: align properly on vertical Toolkit
        pos = self.toolkit.mapTo(self.parent(), self.mainButton.pos())
        self.move(QPoint(
            pos.x(),
            self.toolkit.y()-self.height()
        ))

    def alignExpandButton(self):
        expandPos = self.mainButton.rect().topRight()
        self.expandButton.setParent(self.mainButton)
        self.expandButton.move(
            expandPos.x()-self.expandButton.width()+1,
            expandPos.y()
        )

    def buttonClickEvent(self, event: QMouseEvent, button: ToolkitButton):
        buttonType = button.buttonType()
        if event.button() is Qt.MouseButton.RightButton and button == self.mainButton:
            self.toggle()
            button.toggle()
        else:
            if self.mainButton != button:
                if type(buttonType.value) is DrawTools:
                    self.setMainButton(button)
                self.deactivate()
            self.buttonClicked.emit(event, button)

    def active(self) -> bool:
        return self.__active

    def activate(self) -> None:
        self.__active = True
        self.activated.emit(self)
        self.align()
        self.show()

    def deactivate(self) -> None:
        self.__active = False
        self.hide()

    def toggle(self) -> None:
        if self.__active:
            self.deactivate()
        else:
            self.activate()
