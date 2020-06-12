# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1517, 1082)
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        MainWindow.setStyleSheet("QPushButton {\n"
"  background-color: #d9ddff;\n"
"  border: 1px solid #32414B;\n"
"  border-radius: 5px;\n"
"  padding: 3px;\n"
"  color: #000000\n"
"}\n"
"\n"
"\n"
"QPushButton:pressed {\n"
"  background-color: #6270f5;\n"
"}\n"
"\n"
"QPushButton:pressed:hover {\n"
"   background-color: #6270f5;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"  border: 1px solid #148CD2;\n"
"  background-color: #b8bfff;\n"
"}\n"
"\n"
"QPushButton:selected {\n"
"  background: #1464A0;\n"
"  color: #32414B;\n"
"}\n"
"\n"
"QPushButton:focus {\n"
"  border: 1px solid #1464A0;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"  background-color: #6270f5;\n"
"}\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"QComboBox {\n"
"  background-color: #d9ddff;\n"
"  border: 1px solid #32414B;\n"
"  border-radius: 5px;\n"
"  selection-background-color: #1464A0;\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"  border: 1px solid #32414B;\n"
"  border-radius: 2px;\n"
"  background-color: #d9ddff;\n"
"  selection-background-color: #1464A0;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setSizeIncrement(QtCore.QSize(1, 1))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.headWidget = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.headWidget.sizePolicy().hasHeightForWidth())
        self.headWidget.setSizePolicy(sizePolicy)
        self.headWidget.setMinimumSize(QtCore.QSize(0, 150))
        self.headWidget.setObjectName("headWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.headWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.headLayout = QtWidgets.QHBoxLayout()
        self.headLayout.setSpacing(10)
        self.headLayout.setObjectName("headLayout")
        self.logoLayout = QtWidgets.QVBoxLayout()
        self.logoLayout.setContentsMargins(10, 10, -1, -1)
        self.logoLayout.setObjectName("logoLayout")
        self.logo = QtWidgets.QLabel(self.headWidget)
        self.logo.setText("")
        self.logo.setObjectName("logo")
        self.logoLayout.addWidget(self.logo)
        self.headLayout.addLayout(self.logoLayout)
        self.groupBox_imexport = QtWidgets.QGroupBox(self.headWidget)
        self.groupBox_imexport.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox_imexport.setObjectName("groupBox_imexport")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_imexport)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.imexportLayout = QtWidgets.QVBoxLayout()
        self.imexportLayout.setContentsMargins(7, -1, 7, -1)
        self.imexportLayout.setSpacing(0)
        self.imexportLayout.setObjectName("imexportLayout")
        self.btn_load = QtWidgets.QPushButton(self.groupBox_imexport)
        self.btn_load.setMaximumSize(QtCore.QSize(160, 16777215))
        self.btn_load.setObjectName("btn_load")
        self.imexportLayout.addWidget(self.btn_load)
        self.btn_save = QtWidgets.QPushButton(self.groupBox_imexport)
        self.btn_save.setMaximumSize(QtCore.QSize(160, 16777215))
        self.btn_save.setObjectName("btn_save")
        self.imexportLayout.addWidget(self.btn_save)
        self.horizontalLayout_2.addLayout(self.imexportLayout)
        self.headLayout.addWidget(self.groupBox_imexport)
        self.groupBox_Evaluate = QtWidgets.QGroupBox(self.headWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_Evaluate.sizePolicy().hasHeightForWidth())
        self.groupBox_Evaluate.setSizePolicy(sizePolicy)
        self.groupBox_Evaluate.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox_Evaluate.setObjectName("groupBox_Evaluate")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_Evaluate)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.compareLayout = QtWidgets.QVBoxLayout()
        self.compareLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.compareLayout.setContentsMargins(7, -1, 7, -1)
        self.compareLayout.setSpacing(0)
        self.compareLayout.setObjectName("compareLayout")
        self.pushButton = QtWidgets.QPushButton(self.groupBox_Evaluate)
        self.pushButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setSizeIncrement(QtCore.QSize(0, 0))
        self.pushButton.setObjectName("pushButton")
        self.compareLayout.addWidget(self.pushButton)
        self.comboBox = QtWidgets.QComboBox(self.groupBox_Evaluate)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.compareLayout.addWidget(self.comboBox)
        self.horizontalLayout_3.addLayout(self.compareLayout)
        self.headLayout.addWidget(self.groupBox_Evaluate)
        self.groupBox_Tools = QtWidgets.QGroupBox(self.headWidget)
        self.groupBox_Tools.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox_Tools.setObjectName("groupBox_Tools")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_Tools)
        self.horizontalLayout_4.setSpacing(7)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_Tools = QtWidgets.QVBoxLayout()
        self.verticalLayout_Tools.setContentsMargins(7, -1, 7, -1)
        self.verticalLayout_Tools.setSpacing(0)
        self.verticalLayout_Tools.setObjectName("verticalLayout_Tools")
        self.btn_tool_cursor = QtWidgets.QPushButton(self.groupBox_Tools)
        self.btn_tool_cursor.setCheckable(True)
        self.btn_tool_cursor.setChecked(False)
        self.btn_tool_cursor.setFlat(False)
        self.btn_tool_cursor.setObjectName("btn_tool_cursor")
        self.verticalLayout_Tools.addWidget(self.btn_tool_cursor)
        self.btn_tool_edit = QtWidgets.QPushButton(self.groupBox_Tools)
        self.btn_tool_edit.setCheckable(True)
        self.btn_tool_edit.setObjectName("btn_tool_edit")
        self.verticalLayout_Tools.addWidget(self.btn_tool_edit)
        self.horizontalLayout_4.addLayout(self.verticalLayout_Tools)
        self.headLayout.addWidget(self.groupBox_Tools)
        self.groupBox_PLC = QtWidgets.QGroupBox(self.headWidget)
        self.groupBox_PLC.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox_PLC.setObjectName("groupBox_PLC")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox_PLC)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.plcLayout = QtWidgets.QVBoxLayout()
        self.plcLayout.setContentsMargins(7, -1, 7, -1)
        self.plcLayout.setObjectName("plcLayout")
        self.btn_submit_plc = QtWidgets.QPushButton(self.groupBox_PLC)
        self.btn_submit_plc.setObjectName("btn_submit_plc")
        self.plcLayout.addWidget(self.btn_submit_plc)
        self.horizontalLayout_5.addLayout(self.plcLayout)
        self.headLayout.addWidget(self.groupBox_PLC)
        self.pushButton_2 = QtWidgets.QPushButton(self.headWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.headLayout.addWidget(self.pushButton_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.headLayout.addItem(spacerItem)
        self.headLayout.setStretch(1, 1)
        self.headLayout.setStretch(2, 1)
        self.headLayout.setStretch(3, 1)
        self.headLayout.setStretch(4, 1)
        self.headLayout.setStretch(6, 1)
        self.horizontalLayout.addLayout(self.headLayout)
        self.verticalLayout_2.addWidget(self.headWidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mplWidget = QtWidgets.QWidget(self.centralwidget)
        self.mplWidget.setStyleSheet("background-color: white")
        self.mplWidget.setObjectName("mplWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.mplWidget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.mplLayout = QtWidgets.QVBoxLayout()
        self.mplLayout.setSpacing(0)
        self.mplLayout.setObjectName("mplLayout")
        self.verticalLayout_4.addLayout(self.mplLayout)
        self.verticalLayout.addWidget(self.mplWidget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1517, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.actionExit.triggered['bool'].connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_imexport.setTitle(_translate("MainWindow", "Import/Export"))
        self.btn_load.setText(_translate("MainWindow", "CSV Importieren"))
        self.btn_save.setText(_translate("MainWindow", "CSV Exportieren"))
        self.groupBox_Evaluate.setTitle(_translate("MainWindow", "Auswerten"))
        self.pushButton.setText(_translate("MainWindow", "Vergleiche Soll-Ist"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Überlappend"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Untereinander"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Übereinander"))
        self.groupBox_Tools.setTitle(_translate("MainWindow", "Werkzeuge"))
        self.btn_tool_cursor.setText(_translate("MainWindow", "Cursor"))
        self.btn_tool_edit.setText(_translate("MainWindow", "Bearbeiten"))
        self.groupBox_PLC.setTitle(_translate("MainWindow", "PLC"))
        self.btn_submit_plc.setText(_translate("MainWindow", "Lade in PLC"))
        self.pushButton_2.setText(_translate("MainWindow", "PushButton"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
