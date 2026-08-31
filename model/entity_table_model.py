from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex

from game.entity import Entity
from signals import EntitySignals


class EntityTableModel(QtCore.QAbstractTableModel):
    COLUMNS = ["Active", "Param 1", "Param 2"]

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
        return len(self.COLUMNS)

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
            if index.column() == 0:
                return entity.occupied
            elif index.column() == 1:
                return entity.param_1
            elif index.column() == 2:
                return entity.param_2

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
