from PySide6.QtCore import Signal, QObject, QPointF
from game.entity import Entity


class EntitySignals(QObject):
    entity_discovered = Signal(Entity)
    entity_updated = Signal(Entity)


class VRAMSignals(QObject):
    vram_loaded = Signal(bytearray)


class VRAMHoverSignals(QObject):
    mouse_moved = Signal(QPointF)
    mouse_click = Signal(QPointF)
