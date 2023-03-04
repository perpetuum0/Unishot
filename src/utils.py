from multipledispatch import dispatch
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QPoint, QPointF, QLineF, QRect


def isPointOnScreen(point: QPoint) -> bool:
    for scr in QGuiApplication.screens():
        if scr.geometry().contains(point):
            return True
    return False


def closestPointToLine(point: QPointF, line: QLineF) -> QPointF:
    p1 = line.p1()
    p2 = line.p2()
    p3 = point
    dx, dy = p2.x()-p1.x(), p2.y()-p1.y()
    det = dx*dx + dy*dy
    a = (dy*(p3.y()-p1.y())+dx*(p3.x()-p1.x()))/det
    return QPointF(p1.x()+a*dx, p1.y()+a*dy)


def mapPointToRect(globalP: QPoint, rect: QRect) -> QPoint:
    return QPoint(globalP.x()-rect.left(),
                  globalP.y()-rect.top())


# TODO: expand these functions
@dispatch(QPoint, QPoint)
def QSum(p1: QPoint, p2: QPoint) -> QPoint:
    return QPoint(p1.x()+p2.x(), p1.y()+p2.y())


@dispatch(QPoint, QPoint)
def QDiff(p1: QPoint, p2: QPoint) -> QPoint:
    return QPoint(p1.x()-p2.x(), p1.y()-p2.y())


def circumRect(rects: list[QRect]) -> QRect:
    minPoint = rects[0].topLeft()
    maxPoint = rects[0].bottomRight()

    for rect in rects:
        tL = rect.topLeft()
        bR = rect.bottomRight()

        if tL.x() < minPoint.x():
            minPoint.setX(tL.x())
        if tL.y() < minPoint.y():
            minPoint.setY(tL.y())
        if bR.x() > maxPoint.x():
            maxPoint.setX(bR.x())
        if bR.y() > maxPoint.y():
            maxPoint.setY(bR.y())
    return QRect(minPoint, maxPoint)


def expandRect(rect: QRect, margin: int) -> QRect:
    rect = rect.normalized()
    return QRect(
        QPoint(rect.topLeft().x()-margin,
               rect.topLeft().y()-margin),
        QPoint(rect.bottomRight().x()+margin,
               rect.bottomRight().y()+margin)
    )
