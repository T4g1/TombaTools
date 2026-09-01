from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex
from enum import IntEnum

from game.entity import Entity
from signals import EntitySignals


class Columns(IntEnum):
    ACTIVE = 0
    PARAM_1 = 1
    PARAM_2 = 2
    INITIALIZED = 3
    STATUS = 4
    CLUT = 5
    TEXT_X_START = 6
    TEXT_X_END = 7
    TEXT_Y_START = 8
    TEXT_Y_END = 9
    RAW = 10
    ADDRESS = 11


class EntityTableModel(QtCore.QAbstractTableModel):
    COLUMNS = {
        Columns.ACTIVE: "Active",
        Columns.INITIALIZED: "Initialized",
        Columns.PARAM_1: "Param 1",
        Columns.PARAM_2: "Param 2",
        Columns.STATUS: "Status",
        Columns.TEXT_X_START: "Texture X start",
        Columns.TEXT_X_END: "Texture X end",
        Columns.TEXT_Y_START: "Texture Y start",
        Columns.TEXT_Y_END: "Texture Y end",
        Columns.RAW: "Raw",
        Columns.CLUT: "CLUT",
        Columns.ADDRESS: "Address",
    }

    entities: list[Entity]
    signals: EntitySignals

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entities = []
        self.signals = EntitySignals()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.entities) - 1)
        self.entities.clear()
        self.endRemoveRows()

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.entities)

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self.COLUMNS.keys())

    def addRow(self, entity: Entity):
        self.entities.append(entity)
        self.layoutChanged.emit()
        return True

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.COLUMNS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.entities):
            return None

        entity = self.entities[index.row()]

        if role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 0:
                return (
                    Qt.CheckState.Checked
                    if entity.occupied
                    else Qt.CheckState.Unchecked
                )

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == Columns.ADDRESS:
                return f"0x{entity.address:08X}"
            if index.column() == Columns.ACTIVE:
                return f"0x{entity.occupied:02X}"
            elif index.column() == Columns.PARAM_1:
                return f"0x{entity.param_1:02X}"
            elif index.column() == Columns.PARAM_2:
                return f"0x{entity.param_2:02X}"
            elif index.column() == Columns.INITIALIZED:
                return f"0x{entity.initialized:02X}"
            elif index.column() == Columns.STATUS:
                return f"0x{entity.status:02X}"
            elif index.column() == Columns.RAW:
                return entity.raw.hex()
            elif index.column() == Columns.TEXT_X_START:
                return f"0x{entity.texture_x_start:08X}"
            elif index.column() == Columns.TEXT_Y_START:
                return f"0x{entity.texture_y_start:08X}"
            elif index.column() == Columns.TEXT_X_END:
                return f"0x{entity.texture_x_end:08X}"
            elif index.column() == Columns.TEXT_Y_END:
                return f"0x{entity.texture_y_end:08X}"
            elif index.column() == Columns.CLUT:
                return f"0x{entity.clut:04X}"

        if role == Qt.ItemDataRole.UserRole:
            return entity

        return None

    def setData(self, index, value: Entity, role):
        if role == Qt.ItemDataRole.CheckStateRole:
            checked = value == Qt.CheckState.Checked.value

            new_value = 0x00
            if checked:
                new_value = 0x01

            self.entities[index.row()].occupied = new_value
            self.signals.entity_updated.emit(self.entities[index.row()])

            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )
