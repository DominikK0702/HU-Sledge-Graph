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
        OSGCreatePulseDialog.resize(380, 150)
        self.gridLayout_2 = QtWidgets.QGridLayout(OSGCreatePulseDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.labelType = QtWidgets.QLabel(OSGCreatePulseDialog)
        self.labelType.setObjectName("labelType")
        self.gridLayout.addWidget(self.labelType, 2, 0, 1, 1)
        self.comboBoxType = QtWidgets.QComboBox(OSGCreatePulseDialog)
        self.comboBoxType.setObjectName("comboBoxType")
        self.comboBoxType.addItem("")
        self.comboBoxType.addItem("")
        self.comboBoxType.addItem("")
        self.gridLayout.addWidget(self.comboBoxType, 2, 1, 1, 1)
        self.labelResolution = QtWidgets.QLabel(OSGCreatePulseDialog)
        self.labelResolution.setObjectName("labelResolution")
        self.gridLayout.addWidget(self.labelResolution, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(OSGCreatePulseDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.comboBoxResolution = QtWidgets.QComboBox(OSGCreatePulseDialog)
        self.comboBoxResolution.setObjectName("comboBoxResolution")
        self.comboBoxResolution.addItem("")
        self.comboBoxResolution.addItem("")
        self.comboBoxResolution.addItem("")
        self.gridLayout.addWidget(self.comboBoxResolution, 0, 1, 1, 1)
        self.labelDuration = QtWidgets.QLabel(OSGCreatePulseDialog)
        self.labelDuration.setObjectName("labelDuration")
        self.gridLayout.addWidget(self.labelDuration, 1, 0, 1, 1)
        self.doubleSpinBoxDuration = QtWidgets.QDoubleSpinBox(OSGCreatePulseDialog)
        self.doubleSpinBoxDuration.setSpecialValueText("")
        self.doubleSpinBoxDuration.setMaximum(399.0)
        self.doubleSpinBoxDuration.setObjectName("doubleSpinBoxDuration")
        self.gridLayout.addWidget(self.doubleSpinBoxDuration, 1, 1, 1, 1)
        self.labelUnit = QtWidgets.QLabel(OSGCreatePulseDialog)
        self.labelUnit.setObjectName("labelUnit")
        self.gridLayout.addWidget(self.labelUnit, 3, 0, 1, 1)
        self.comboBoxUnit = QtWidgets.QComboBox(OSGCreatePulseDialog)
        self.comboBoxUnit.setObjectName("comboBoxUnit")
        self.comboBoxUnit.addItem("")
        self.comboBoxUnit.addItem("")
        self.gridLayout.addWidget(self.comboBoxUnit, 3, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setRowStretch(3, 1)
        self.gridLayout.setRowStretch(4, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(OSGCreatePulseDialog)
        QtCore.QMetaObject.connectSlotsByName(OSGCreatePulseDialog)

    def retranslateUi(self, OSGCreatePulseDialog):
        _translate = QtCore.QCoreApplication.translate
        OSGCreatePulseDialog.setWindowTitle(_translate("OSGCreatePulseDialog", "Create Pulse"))
        self.labelType.setText(_translate("OSGCreatePulseDialog", "Type:"))
        self.comboBoxType.setItemText(0, _translate("OSGCreatePulseDialog", "Acceleration"))
        self.comboBoxType.setItemText(1, _translate("OSGCreatePulseDialog", "Way"))
        self.comboBoxType.setItemText(2, _translate("OSGCreatePulseDialog", "Velocity"))
        self.labelResolution.setText(_translate("OSGCreatePulseDialog", "Resolution:"))
        self.comboBoxResolution.setItemText(0, _translate("OSGCreatePulseDialog", "16 khz"))
        self.comboBoxResolution.setItemText(1, _translate("OSGCreatePulseDialog", "8 khz"))
        self.comboBoxResolution.setItemText(2, _translate("OSGCreatePulseDialog", "4 khz"))
        self.labelDuration.setText(_translate("OSGCreatePulseDialog", "Duration:"))
        self.doubleSpinBoxDuration.setSuffix(_translate("OSGCreatePulseDialog", " ms"))
        self.labelUnit.setText(_translate("OSGCreatePulseDialog", "Unit:"))
        self.comboBoxUnit.setItemText(0, _translate("OSGCreatePulseDialog", "[G]"))
        self.comboBoxUnit.setItemText(1, _translate("OSGCreatePulseDialog", "[m/s²]"))
