# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OSGCreatePulseDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OSGCreatePulseDialog(object):
    def setupUi(self, OSGCreatePulseDialog):
        OSGCreatePulseDialog.setObjectName("OSGCreatePulseDialog")
        OSGCreatePulseDialog.resize(350, 200)
        self.centralwidget = QtWidgets.QWidget(OSGCreatePulseDialog)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.comboBoxUnit = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxUnit.setEditable(False)
        self.comboBoxUnit.setObjectName("comboBoxUnit")
        self.gridLayout.addWidget(self.comboBoxUnit, 3, 1, 1, 1)
        self.labelDuration = QtWidgets.QLabel(self.centralwidget)
        self.labelDuration.setObjectName("labelDuration")
        self.gridLayout.addWidget(self.labelDuration, 1, 0, 1, 1)
        self.comboBoxResolution = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxResolution.setEditable(False)
        self.comboBoxResolution.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContentsOnFirstShow)
        self.comboBoxResolution.setObjectName("comboBoxResolution")
        self.comboBoxResolution.addItem("")
        self.comboBoxResolution.addItem("")
        self.comboBoxResolution.addItem("")
        self.gridLayout.addWidget(self.comboBoxResolution, 0, 1, 1, 1)
        self.comboBoxType = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxType.setEditable(False)
        self.comboBoxType.setObjectName("comboBoxType")
        self.comboBoxType.addItem("")
        self.comboBoxType.addItem("")
        self.comboBoxType.addItem("")
        self.gridLayout.addWidget(self.comboBoxType, 2, 1, 1, 1)
        self.labelResolution = QtWidgets.QLabel(self.centralwidget)
        self.labelResolution.setObjectName("labelResolution")
        self.gridLayout.addWidget(self.labelResolution, 0, 0, 1, 1)
        self.labelUnit = QtWidgets.QLabel(self.centralwidget)
        self.labelUnit.setObjectName("labelUnit")
        self.gridLayout.addWidget(self.labelUnit, 3, 0, 1, 1)
        self.labelType = QtWidgets.QLabel(self.centralwidget)
        self.labelType.setObjectName("labelType")
        self.gridLayout.addWidget(self.labelType, 2, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.doubleSpinBoxDuration = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBoxDuration.setMaximum(400.0)
        self.doubleSpinBoxDuration.setObjectName("doubleSpinBoxDuration")
        self.gridLayout.addWidget(self.doubleSpinBoxDuration, 1, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        OSGCreatePulseDialog.setCentralWidget(self.centralwidget)

        self.retranslateUi(OSGCreatePulseDialog)
        QtCore.QMetaObject.connectSlotsByName(OSGCreatePulseDialog)

    def retranslateUi(self, OSGCreatePulseDialog):
        _translate = QtCore.QCoreApplication.translate
        OSGCreatePulseDialog.setWindowTitle(_translate("OSGCreatePulseDialog", "Create Pulse"))
        self.labelDuration.setText(_translate("OSGCreatePulseDialog", "Duration:"))
        self.comboBoxResolution.setItemText(0, _translate("OSGCreatePulseDialog", "16 khz"))
        self.comboBoxResolution.setItemText(1, _translate("OSGCreatePulseDialog", "8khz"))
        self.comboBoxResolution.setItemText(2, _translate("OSGCreatePulseDialog", "4 khz"))
        self.comboBoxType.setItemText(0, _translate("OSGCreatePulseDialog", "Acceleration"))
        self.comboBoxType.setItemText(1, _translate("OSGCreatePulseDialog", "Velocity"))
        self.comboBoxType.setItemText(2, _translate("OSGCreatePulseDialog", "Way"))
        self.labelResolution.setText(_translate("OSGCreatePulseDialog", "Resolution:"))
        self.labelUnit.setText(_translate("OSGCreatePulseDialog", "Unit:"))
        self.labelType.setText(_translate("OSGCreatePulseDialog", "Type:"))
        self.doubleSpinBoxDuration.setSuffix(_translate("OSGCreatePulseDialog", " ms"))
