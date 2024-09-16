from PyQt5 import QtCore, QtGui, QtWidgets
from def_clock import ClockWidget
from def_dataframes import DataFrameOperations
from def_dropDownBox import DropDownBoxOperations
from def_file import FileOperations
from def_menu import MenuOperations
from def_metrics import TradingMetrics
from def_ratings import RatingOperations
from def_widgets import WidgetOperations
from def_windows import WindowOperations

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 800)

        # Initialize csv_file_path here
        self.csv_file_path = "m1.csv"  # Set this to your desired CSV file path

        # Craete Empty CSV file
        FileOperations.create_empty_csv(self.csv_file_path)

        # Create an instance of WindowOperations
        self.window_operations = WindowOperations(MainWindow)  # Pass the main window as the parent

        # Now pass the overviewTab to FileOperations
        self.file_operations = FileOperations(self.window_operations, self.csv_file_path)
        MainWindow.setStyleSheet("""
QMainWindow {
    background-color: #001f3f;
}

QLabel {
    color: #ffffff;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QFrame {
    background-color: #002f5f;
    border: 1px solid #00ff00;
    border-radius: 5px;
}

QListWidget {
    background-color: #001f3f;
    color: #ffffff;
    border: 1px solid #00ff00;
    font-family: 'Consolas', 'Courier New', monospace;
}

QListWidget::item {
    border-bottom: 1px solid #00ff00;
    padding: 2px;
}

QScrollBar:vertical {
    border: 1px solid #00ff00;
    background: #001f3f;
    width: 15px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #00ff00;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: 1px solid #00ff00;
    background: #001f3f;
    height: 15px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}

QMenuBar {
    background-color: #001f3f;
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #00ff00;
    color: #001f3f;
}

QMenu {
    background-color: #001f3f;
    color: #ffffff;
}

QMenu::item:selected {
    background-color: #00ff00;
    color: #001f3f;
}
""")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.japanClock = QtWidgets.QLCDNumber(self.centralwidget)
        self.japanClock.setObjectName("japanClock")
        self.gridLayout.addWidget(self.japanClock, 0, 0, 1, 1)

        self.japanLabel = QtWidgets.QLabel(self.centralwidget)
        self.japanLabel.setObjectName("japanLabel")
        self.gridLayout.addWidget(self.japanLabel, 1, 0, 1, 1)

        self.australiaClock = QtWidgets.QLCDNumber(self.centralwidget)
        self.australiaClock.setObjectName("australiaClock")
        self.gridLayout.addWidget(self.australiaClock, 0, 1, 1, 1)

        self.australiaLabel = QtWidgets.QLabel(self.centralwidget)
        self.australiaLabel.setObjectName("australiaLabel")
        self.gridLayout.addWidget(self.australiaLabel, 1, 1, 1, 1)

        self.germanyClock = QtWidgets.QLCDNumber(self.centralwidget)
        self.germanyClock.setObjectName("germanyClock")
        self.gridLayout.addWidget(self.germanyClock, 0, 2, 1, 1)

        self.germanyLabel = QtWidgets.QLabel(self.centralwidget)
        self.germanyLabel.setObjectName("germanyLabel")
        self.gridLayout.addWidget(self.germanyLabel, 1, 2, 1, 1)

        self.londonClock = QtWidgets.QLCDNumber(self.centralwidget)
        self.londonClock.setObjectName("londonClock")
        self.gridLayout.addWidget(self.londonClock, 0, 3, 1, 1)

        self.londonLabel = QtWidgets.QLabel(self.centralwidget)
        self.londonLabel.setObjectName("londonLabel")
        self.gridLayout.addWidget(self.londonLabel, 1, 3, 1, 1)

        self.newyorkClock = QtWidgets.QLCDNumber(self.centralwidget)
        self.newyorkClock.setObjectName("newyorkClock")
        self.gridLayout.addWidget(self.newyorkClock, 0, 4, 1, 1)

        self.newyorkLabel = QtWidgets.QLabel(self.centralwidget)
        self.newyorkLabel.setObjectName("newyorkLabel")
        self.gridLayout.addWidget(self.newyorkLabel, 1, 4, 1, 1)

        self.sanfransiscoClock = QtWidgets.QLCDNumber(self.centralwidget)
        self.sanfransiscoClock.setObjectName("sanfransiscoClock")
        self.gridLayout.addWidget(self.sanfransiscoClock, 0, 5, 1, 1)

        self.sanfransiscoLabel = QtWidgets.QLabel(self.centralwidget)
        self.sanfransiscoLabel.setObjectName("sanfransiscoLabel")
        self.gridLayout.addWidget(self.sanfransiscoLabel, 1, 5, 1, 1)

        spacerItem = QtWidgets.QSpacerItem(1516, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 6)

        self.startDateLabel = QtWidgets.QLabel(self.centralwidget)
        self.startDateLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.startDateLabel.setObjectName("startDateLabel")
        self.gridLayout.addWidget(self.startDateLabel, 3, 0, 1, 1)

        self.dateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.gridLayout.addWidget(self.dateEdit, 3, 1, 1, 2)

        self.metricsView = QtWidgets.QColumnView(self.centralwidget)
        self.metricsView.setEnabled(True)
        self.metricsView.setObjectName("metricsView")
        self.gridLayout.addWidget(self.metricsView, 7, 0, 1, 6)

        self.dateEdit_2 = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dateEdit_2.setObjectName("dateEdit_2")
        self.gridLayout.addWidget(self.dateEdit_2, 3, 4, 1, 2)

        self.sectorLabel = QtWidgets.QLabel(self.centralwidget)
        self.sectorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.sectorLabel.setObjectName("sectorLabel")
        self.gridLayout.addWidget(self.sectorLabel, 4, 0, 1, 1)

        self.sectorComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.sectorComboBox.setCurrentText("")
        self.sectorComboBox.setObjectName("sectorComboBox")
        self.gridLayout.addWidget(self.sectorComboBox, 4, 1, 1, 2)

        self.tradesView = QtWidgets.QColumnView(self.centralwidget)
        self.tradesView.setObjectName("tradesView")
        self.gridLayout.addWidget(self.tradesView, 8, 0, 1, 6)

        self.endDateLabel = QtWidgets.QLabel(self.centralwidget)
        self.endDateLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.endDateLabel.setObjectName("endDateLabel")
        self.gridLayout.addWidget(self.endDateLabel, 3, 3, 1, 1)

        spacerItem1 = QtWidgets.QSpacerItem(1516, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 0, 1, 6)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.overviewTab = QtWidgets.QWidget()
        self.overviewTab.setObjectName("overView")
        self.tabWidget.addTab(self.overviewTab, "")

        self.metricsView1 = QtWidgets.QWidget()
        self.metricsView1.setObjectName("metricsView1")
        self.tabWidget.addTab(self.metricsView1, "")

        self.chart1View = QtWidgets.QWidget()
        self.chart1View.setObjectName("chart1View")
        self.tabWidget.addTab(self.chart1View, "")

        self.chart2Tab = QtWidgets.QWidget()
        self.chart2Tab.setObjectName("chart2Tab")
        self.tabWidget.addTab(self.chart2Tab, "")

        self.gridLayout.addWidget(self.tabWidget, 5, 0, 1, 6)
        self.marketLabel = QtWidgets.QLabel(self.centralwidget)
        self.marketLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.marketLabel.setObjectName("marketLabel")

        self.gridLayout.addWidget(self.marketLabel, 4, 3, 1, 1)
        self.marketComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.marketComboBox.setObjectName("marketComboBox")

        self.gridLayout.addWidget(self.marketComboBox, 4, 4, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1537, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionUpdate = QtWidgets.QAction(MainWindow)
        self.actionUpdate.setObjectName("actionUpdate")
        self.actionDelete_File = QtWidgets.QAction(MainWindow)
        self.actionDelete_File.setObjectName("actionDelete_File")

        self.actionVersion = QtWidgets.QAction(MainWindow)
        self.actionVersion.setObjectName("actionVersion")

        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")

        self.menuFile.addAction("Update File", self.file_operations.updateFile,"F1")
        self.menuFile.addAction("Delete File", self.file_operations.deleteFile, "F2")
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addAction(MenuOperations.show_version(self))
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.australiaLabel.setText(_translate("MainWindow", "Australia"))
        self.germanyLabel.setText(_translate("MainWindow", "Germany"))
        self.newyorkLabel.setText(_translate("MainWindow", "New York"))
        self.japanLabel.setText(_translate("MainWindow", "Japan"))
        self.sanfransiscoLabel.setText(_translate("MainWindow", "San Fransico"))
        self.londonLabel.setText(_translate("MainWindow", "London"))
        self.startDateLabel.setText(_translate("MainWindow", "Start Date"))
        self.sectorLabel.setText(_translate("MainWindow", "Sector"))
        self.endDateLabel.setText(_translate("MainWindow", "End Date"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.overviewTab), _translate("MainWindow", "Overview"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.metricsView1), _translate("MainWindow", "Metrics"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.chart1View), _translate("MainWindow", "Chart1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.chart2Tab), _translate("MainWindow", "Chart2"))
        self.marketLabel.setText(_translate("MainWindow", "Market"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionUpdate.setText(_translate("MainWindow", "Update"))
        self.actionDelete_File.setText(_translate("MainWindow", "Delete File"))
        self.actionVersion.setText(_translate("MainWindow", "Version"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
