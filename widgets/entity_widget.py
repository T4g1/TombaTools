from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QGraphicsScene
from PySide6.QtGui import QPixmap

from common import wheel_zoom
from pixmap_builder import build_preview

from entity_widget_ui import Ui_EntityWidget

from game.frame import Frame
from game.entity import Entity
from widgets.pixmap_item import PixmapItem
from widgets.vram_zoom_viewer import VRAMZoomViewer

PREVIEW_TIMER = 500


class EntityWidget(QWidget):
    entity_preview: PixmapItem
    vram_zoom_viewer: VRAMZoomViewer

    load_preview = Signal(Entity)
    update_entity = Signal(Entity)
    refresh_entity = Signal(Entity)

    current_entity: Entity | None = None

    def __init__(self, vram_zoom_viewer: VRAMZoomViewer, parent=None):
        super().__init__(parent)

        self.ui = Ui_EntityWidget()
        self.ui.setupUi(self)

        self.vram_zoom_viewer = vram_zoom_viewer

        scene = QGraphicsScene(self)
        self.entity_preview = PixmapItem()
        scene.addItem(self.entity_preview)
        self.ui.entity_preview.setScene(scene)
        self.ui.entity_preview.wheelEvent = lambda event: wheel_zoom(
            self.ui.entity_preview, event
        )
        self.ui.animate_preview.toggled.connect(self.set_animation_timer)
        self.ui.switch_state_button.pressed.connect(self.on_switch_state)
        self.ui.use_clut_button.pressed.connect(self.on_use_clut)
        self.ui.refresh_button.pressed.connect(self.emit_refresh_entity)

        self.preview_timer = QTimer(self)
        self.preview_timer.setInterval(PREVIEW_TIMER)
        self.preview_timer.timeout.connect(self.emit_refresh_entity)

    def clear_preview(self):
        """Clears preview area"""
        self.pixmap_preview = None
        self.entity_preview.setPixmap(QPixmap())
        self.ui.entity_preview.resetTransform()
        self.ui.entity_preview.centerOn(0, 0)

    def on_preview_frames(self, frames: list[Frame]):
        """Display preview frames"""
        self.pixmap_preview = build_preview(
            frames, self.vram_zoom_viewer.raw_data, self.current_entity
        )
        self.entity_preview.setPixmap(self.pixmap_preview)
        self.entity_preview.setScale(2.0)

    def set_animation_timer(self, animated: bool):
        """Determines wether or not the animation timer should run"""
        if animated and not self.preview_timer.isActive():
            self.preview_timer.start()

        if not animated:
            self.preview_timer.stop()

    def on_preview_entity(self, entity: Entity):
        """Displays an entity and start timer"""
        self.clear_preview()
        self.display_entity(entity)
        self.set_animation_timer(self.ui.animate_preview.isChecked())
        self.emit_load_preview()

    def emit_load_preview(self):
        """Ask to refresh the preview"""
        if self.current_entity is not None:
            self.load_preview.emit(self.current_entity)

    def emit_refresh_entity(self):
        if self.current_entity is not None:
            self.refresh_entity.emit(self.current_entity)

    def display_entity(self, entity: Entity):
        """Displays entity informations"""
        self.current_entity = entity

        self.ui.address.setText(f"0x{entity.address:08X}")
        self.ui.raw.setText(f"{entity.raw.hex()}")
        self.ui.clut.setText(f"0x{entity.clut:08X}")
        self.ui.handler_id.setText(f"0x{entity.handler_id:02X}")
        self.ui.handlers_array_id.setText(f"0x{entity.handlers_array_id:02X}")
        self.ui.handler_address.setText(f"0x{entity.get_handler_address():08X}")
        self.ui.frame_array_address.setText(f"0x{entity.current_frame:08X}")
        self.ui.current_frame_address.setText(f"0x{entity.frame_array:08X}")

        self.ui.position_x.setText(f"{entity.position_x}")
        self.ui.position_y.setText(f"{entity.position_y}")
        self.ui.position_z.setText(f"{entity.position_z}")

        self.ui.occupied.setChecked(entity.occupied != 0x00)
        self.ui.active.setChecked(entity.active != 0x00)

    def on_switch_state(self):
        if self.current_entity is None:
            return

        self.current_entity.occupied = 0x00 if self.current_entity.occupied else 0x01
        self.update_entity.emit(self.current_entity)

        action_text = "Disable" if self.current_entity.occupied else "Enable"
        self.ui.switch_state_button.setText(action_text)

    def on_use_clut(self):
        pass

    def on_refresh(self, entity: Entity):
        if self.current_entity is None or self.current_entity.address == entity.address:
            self.display_entity(entity)
            self.emit_load_preview()
