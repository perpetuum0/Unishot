from PySide6.QtWidgets import QWidget, QLabel, QApplication, QFileDialog
from PySide6.QtCore import (
    Qt, QPoint, QEvent, QRect, QStandardPaths)
from PySide6.QtGui import (QGuiApplication, QPixmap,
                           QPainter, QColor, QBrush, QScreen,
                           QShortcut, QKeySequence)

from typings import Screenshot
from area_selection import AreaSelection
from toolkit import Toolkit, ToolkitButton, ToolkitColorMenu
from drawing import Draw, PostEffects
import utils


class Screenshooter(QWidget):
    __active: bool
    ignoreFocus: bool
    selection: QRect
    screens: list[QScreen]
    screenshot: QPixmap
    postEffects: PostEffects

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
        self.postEffects = PostEffects()
        self.__active = False

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
                Toolkit.Button.FlipHor,
                Toolkit.Button.FlipVer,
                # [Toolkit.Button.FlipVer, Toolkit.Button.FlipHor]
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
        self.redoShortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        self.redoShortcut.activated.connect(self.draw.redo)
        self.selectAllShortcut = QShortcut(
            QKeySequence.StandardKey.SelectAll, self
        )
        self.selectAllShortcut.activated.connect(
            lambda: self.areaSelection.setSelection(self.screenshot.rect())
        )

    def activate(self) -> None:
        self.__active = True
        self.ignoreFocus = False
        self.shoot()
        self.selection = self.screenshot.rect()  # select all by default

        self.show()
        self.activateWindow()

    def shoot(self) -> None:
        self.screens = QGuiApplication.screens()

        screenshots = self.getScreenshots(self.screens)
        self.screenshot = self.mergeScreenshots(screenshots)

        cRect = utils.circumRect(
            [s.Geometry for s in screenshots]
        )

        self.setGeometry(cRect)

        self.hideToolkit()
        self.draw.setCanvas(cRect)
        self.draw.stop()
        self.postEffects.clear()
        self.updatePreview(self.screenshot)
        self.areaSelection.start(self.screenshot, cRect.topLeft())

    def getScreenshots(self, screens: list[QScreen]) -> list[Screenshot]:
        screenshots = list[Screenshot]()

        for screen in screens:
            screenshots.append(
                Screenshot(screen.geometry(), screen.grabWindow(0))
            )

        return screenshots

    def mergeScreenshots(self, screenshots: list[Screenshot]) -> QPixmap:
        cRect = utils.circumRect(
            [s.Geometry for s in screenshots]
        )
        offset = cRect.topLeft()

        mergedShot = QPixmap(
            cRect.width() - offset.x(),
            cRect.height() - offset.y()
        )
        mergedShot.fill(QColor(0, 0, 0, 0))

        painter = QPainter(mergedShot)
        for geom, pixmap in screenshots:
            painter.drawPixmap(
                utils.QDiff(geom.topLeft(), offset),
                pixmap
            )
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

    def toolkitAction(self, buttonType: Toolkit.Button, button: ToolkitButton) -> None:
        match buttonType:
            case Toolkit.Button.Save:
                self.saveScreenshot()
                self.draw.stop()
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
                self.colorMenu.deactivated.connect(
                    lambda: button.setChecked(False)
                )
            case Toolkit.Button.FlipHor:
                self.postEffects.toggleFlip(x=True)
                self.updatePostEffects()
            case Toolkit.Button.FlipVer:
                self.postEffects.toggleFlip(y=True)
                self.updatePostEffects()
            case Toolkit.Button.RotateLeft | Toolkit.Button.RotateRight:
                raise NotImplementedError
            case DrawTools:
                self.draw.start(buttonType.value)
                self.toolkitHor.raise_()
                self.toolkitVer.raise_()

    def saveScreenshot(self) -> None:
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

    def copyScreenshot(self) -> None:
        QApplication.clipboard().setImage(
            self.getFinalScreenshot().toImage())
        self.hide()

    def getFinalScreenshot(self) -> QPixmap:
        # Post effects do not apply to drawings.
        finalScreenshot = self.postEffects.apply(
            self.screenshot.copy(self.selection)
        )

        painter = QPainter(finalScreenshot)
        painter.drawPixmap(
            QPoint(0, 0), self.draw.drawPixmap().copy(self.selection)
        )
        painter.end()

        return finalScreenshot

    def updatePostEffects(self) -> None:
        self.areaSelection.selectionPreview.setEffects(
            self.postEffects
        )

    def setSelection(self, newSelection: QRect) -> None:
        self.selection = newSelection

    def showToolkit(self) -> None:
        posH = self.alignToolkit(
            self.toolkitHor.geometry(), oy1=-40, ox2=-self.toolkitHor.width(), oy2=10)
        posV = self.alignToolkit(
            self.toolkitVer.geometry(), ox1=-40, oy2=-self.toolkitVer.height(), ox2=10)

        self.toolkitHor.move(posH)
        self.toolkitVer.move(posV)

        self.toolkitHor.show()
        self.toolkitVer.show()

    def hideToolkit(self) -> None:
        self.toolkitHor.hide()
        self.toolkitVer.hide()
        self.colorMenu.deactivate()

    def alignToolkit(self, geometry: QRect, ox1=0, oy1=0, ox2=0, oy2=0) -> QPoint:
        geometry.moveTo(
            self.selection.topLeft().x()+ox1,
            self.selection.topLeft().y()+oy1
        )
        if not utils.isPointOnScreen(geometry.topLeft()):
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
            if self.colorMenu.active():
                self.colorMenu.deactivate()
            elif self.draw.active():
                self.toolkitHor.clearTool()
                self.toolkitVer.clearTool()
            else:
                self.hide()
            event.accept()
        else:
            event.ignore()

    def active(self) -> bool:
        return self.__active

    def hideEvent(self, ev) -> None:
        self.__active = False
