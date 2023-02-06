from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QPoint


def isPointOnScreen(point: QPoint) -> bool:
    for scr in QGuiApplication.screens():
        if scr.geometry().contains(point):
            return True
    return False
