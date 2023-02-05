from typings import Screenshot
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QFileDialog
from PySide6.QtCore import (Qt, QPoint, QSize, QEvent, QRect, QStandardPaths)
from PySide6.QtGui import (QGuiApplication, QPixmap,
                           QPainter, QColor, QBrush, QScreen,
                           QShortcut, QKeySequence)
from area_selection import AreaSelection
from toolkit import Toolkit
from typings import ToolkitButtons


class Screenshooter(QWidget):
    ignoreFocus: bool

    selection: QRect
    screenshot: QPixmap

    previewLabel: QLabel
    areaSelection: AreaSelection

    def __init__(self) -> None:
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.move(0, 0)

        self.previewLabel = QLabel(self)
        self.previewLabel.show()

        self.areaSelection = AreaSelection(self)
        self.areaSelection.show()
        self.areaSelection.transformStart.connect(self.hideToolkit)
        self.areaSelection.transformEnd.connect(
            lambda sel: [self.setSelection(sel), self.showToolkit()]
        )

        self.toolkit = Toolkit(
            self.areaSelection)
        self.toolkit.action.connect(self.toolkitAction)

        self.saveShortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.saveShortcut.activated.connect(self.saveScreenshot)
        self.clipboardShortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        self.clipboardShortcut.activated.connect(
            self.copyScreenshot)

    def activate(self):
        self.ignoreFocus = False
        self.shoot()
        self.show()
        self.activateWindow()

    def shoot(self) -> None:
        screenshots = self.getScreenshots(QGuiApplication.screens())

        self.screenshot = self.mergeScreenshots(screenshots)

        self.hideToolkit()
        self.updatePreview(self.screenshot)
        self.areaSelection.start(self.screenshot)

    def getScreenshots(self, screens: list[QScreen]) -> list[Screenshot]:
        screenshots = list[Screenshot]()

        for screen in screens:
            geom = screen.geometry()
            screenshots.append(
                Screenshot(screen.grabWindow(0), QPoint(geom.x(), geom.y()))
            )

        return screenshots

    def mergeScreenshots(self, screenshots: list[Screenshot]) -> QPixmap:
        width, height = 0, 0
        for pixmap, pos in screenshots:
            width += pixmap.width()
            if height < pixmap.height():
                height = pixmap.height()

        mergedShot = QPixmap(QSize(width, height))
        mergedShot.fill(QColor(0, 0, 0, 0))

        painter = QPainter(mergedShot)
        for pixmap, pos in screenshots:
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

    def toolkitAction(self, button: ToolkitButtons):
        match button:
            case ToolkitButtons.Save:
                self.saveScreenshot()
            case ToolkitButtons.Copy:
                self.copyScreenshot()

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
            self.screenshot.copy(self.selection).save(fileName[0])

    def copyScreenshot(self):
        QApplication.clipboard().setImage(
            self.screenshot.copy(self.selection).toImage())
        self.hide()

    def setSelection(self, newSelection: QRect):
        self.selection = newSelection

    def showToolkit(self):
        # TODO: adjust to screen corners
        pos = self.selection
        self.toolkit.move(pos.x()-1, pos.y()-35)
        self.toolkit.show()

    def hideToolkit(self):
        self.toolkit.hide()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate and not self.ignoreFocus:
            self.hide()
            event.accept()
        else:
            event.ignore()
        return super().event(event)

    def keyPressEvent(self, event) -> None:
        if (event.key() == 16777216):
            self.hide()
            event.accept()
        else:
            event.ignore()
