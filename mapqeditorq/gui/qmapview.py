# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class QMapPixmap(QtWidgets.QGraphicsObject):
    clicked = QtCore.pyqtSignal(QtWidgets.QGraphicsSceneMouseEvent)
    click_dragged = QtCore.pyqtSignal(QtWidgets.QGraphicsSceneMouseEvent)
    click_release = QtCore.pyqtSignal(QtWidgets.QGraphicsSceneMouseEvent)

    def __init__(self, pixmap):
        super(QMapPixmap, self).__init__()
        self.set_pixmap(pixmap)
        self.button = None

    def boundingRect(self):
        return QtCore.QRectF(self.pixmap.rect())

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap

    def mousePressEvent(self, event):
        self.button = event.button()
        self.clicked.emit(event)

    def mouseMoveEvent(self, event):
        b = self.button
        event.button = lambda: b
        self.click_dragged.emit(event)

    def mouseReleaseEvent(self, event):
        self.click_release.emit(event)
        self.button = None

    def paint(self, painter, option, widget):
        painter.drawPixmap(QtCore.QPoint(0, 0), self.pixmap)

