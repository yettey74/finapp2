from PyQt5.QtWidgets import (QAction, QMessageBox)
from def_file import FileOperations

class MenuOperations:
    def __init__(self, file_operations):
        self.file_operations = file_operations  # Store the FileOperations instance

    def setupMenuBar(self, main_window):
        menubar = main_window.menuBar()
        fileMenu = menubar.addMenu('File')
        
        updateAction = QAction('Update File', main_window)
        updateAction.setShortcut('F1')
        updateAction.triggered.connect(self.file_operations.updateFile)  # Connect to the instance method
        fileMenu.addAction(updateAction)

        deleteAction = QAction('Delete File', main_window)
        deleteAction.setShortcut('F2')
        deleteAction.triggered.connect(self.file_operations.deleteFile)
        fileMenu.addAction(deleteAction)

        optionsAction = QAction('Options', main_window)
        optionsAction.triggered.connect(self.show_options)  # Connect to the method in MenuOperations
        fileMenu.addAction(optionsAction)

        helpMenu = menubar.addMenu('Help')
        versionAction = QAction('Version', main_window)
        versionAction.triggered.connect(lambda: self.show_version(main_window))  # Pass main_window
        helpMenu.addAction(versionAction)

    def show_options(self):
        # This is a placeholder for the options dialog
        QMessageBox.information(None, "Options", "Options dialog not implemented yet.")

    def show_version(self):
        VERSION = "0.0.0.10.0"  # Update this as needed
        QMessageBox.information(None, "Version", f"FinApp version {VERSION}")