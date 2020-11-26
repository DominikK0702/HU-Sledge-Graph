from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem
from OSGGraphicsView import OSGPulseGraphicsView
from ui.OSGMainWindow import Ui_OSGMainWindow
from ui.OSGCreatePulseDialog import Ui_OSGCreatePulseDialog
from OSGPLC import OSGPLC
from OSGPLCConverter import OSGSinamicsConverter
from OSGPulse import OSGPulseLibrary
import OSGDialogs
from loguru import logger


class OSGMainWindow(QMainWindow, Ui_OSGMainWindow):
    def __init__(self, app, *args, **kwargs):
        super(OSGMainWindow, self).__init__(*args, **kwargs)
        self.application = app
        self.setupUi(self)
        self.setupWindow()
        self.tool_tab_pulse = OSGMWPulseToolTab(self)
        self.pulse_library = OSGPulseLibrary()
        self.pulseTree = OSGMWPulseTree(self)
        self.pulseGraphicsView = OSGPulseGraphicsView(self.graphicsView)
        self.plc = OSGPLC(self)
        self.setupPlcEvents()
        self.converter = OSGSinamicsConverter(self)
        self.setupConverterEvents()
        self.show()

    def setupWindow(self):
        self.setWindowMonitor()
        self.setWindowIcon(QIcon(self.application.configmanager._config['APP'].get('window_icon')))
        self.logo.setPixmap(QPixmap(self.application.configmanager._config['APP'].get('logo')))
        if self.application.configmanager._config['APP'].getboolean('always_top'): self.setWindowFlag(
            Qt.WindowStaysOnTopHint)
        if self.application.configmanager._config['APP'].getboolean('maximized'): self.showMaximized()
        if self.application.configmanager._config['APP'].getboolean('fullscreen'): self.showFullScreen()
        self.setupStrings()

        self.connectComponents()

    def setupPlcEvents(self):
        self.plc.events.language_changed.connect(self.setupStrings)

    def setupConverterEvents(self):
        pass

    def showMessage(self, message, duration=0):
        self.statusbar.showMessage(message, duration)

    def setWindowMonitor(self):
        display_id = self.application.configmanager._config['APP'].getint('monitor_nr')
        monitor = QDesktopWidget().screenGeometry(display_id)
        self.move(monitor.left(), monitor.top())

    def setupStrings(self):
        # Main Window Title
        self.setWindowTitle(self.application.configmanager.lang_get_string('title'))
        # Main Window Menu bar

    def set_current_pulseinfo(self, pulsdata):
        self.labelCurrentPulseNameValue.setText(pulsdata.get_name())
        self.labelCurrentPulseMaxValue.setText(str(pulsdata.get_max()) + ' G')
        self.labelCurrentPulseMinValue.setText(str(pulsdata.get_min()) + ' G')
        self.labelCurrentPulseDurationValue.setText(str(round(pulsdata.get_duration(), 2)) + ' ms')
        self.labelCurrentPulseResolutionValue.setText(str(pulsdata.get_resolution()) + ' hz')

    def connectComponents(self):
        self.actionAbout_Qt.triggered.connect(lambda: OSGDialogs.show_qtinfo(self))
        self.actionAbout.triggered.connect(lambda: OSGDialogs.show_info(self))

    def setPlcConnectionStatus(self, state):
        if state:
            self.labelPlcStatusValue.setText('connected')
            self.labelPlcStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['PLC'].get('color_connected')}")
        else:
            self.labelPlcStatusValue.setText('disconnected')
            self.labelPlcStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['PLC'].get('color_disconnected')}")

    def setConverterConnectionStatus(self, state):
        if state:
            self.labelConverterStatusValue.setText('connected')
            self.labelConverterStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['CONVERTER'].get('color_connected')}")
        else:
            self.labelConverterStatusValue.setText('disconnected')
            self.labelConverterStatusValue.setStyleSheet(
                f"color: #{self.application.configmanager._config['CONVERTER'].get('color_disconnected')}")


class OSGMWPulseTree:
    def __init__(self, mainwindow: OSGMainWindow):
        self.mainwindow = mainwindow
        self.cfgmanager = mainwindow.application.configmanager
        self.connect_components()

        self.mainwindow.treeWidget.headerItem().setText(0, "Name")
        self.mainwindow.treeWidget.headerItem().setText(1, "Duration [ms]")
        self.mainwindow.treeWidget.headerItem().setText(2, "Resolution [hz]")
        self.mainwindow.treeWidget.headerItem().setText(3, "Max [G]")
        self.mainwindow.treeWidget.headerItem().setText(4, "Min  [G]")
        self.mainwindow.treeWidget.headerItem().setText(5, "Description")

    def set_tree(self, pulselibrarys, parent=None):
        if parent is not None:
            root_item = parent
            for i in pulselibrarys:
                child_item = QTreeWidgetItem(root_item)
                child_item.setText(0, i.get_name())
                child_item.setText(1, str(i.get_duration()))
                child_item.setText(2, str(i.get_resolution()))
                child_item.setText(3, str(i.get_max()))
                child_item.setText(4, str(i.get_min()))
                child_item.setText(5, i.get_description())
                child_item.pulse_data = i
                root_item.addChild(child_item)
                if i.get_branches_count() > 0:
                    self.set_tree(i.get_branches(), child_item)
        else:
            if type(pulselibrarys) != type(list()):
                pulselibrarys = [pulselibrarys]
            for i in pulselibrarys:
                root_item = QTreeWidgetItem(self.mainwindow.treeWidget)
                root_item.setText(0, i.get_name())
                root_item.setText(1, str(i.get_duration()))
                root_item.setText(2, str(i.get_resolution()))
                root_item.setText(3, str(i.get_max()))
                root_item.setText(4, str(i.get_min()))
                root_item.setText(5, i.get_description())
                root_item.pulse_data = i
                self.mainwindow.treeWidget.insertTopLevelItem(0, root_item)

                if i.get_branches_count() > 0:
                    self.set_tree(i.get_branches(), root_item)

    def connect_components(self):
        self.mainwindow.treeWidget.itemClicked.connect(self.pulse_selected)
        self.mainwindow.treeWidget.show()
        self.mainwindow.groupBox_2.show()
        self.mainwindow.pushButtonTogglePulseLibrary.setText(u"►")

    def pulse_selected(self, item, column):
        self.mainwindow.pulse_graph.plot_pulse(*item.pulse_data.get_data())


