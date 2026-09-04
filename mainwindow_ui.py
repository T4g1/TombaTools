# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
    QAction,
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
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.actionConnect = QAction(MainWindow)
        self.actionConnect.setObjectName("actionConnect")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_entities = QWidget()
        self.tab_entities.setObjectName("tab_entities")
        self.horizontalLayout = QHBoxLayout(self.tab_entities)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.entitiesTableView = QTableView(self.tab_entities)
        self.entitiesTableView.setObjectName("entitiesTableView")
        self.entitiesTableView.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.entitiesTableView.setSortingEnabled(True)

        self.horizontalLayout.addWidget(self.entitiesTableView)

        self.entity_viewer = QWidget(self.tab_entities)
        self.entity_viewer.setObjectName("entity_viewer")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.entity_viewer.sizePolicy().hasHeightForWidth()
        )
        self.entity_viewer.setSizePolicy(sizePolicy)
        self.entity_viewer_layout = QVBoxLayout(self.entity_viewer)
        self.entity_viewer_layout.setObjectName("entity_viewer_layout")

        self.horizontalLayout.addWidget(self.entity_viewer)

        self.tabWidget.addTab(self.tab_entities, "")
        self.tab_vram = QWidget()
        self.tab_vram.setObjectName("tab_vram")
        self.verticalLayout = QVBoxLayout(self.tab_vram)
        self.verticalLayout.setObjectName("verticalLayout")
        self.vram_menu = QHBoxLayout()
        self.vram_menu.setObjectName("vram_menu")
        self.label = QLabel(self.tab_vram)
        self.label.setObjectName("label")

        self.vram_menu.addWidget(self.label)

        self.mode = QComboBox(self.tab_vram)
        self.mode.addItem("")
        self.mode.addItem("")
        self.mode.addItem("")
        self.mode.setObjectName("mode")

        self.vram_menu.addWidget(self.mode)

        self.clut_layout = QVBoxLayout()
        self.clut_layout.setObjectName("clut_layout")
        self.clut_x_layout = QHBoxLayout()
        self.clut_x_layout.setObjectName("clut_x_layout")
        self.clut_x_label = QLabel(self.tab_vram)
        self.clut_x_label.setObjectName("clut_x_label")

        self.clut_x_layout.addWidget(self.clut_x_label)

        self.clut_x = QSpinBox(self.tab_vram)
        self.clut_x.setObjectName("clut_x")
        self.clut_x.setMaximum(2048)
        self.clut_x.setSingleStep(16)

        self.clut_x_layout.addWidget(self.clut_x)

        self.clut_layout.addLayout(self.clut_x_layout)

        self.clut_y_layout = QHBoxLayout()
        self.clut_y_layout.setObjectName("clut_y_layout")
        self.clut_y_label = QLabel(self.tab_vram)
        self.clut_y_label.setObjectName("clut_y_label")

        self.clut_y_layout.addWidget(self.clut_y_label)

        self.clut_y = QSpinBox(self.tab_vram)
        self.clut_y.setObjectName("clut_y")
        self.clut_y.setMaximum(511)

        self.clut_y_layout.addWidget(self.clut_y)

        self.clut_layout.addLayout(self.clut_y_layout)

        self.vram_menu.addLayout(self.clut_layout)

        self.verticalLayout.addLayout(self.vram_menu)

        self.tabWidget.addTab(self.tab_vram, "")
        self.tab_transitions = QWidget()
        self.tab_transitions.setObjectName("tab_transitions")
        self.tabWidget.addTab(self.tab_transitions, "")
        self.tab_log = QWidget()
        self.tab_log.setObjectName("tab_log")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_log)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.logTextBox = QTextEdit(self.tab_log)
        self.logTextBox.setObjectName("logTextBox")

        self.horizontalLayout_3.addWidget(self.logTextBox)

        self.tabWidget.addTab(self.tab_log, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuEmulator = QMenu(self.menubar)
        self.menuEmulator.setObjectName("menuEmulator")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuEmulator.menuAction())
        self.menuEmulator.addAction(self.actionConnect)
        self.menuEmulator.addSeparator()
        self.menuEmulator.addAction(self.actionQuit)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Tomba! Tools", None)
        )
        self.actionConnect.setText(
            QCoreApplication.translate("MainWindow", "Connect", None)
        )
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", "Quit", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_entities),
            QCoreApplication.translate("MainWindow", "Entities", None),
        )
        self.label.setText(
            QCoreApplication.translate("MainWindow", "Color mode:", None)
        )
        self.mode.setItemText(
            0,
            QCoreApplication.translate(
                "MainWindow", "16bit Texture (Direct Color)", None
            ),
        )
        self.mode.setItemText(
            1,
            QCoreApplication.translate(
                "MainWindow", "8bit Texture (256 Color Palette)", None
            ),
        )
        self.mode.setItemText(
            2,
            QCoreApplication.translate(
                "MainWindow", "4bit Texture (16 Color Palette)", None
            ),
        )

        self.clut_x_label.setText(
            QCoreApplication.translate("MainWindow", "CLUT X:", None)
        )
        self.clut_y_label.setText(
            QCoreApplication.translate("MainWindow", "CLUT Y", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_vram),
            QCoreApplication.translate("MainWindow", "VRAM", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_transitions),
            QCoreApplication.translate("MainWindow", "Transitions", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_log),
            QCoreApplication.translate("MainWindow", "Log", None),
        )
        self.menuEmulator.setTitle(
            QCoreApplication.translate("MainWindow", "Emulator", None)
        )

    # retranslateUi
