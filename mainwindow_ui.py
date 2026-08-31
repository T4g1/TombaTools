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
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QTableView,
    QTextEdit,
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

        self.horizontalLayout.addWidget(self.entitiesTableView)

        self.tabWidget.addTab(self.tab_entities, "")
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
