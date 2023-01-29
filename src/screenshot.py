from typings import Screenshot
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore import (Qt, QPoint, QSize, QEvent)
from PySide6.QtGui import (QGuiApplication, QPixmap,
                           QPainter, QColor, QBrush, QScreen,
                           QShortcut, QKeySequence)
from area_selection import AreaSelection


class Screenshooter(QWidget):
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

        self.clipboardShortcut = QShortcut(QKeySequence("CTRL+C"), self)
        self.clipboardShortcut.activated.connect(
            self.copyScreenshotToClipboard)

    def activate(self):
        self.shoot()
        self.show()
        self.activateWindow()

    def shoot(self) -> None:
        screenshots = self.getScreenshots(QGuiApplication.screens())

        self.screenshot = self.mergeScreenshots(screenshots)

        self.areaSelection.start(self.screenshot)
        self.updatePreview(self.screenshot)

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

    def copyScreenshotToClipboard(self):
        QApplication.clipboard().setImage(
            self.screenshot.copy(self.areaSelection.selection).toImage())
        self.hide()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate:
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
