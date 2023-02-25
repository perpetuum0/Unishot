from PySide6.QtWidgets import QWidget, QLabel, QApplication, QFileDialog
from PySide6.QtCore import (
    Qt, QPoint, QSize, QEvent, QRect, QStandardPaths)
from PySide6.QtGui import (QGuiApplication, QPixmap,
                           QPainter, QColor, QBrush, QScreen,
                           QShortcut, QKeySequence)

from typings import Screenshot
from area_selection import AreaSelection
from toolkit import Toolkit, ToolkitButton, ToolkitColorMenu
from drawing import Draw
from utils import isPointOnScreen, mapPointToRect


class Screenshooter(QWidget):
    active: bool
    ignoreFocus: bool
    selection: QRect
    screens: list[QScreen]
    screenshot: QPixmap

    previewLabel: QLabel
    areaSelection: AreaSelection
    draw: Draw

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.move(0, 0)

        self.previewLabel = QLabel(self)
        self.areaSelection = AreaSelection(self)
        self.draw = Draw(self)
        self.active = False

        self.areaSelection.transformStart.connect(
            self.hideToolkit
        )
        self.areaSelection.transformEnd.connect(
            lambda sel: [self.setSelection(sel), self.showToolkit()]
        )

        self.colorMenu = ToolkitColorMenu(self)
        self.colorMenu.currentColorChanged.connect(self.draw.setColor)
        self.draw.setColor(self.colorMenu.currentColor())

        self.toolkitHor = Toolkit(
            self,
            [
                Toolkit.Button.Cursor,
                Toolkit.Button.DrawBrush,
                Toolkit.Button.DrawArrow,
                Toolkit.Button.DrawLine,
                Toolkit.Button.DrawSquare,
                Toolkit.Button.DrawEllipse,
                Toolkit.Button.DrawText,
                Toolkit.Button.Color,
            ],
            Toolkit.Orientation.Horizontal
        )
        self.toolkitVer = Toolkit(
            self,
            [Toolkit.Button.Close, Toolkit.Button.Copy, Toolkit.Button.Save],
            Toolkit.Orientation.Vertical
        )

        self.toolkitHor.action.connect(self.toolkitAction)
        self.toolkitVer.action.connect(self.toolkitAction)

        self.saveShortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.saveShortcut.activated.connect(self.saveScreenshot)
        self.clipboardShortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        self.clipboardShortcut.activated.connect(self.copyScreenshot)
        self.undoShortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        self.undoShortcut.activated.connect(self.draw.undo)

    def activate(self):
        self.active = True
        self.ignoreFocus = False
        self.shoot()

        self.show()
        self.activateWindow()

    def shoot(self) -> None:
        self.screens = QGuiApplication.screens()

        screenshots = self.getScreenshots(self.screens)
        self.screenshot = self.mergeScreenshots(screenshots)

        self.hideToolkit()
        self.draw.setCanvas(self.screenshot.rect())
        self.draw.stop()
        self.updatePreview(self.screenshot)
        self.areaSelection.start(self.screenshot)

    def getScreenshots(self, screens: list[QScreen]) -> list[Screenshot]:
        screenshots = list[Screenshot]()

        for screen in screens:
            geom = screen.geometry()

            screenshots.append(
                Screenshot(QPoint(geom.x(), geom.y()), screen.grabWindow(0))
            )

        return screenshots

    def mergeScreenshots(self, screenshots: list[Screenshot]) -> QPixmap:
        width, height = 0, 0
        for pos, pixmap in screenshots:
            width += pixmap.width()
            if height < pixmap.height():
                height = pixmap.height()

        mergedShot = QPixmap(QSize(width, height))
        mergedShot.fill(QColor(0, 0, 0, 0))

        painter = QPainter(mergedShot)
        for pos, pixmap in screenshots:
            painter.drawPixmap(pos, pixmap)
        painter.end()

        return mergedShot

    def updatePreview(self, newPreview: QPixmap) -> None:
        newPreview = newPreview.copy()  # Prevent modifying base value
        w, h = newPreview.width(), newPreview.height()

        painter = QPainter(newPreview)

        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.drawRect(0, 0, w, h)
        painter.end()

        self.previewLabel.setFixedSize(w, h)
        self.previewLabel.setPixmap(newPreview)

    def toolkitAction(self, buttonType: Toolkit.Button, button: ToolkitButton):
        self.draw.stop()
        match buttonType:
            case Toolkit.Button.Save:
                self.saveScreenshot()
            case Toolkit.Button.Copy:
                self.copyScreenshot()
            case Toolkit.Button.Close:
                self.hide()
            case Toolkit.Button.Cursor:
                self.draw.stop()
            case Toolkit.Button.Color:
                self.colorMenu.toggle(
                    QPoint(
                        button.x()+button.parent().x()+button.width()/2,
                        button.y()+button.parent().y()
                    )
                )
                self.colorMenu.currentColorChanged.connect(
                    button.setColorIcon
                )
            case DrawTools:
                self.draw.start(buttonType.value)
                self.toolkitHor.raise_()
                self.toolkitVer.raise_()

    def saveScreenshot(self):
        self.ignoreFocus = True
        fileName = QFileDialog.getSaveFileName(
            self,
            caption='Save Screenshot',
            dir=QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DesktopLocation
            ),
            filter="Images (*.png *.jpg *.jpeg);;All files (*)"
        )
        self.ignoreFocus = False
        if fileName != ('', ''):
            self.hide()
            self.getFinalScreenshot().save(fileName[0])

    def copyScreenshot(self):
        QApplication.clipboard().setImage(
            self.getFinalScreenshot().toImage())
        self.hide()

    def getFinalScreenshot(self):
        screenshot = self.screenshot.copy(self.selection)

        painter = QPainter(screenshot)
        painter.drawPixmap(
            QPoint(0, 0), self.draw.drawPixmap().copy(self.selection)
        )

        return screenshot

    def setSelection(self, newSelection: QRect):
        self.selection = newSelection

    def showToolkit(self):
        posH = self.alignToolkit(
            self.toolkitHor.geometry(), oy1=-40, ox2=-self.toolkitHor.width(), oy2=10)
        posV = self.alignToolkit(
            self.toolkitVer.geometry(), ox1=-40, oy2=-self.toolkitVer.height(), ox2=10)

        self.toolkitHor.move(posH)
        self.toolkitVer.move(posV)

        self.toolkitHor.show()
        self.toolkitVer.show()

    def hideToolkit(self):
        self.toolkitHor.hide()
        self.toolkitVer.hide()
        self.colorMenu.deactivate()

    def alignToolkit(self, geometry: QRect, ox1=0, oy1=0, ox2=0, oy2=0) -> QPoint:
        geometry.moveTo(
            self.selection.topLeft().x()+ox1,
            self.selection.topLeft().y()+oy1
        )
        if not isPointOnScreen(geometry.topLeft()):
            geometry.moveTo(
                self.selection.bottomRight().x()+ox2,
                self.selection.bottomRight().y()+oy2
            )

        return QPoint(geometry.x(), geometry.y())

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate and not self.ignoreFocus:
            self.hide()
            event.accept()
        else:
            event.ignore()
        return super().event(event)

    def keyPressEvent(self, event) -> None:
        # Hide on hitting ESC
        if event.key() == Qt.Key.Key_Escape:
            if self.draw.active:
                self.toolkitHor.clearTool()
                self.toolkitVer.clearTool()
            else:
                self.hide()
            event.accept()
        else:
            event.ignore()

    def hideEvent(self, ev) -> None:
        self.active = False
