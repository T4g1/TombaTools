from PySide6.QtCore import Signal, QObject, QPointF


class VRAMHoverSignals(QObject):
    mouse_moved = Signal(QPointF)
    mouse_click = Signal(QPointF)
