# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'entity_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_EntityWidget(object):
    def setupUi(self, EntityWidget):
        if not EntityWidget.objectName():
            EntityWidget.setObjectName("EntityWidget")
        EntityWidget.resize(297, 748)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(EntityWidget.sizePolicy().hasHeightForWidth())
        EntityWidget.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(EntityWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QLabel(EntityWidget)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.address = QLabel(EntityWidget)
        self.address.setObjectName("address")

        self.horizontalLayout_4.addWidget(self.address)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.entity_preview = QGraphicsView(EntityWidget)
        self.entity_preview.setObjectName("entity_preview")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.entity_preview.sizePolicy().hasHeightForWidth()
        )
        self.entity_preview.setSizePolicy(sizePolicy1)
        self.entity_preview.setMinimumSize(QSize(200, 200))
        self.entity_preview.setMouseTracking(True)
        self.entity_preview.setAutoFillBackground(True)
        brush = QBrush(QColor(126, 126, 126, 255))
        brush.setStyle(Qt.BrushStyle.Dense4Pattern)
        self.entity_preview.setBackgroundBrush(brush)
        self.entity_preview.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.entity_preview.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.entity_preview.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.verticalLayout_2.addWidget(self.entity_preview)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.animate_preview = QCheckBox(EntityWidget)
        self.animate_preview.setObjectName("animate_preview")

        self.horizontalLayout_3.addWidget(self.animate_preview)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.switch_state_button = QPushButton(EntityWidget)
        self.switch_state_button.setObjectName("switch_state_button")

        self.horizontalLayout.addWidget(self.switch_state_button)

        self.refresh_button = QPushButton(EntityWidget)
        self.refresh_button.setObjectName("refresh_button")

        self.horizontalLayout.addWidget(self.refresh_button)

        self.use_clut_button = QPushButton(EntityWidget)
        self.use_clut_button.setObjectName("use_clut_button")
        self.use_clut_button.setEnabled(True)

        self.horizontalLayout.addWidget(self.use_clut_button)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.occupied = QCheckBox(EntityWidget)
        self.occupied.setObjectName("occupied")
        self.occupied.setEnabled(False)

        self.horizontalLayout_11.addWidget(self.occupied)

        self.active = QCheckBox(EntityWidget)
        self.active.setObjectName("active")
        self.active.setEnabled(False)

        self.horizontalLayout_11.addWidget(self.active)

        self.verticalLayout_2.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_11 = QLabel(EntityWidget)
        self.label_11.setObjectName("label_11")

        self.horizontalLayout_10.addWidget(self.label_11)

        self.position_x = QLineEdit(EntityWidget)
        self.position_x.setObjectName("position_x")

        self.horizontalLayout_10.addWidget(self.position_x)

        self.label_10 = QLabel(EntityWidget)
        self.label_10.setObjectName("label_10")

        self.horizontalLayout_10.addWidget(self.label_10)

        self.position_y = QLineEdit(EntityWidget)
        self.position_y.setObjectName("position_y")

        self.horizontalLayout_10.addWidget(self.position_y)

        self.label_9 = QLabel(EntityWidget)
        self.label_9.setObjectName("label_9")

        self.horizontalLayout_10.addWidget(self.label_9)

        self.position_z = QLineEdit(EntityWidget)
        self.position_z.setObjectName("position_z")

        self.horizontalLayout_10.addWidget(self.position_z)

        self.verticalLayout_2.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_8 = QLabel(EntityWidget)
        self.label_8.setObjectName("label_8")

        self.horizontalLayout_9.addWidget(self.label_8)

        self.clut = QLineEdit(EntityWidget)
        self.clut.setObjectName("clut")

        self.horizontalLayout_9.addWidget(self.clut)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_5 = QLabel(EntityWidget)
        self.label_5.setObjectName("label_5")

        self.horizontalLayout_6.addWidget(self.label_5)

        self.handler_id = QLineEdit(EntityWidget)
        self.handler_id.setObjectName("handler_id")

        self.horizontalLayout_6.addWidget(self.handler_id)

        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_6 = QLabel(EntityWidget)
        self.label_6.setObjectName("label_6")

        self.horizontalLayout_7.addWidget(self.label_6)

        self.handlers_array_id = QLineEdit(EntityWidget)
        self.handlers_array_id.setObjectName("handlers_array_id")

        self.horizontalLayout_7.addWidget(self.handlers_array_id)

        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_7 = QLabel(EntityWidget)
        self.label_7.setObjectName("label_7")

        self.horizontalLayout_8.addWidget(self.label_7)

        self.handler_address = QLineEdit(EntityWidget)
        self.handler_address.setObjectName("handler_address")

        self.horizontalLayout_8.addWidget(self.handler_address)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QLabel(EntityWidget)
        self.label.setObjectName("label")

        self.horizontalLayout_2.addWidget(self.label)

        self.current_frame_address = QLineEdit(EntityWidget)
        self.current_frame_address.setObjectName("current_frame_address")

        self.horizontalLayout_2.addWidget(self.current_frame_address)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_3 = QLabel(EntityWidget)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.frame_array_address = QLineEdit(EntityWidget)
        self.frame_array_address.setObjectName("frame_array_address")

        self.horizontalLayout_5.addWidget(self.frame_array_address)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.label_2 = QLabel(EntityWidget)
        self.label_2.setObjectName("label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.raw = QTextEdit(EntityWidget)
        self.raw.setObjectName("raw")

        self.verticalLayout_2.addWidget(self.raw)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.retranslateUi(EntityWidget)

        QMetaObject.connectSlotsByName(EntityWidget)

    # setupUi

    def retranslateUi(self, EntityWidget):
        EntityWidget.setWindowTitle(
            QCoreApplication.translate("EntityWidget", "Form", None)
        )
        self.label_4.setText(
            QCoreApplication.translate("EntityWidget", "Address:", None)
        )
        self.address.setText(
            QCoreApplication.translate("EntityWidget", "PLACEHOLDER", None)
        )
        self.animate_preview.setText(
            QCoreApplication.translate("EntityWidget", "Animate", None)
        )
        self.switch_state_button.setText(
            QCoreApplication.translate("EntityWidget", "Activate", None)
        )
        self.refresh_button.setText(
            QCoreApplication.translate("EntityWidget", "Refresh", None)
        )
        self.use_clut_button.setText(
            QCoreApplication.translate("EntityWidget", "Use CLUT", None)
        )
        self.occupied.setText(
            QCoreApplication.translate("EntityWidget", "Occupied", None)
        )
        self.active.setText(QCoreApplication.translate("EntityWidget", "Active", None))
        self.label_11.setText(QCoreApplication.translate("EntityWidget", "X:", None))
        self.label_10.setText(QCoreApplication.translate("EntityWidget", "Y:", None))
        self.label_9.setText(QCoreApplication.translate("EntityWidget", "Z:", None))
        self.label_8.setText(QCoreApplication.translate("EntityWidget", "CLUT:", None))
        self.label_5.setText(
            QCoreApplication.translate("EntityWidget", "Handler ID (+0x02):", None)
        )
        self.label_6.setText(
            QCoreApplication.translate(
                "EntityWidget", "Hanlders array ID (+0x1C):", None
            )
        )
        self.label_7.setText(
            QCoreApplication.translate("EntityWidget", "Handler:", None)
        )
        self.label.setText(
            QCoreApplication.translate("EntityWidget", "Frame addr (+0x24):", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("EntityWidget", "Frames addr (+0x3C):", None)
        )
        self.label_2.setText(QCoreApplication.translate("EntityWidget", "Raw:", None))

    # retranslateUi
