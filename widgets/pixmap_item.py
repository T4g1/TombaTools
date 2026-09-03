from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)
from PySide6.QtCore import Qt

from signals import VRAMHoverSignals


class PixmapItem(QGraphicsPixmapItem):
    signals: VRAMHoverSignals

    def __init__(self, parent=None):
        super().__init__(parent)

        self.signals = VRAMHoverSignals()

        self.setAcceptHoverEvents(True)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverMoveEvent(event)

        self.signals.mouse_moved.emit(event.pos())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        super().mousePressEvent(event)

        if event.button() is Qt.MouseButton.RightButton:
            self.signals.mouse_click.emit(event.pos())
