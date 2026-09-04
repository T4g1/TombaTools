from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex, Signal
from enum import IntEnum

from game.entity import Entity


class EntityColumns(IntEnum):
    OCCUPIED = 0
    ACTIVE = 1
    ADDRESS = 2
    HANDLER_ID = 3
    HANDLERS_ARRAY_ID = 4
    HANDLER = 5
    CLUT = 6
    CURRENT_FRAME = 7
    FRAMES_ARRAY = 8
    STATUS = 9
    RAW = 10


class EntityTableModel(QtCore.QAbstractTableModel):
    COLUMNS = {
        EntityColumns.OCCUPIED: "Occupied",
        EntityColumns.ACTIVE: "Active",
        EntityColumns.ADDRESS: "Address",
        EntityColumns.HANDLER_ID: "Handler ID",
        EntityColumns.HANDLERS_ARRAY_ID: "Handlers array ID",
        EntityColumns.HANDLER: "Handler",
        EntityColumns.STATUS: "Status",
        EntityColumns.CLUT: "CLUT",
        EntityColumns.CURRENT_FRAME: "Frame",
        EntityColumns.FRAMES_ARRAY: "Frames",
        EntityColumns.RAW: "Raw",
    }

    entities: list[Entity]

    entity_updated = Signal(Entity)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entities = []

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
            if index.column() == EntityColumns.OCCUPIED:
                return (
                    Qt.CheckState.Checked
                    if entity.occupied
                    else Qt.CheckState.Unchecked
                )
            elif index.column() == EntityColumns.ACTIVE:
                return (
                    Qt.CheckState.Checked if entity.active else Qt.CheckState.Unchecked
                )

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == EntityColumns.ADDRESS:
                return f"0x{entity.address:08X}"
            elif index.column() == EntityColumns.ACTIVE:
                return f"0x{entity.active:02X}"
            elif index.column() == EntityColumns.OCCUPIED:
                return f"0x{entity.occupied:02X}"
            elif index.column() == EntityColumns.HANDLER_ID:
                return f"0x{entity.handler_id:02X}"
            elif index.column() == EntityColumns.HANDLERS_ARRAY_ID:
                return f"0x{entity.handlers_array_id:02X}"
            elif index.column() == EntityColumns.HANDLER:
                return f"0x{entity.get_handler_address():08X}"
            elif index.column() == EntityColumns.STATUS:
                return f"0x{entity.status:02X}"
            elif index.column() == EntityColumns.RAW:
                return entity.raw.hex()
            elif index.column() == EntityColumns.CLUT:
                return f"0x{entity.clut:04X}"
            elif index.column() == EntityColumns.CURRENT_FRAME:
                return f"0x{entity.current_frame:08X}"
            elif index.column() == EntityColumns.FRAMES_ARRAY:
                return f"0x{entity.frame_array:08X}"

        if role == Qt.ItemDataRole.UserRole:
            return entity

        return None

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.CheckStateRole:
            checked = value == Qt.CheckState.Checked.value

            new_value = 0x00
            if checked:
                new_value = 0x01

            entity = self.entities[index.row()]
            if index.column() == EntityColumns.ACTIVE:
                entity.active = new_value
            elif index.column() == EntityColumns.OCCUPIED:
                entity.occupied = new_value

            self.entities[index.row()] = entity
            self.entity_updated.emit(entity)

            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )

    def on_entity_updated(self, entity: Entity):
        for i in range(len(self.entities)):
            if self.entities[i].address == entity.address:
                self.entities[i] = entity

    def sort(self, column: int, order: Qt.SortOrder):
        self.layoutAboutToBeChanged.emit()

        reverse = order == Qt.SortOrder.DescendingOrder

        mapping = {
            EntityColumns.ADDRESS: lambda e: e.address,
            EntityColumns.ACTIVE: lambda e: e.active,
            EntityColumns.OCCUPIED: lambda e: e.occupied,
            EntityColumns.HANDLER_ID: lambda e: e.handler_id,
            EntityColumns.HANDLERS_ARRAY_ID: lambda e: e.handlers_array_id,
            EntityColumns.HANDLER: lambda e: e.get_handler_address(),
            EntityColumns.STATUS: lambda e: e.status,
            EntityColumns.RAW: lambda e: e.raw.hex(),
            EntityColumns.CLUT: lambda e: e.clut,
            EntityColumns.CURRENT_FRAME: lambda e: e.current_frame,
            EntityColumns.FRAMES_ARRAY: lambda e: e.frame_array,
        }

        self.entities.sort(key=mapping[EntityColumns(column)], reverse=reverse)

        self.layoutChanged.emit()
