from ui.QtInfo import Ui_QtInfo
from ui.InfoDialog import Ui_InfoDialog
from ui.OSGCreatePulseDialog import Ui_OSGCreatePulseDialog
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow


def show_qtinfo(parent):
    qtinfo = QMainWindow(parent)
    qtinfo_ui = Ui_QtInfo()
    qtinfo_ui.setupUi(qtinfo)
    qtinfo_ui.label.setPixmap(QtGui.QPixmap('./assets/qt.png'))
    qtinfo.show()


def show_info(parent):
    info = QMainWindow(parent)
    info_ui = Ui_InfoDialog()
    info_ui.setupUi(info)
    info.show()


def show_create_pulse(parent, handle_create_pulse_finished):
    create_pulse = QMainWindow(parent)
    create_pulse_ui = Ui_OSGCreatePulseDialog()
    create_pulse_ui.setupUi(create_pulse)
    ##
    resolutions = ["16kHz", "12kHz", "8kHz", "4kHz"]
    max_datapoints = 3000
    max_duration = max_datapoints / int(resolutions[0].split('kHz')[0])

    units = [
        ["[G]", "[m/s²]"],
        ["[m/s]", "[km/h]"],
        ["[mm]", "[cm]", "[m]"]
    ]

    def type_changed(index):
        create_pulse_ui.comboBoxUnit.clear()
        create_pulse_ui.comboBoxUnit.addItems(units[index])

    def resolution_changed(index):
        max_duration = max_datapoints / int(resolutions[index].split('kHz')[0])
        create_pulse_ui.labelDuration.setText(f"Duration (max: {max_duration}ms):")
        create_pulse_ui.doubleSpinBoxDuration.setMaximum(max_duration)
        create_pulse_ui.doubleSpinBoxDuration.setValue(max_duration)

    create_pulse.setWindowIcon(QtGui.QIcon("./assets/Slice1.png"))

    create_pulse_ui.comboBoxResolution.clear()
    create_pulse_ui.comboBoxResolution.addItems(resolutions)

    create_pulse_ui.labelDuration.setText(f"Duration (max: {max_duration}ms):")
    create_pulse_ui.doubleSpinBoxDuration.setMaximum(max_duration)
    create_pulse_ui.doubleSpinBoxDuration.setValue(max_duration)

    create_pulse_ui.comboBoxUnit.addItems(units[0])
    create_pulse_ui.comboBoxType.currentIndexChanged.connect(type_changed)
    create_pulse_ui.comboBoxResolution.currentIndexChanged.connect(resolution_changed)

    create_pulse_ui.buttonBox.accepted.connect(lambda: handle_create_pulse_finished(
        resolutions[create_pulse_ui.comboBoxResolution.currentIndex()],
        create_pulse_ui.doubleSpinBoxDuration.value(),
        create_pulse_ui.comboBoxType.currentText(),
        units[create_pulse_ui.comboBoxType.currentIndex()][create_pulse_ui.comboBoxUnit.currentIndex()],
        max_datapoints,
        create_pulse.close
    ))

    create_pulse.show()
