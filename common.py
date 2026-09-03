import logging
from PySide6 import QtWidgets

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class GuiLogger(logging.Handler):
    """Interface between python logging and QT"""

    display: QtWidgets.QTextEdit

    def __init__(self, display: QtWidgets.QTextEdit):
        super().__init__()

        self.display = display

    def emit(self, record):
        self.display.textCursor().insertText(f"{self.format(record)}\n")


def wheel_zoom(ui, event):
    """Zooms into the image based on mouse wheel movement."""
    zoom_factor = 1.15

    if event.angleDelta().y() > 0:
        # Zoom In
        ui.scale(zoom_factor, zoom_factor)
    elif event.angleDelta().y() < 0:
        # Zoom Out
        ui.scale(1.0 / zoom_factor, 1.0 / zoom_factor)

    event.accept()
