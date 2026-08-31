from PySide6.QtCore import Signal, QObject
from game.entity import Entity
from game.vram import Pixels


class EntitySignals(QObject):
    entity_discovered = Signal(Entity)
    entity_updated = Signal(Entity)


class VRAMSignals(QObject):
    vram_loaded = Signal(Pixels)
