from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QPoint, QRect


def isPointOnScreen(point: QPoint) -> bool:
    for scr in QGuiApplication.screens():
        if scr.geometry().contains(point):
            return True
    return False


def mapPointToRect(globalP: QPoint, rect: QRect):
    return QPoint(globalP.x()-rect.left(),
                  globalP.y()-rect.top())
