from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import (Qt, QPoint, QSize, QEvent)
from PySide6.QtGui import (QGuiApplication, QPixmap,
                           QPainter, QColor, QBrush, QScreen, QHideEvent)
from areaSelection import AreaSelection


class Screenshot(QWidget):
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

    def activate(self):
        self.shoot()
        self.show()
        self.activateWindow()

    def shoot(self) -> None:
        screenshots = self.get_screenshots(QGuiApplication.screens())

        self.screenshot = self.merge_screenshots(screenshots)

        self.areaSelection.start(self.screenshot)
        self.update_preview(self.screenshot)

    def get_screenshots(self, screens: list[QScreen]) -> list[tuple[QPixmap, QPoint]]:
        # [(screen_pixmap, screen_position)]
        screenshots = []

        for screen in screens:
            geom = screen.geometry()
            screenshots.append(
                (screen.grabWindow(0), QPoint(geom.x(), geom.y()))
            )

        return screenshots

    def merge_screenshots(self, screenshots: list) -> QPixmap:
        width, height = 0, 0
        for pixmap, pos in screenshots:
            width += pixmap.width()
            if height < pixmap.height():
                height = pixmap.height()

        merged_shot = QPixmap(QSize(width, height))
        merged_shot.fill(QColor(0, 0, 0, 0))

        painter = QPainter(merged_shot)
        for pixmap, pos in screenshots:
            painter.drawPixmap(pos, pixmap)
        painter.end()

        return merged_shot

    def update_preview(self, newPreview: QPixmap) -> None:
        newPreview = newPreview.copy()  # Prevent modifying original preview
        w, h = newPreview.width(), newPreview.height()

        painter = QPainter(newPreview)

        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.drawRect(0, 0, w, h)
        painter.end()

        self.previewLabel.setFixedSize(w, h)
        self.previewLabel.setPixmap(newPreview)

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate:
            self.hide()
            event.accept()
        event.ignore()
        return super().event(event)

    def keyPressEvent(self, event) -> None:
        if (event.key() == 16777216):
            self.hide()
            event.accept()
        event.ignore()
