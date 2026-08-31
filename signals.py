from PySide6.QtCore import Signal, QObject
from game.entity import Entity


class EntitySignals(QObject):
    entity_discovered = Signal(Entity)
    entity_updated = Signal(Entity)