class OSGMWPulseToolTab:
    def __init__(self, mainwindow: OSGMainWindow):
        self.mainwindow = mainwindow
        self.cfgmanager = mainwindow.application.configmanager
        self.create_pulse_ui = None
        self.create_pulse_mw = None
        self.connect_components()

    def connect_components(self):
        self.mainwindow.pushButtonImportPulse.clicked.connect(self.import_pulse)
        self.mainwindow.pushButtonTogglePulseLibrary.clicked.connect(self.toogle_pulse_library)
        self.mainwindow.pushButtonCreatePulse.clicked.connect(self.handle_create_pulse)

    def toogle_pulse_library(self):
        if self.mainwindow.treeWidget.isHidden():
            self.mainwindow.treeWidget.show()
            self.mainwindow.groupBox_2.show()
            self.mainwindow.pushButtonTogglePulseLibrary.setText(u"►")
        else:
            self.mainwindow.treeWidget.hide()
            self.mainwindow.groupBox_2.hide()
            self.mainwindow.pushButtonTogglePulseLibrary.setText(u"◄")

    def handle_create_pulse(self):
        resolutions = ["16kHz", "12kHz", "8kHz", "4kHz"]
        max_datapoints = 3000
        max_duration = max_datapoints / int(resolutions[0].split('kHz')[0])

        units = [
            ["[G]", "[m/s²]"],
            ["[m/s]", "[km/h]"],
            ["[mm]", "[cm]", "[m]"]
        ]

        def type_changed(index):
            self.create_pulse_ui.comboBoxUnit.clear()
            self.create_pulse_ui.comboBoxUnit.addItems(units[index])

        def resolution_changed(index):
            max_duration = max_datapoints / int(resolutions[index].split('kHz')[0])
            self.create_pulse_ui.labelDuration.setText(f"Duration (max: {max_duration}ms):")
            self.create_pulse_ui.doubleSpinBoxDuration.setMaximum(max_duration)
            self.create_pulse_ui.doubleSpinBoxDuration.setValue(max_duration)

        self.create_pulse_mw = QMainWindow()
        self.create_pulse_ui = Ui_OSGCreatePulseDialog()
        self.create_pulse_ui.setupUi(self.create_pulse_mw)
        self.create_pulse_mw.setWindowIcon(QIcon("./assets/Slice1.png"))

        self.create_pulse_ui.comboBoxResolution.clear()
        self.create_pulse_ui.comboBoxResolution.addItems(resolutions)

        self.create_pulse_ui.labelDuration.setText(f"Duration (max: {max_duration}ms):")
        self.create_pulse_ui.doubleSpinBoxDuration.setMaximum(max_duration)
        self.create_pulse_ui.doubleSpinBoxDuration.setValue(max_duration)

        self.create_pulse_ui.comboBoxUnit.addItems(units[0])
        self.create_pulse_ui.comboBoxType.currentIndexChanged.connect(type_changed)
        self.create_pulse_ui.comboBoxResolution.currentIndexChanged.connect(resolution_changed)

        self.create_pulse_ui.buttonBox.accepted.connect(lambda: self.handle_create_pulse_finished(
            resolutions[self.create_pulse_ui.comboBoxResolution.currentIndex()],
            self.create_pulse_ui.doubleSpinBoxDuration.value(),
            self.create_pulse_ui.comboBoxType.currentText(),
            units[self.create_pulse_ui.comboBoxType.currentIndex()][self.create_pulse_ui.comboBoxUnit.currentIndex()],
            max_datapoints
        ))

        self.create_pulse_mw.show()

    def handle_create_pulse_finished(self, resolution, duration, type, unit, maxpoints):
        self.create_pulse_mw.close()
        res = int(resolution.split('kHz')[0]) * 1e3
        x = [(i / res) for i in range(0, maxpoints)]
        y = [0.0 for i in range(len(x))]
        print(1)

    def import_pulse(self):
        logger.info('Import Pulse')
        filetypes = ["Pulse Library (*.opl)", "Pulse CSV (*.pcsv)"]
        options = QFileDialog.Options()
        fileName, fileType = QFileDialog.getOpenFileName(self.mainwindow,
                                                         self.cfgmanager.lang_get_string(
                                                             'filedialog_pulse_import_title'),
                                                         self.cfgmanager._config['PULSE'].get('import_file_dir'),
                                                         ";;".join(filetypes),
                                                         options=options)
        if fileName:
            logger.info(f"Pulse selected: {fileName}")
            if fileType == filetypes[0] and self.mainwindow.pulse_library.load_pulse_library(fileName):
                self.mainwindow.set_current_pulseinfo(self.mainwindow.pulse_library.current_pulse_data)
                logger.info('Imported Pulse library')
                self.mainwindow.pulseTree.set_tree(self.mainwindow.pulse_library.current_pulse_data)
            elif fileType == filetypes[1] and self.mainwindow.pulse_library.load_from_csv(fileName):
                logger.info('Imported Pulse CSV')
            else:
                logger.error('Importing Pulse failed.')
        else:
            logger.info('Import pulse canceled by user.')
