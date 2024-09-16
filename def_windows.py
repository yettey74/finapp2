import logging
from PyQt5.QtWidgets import ( QListWidget, QWidget, QLabel )

class WindowOperations(QWidget):  # Make sure it inherits from QWidget
       def __init__(self, parent=None):
              super().__init__(parent)  # Call the parent constructor
              self.createMessageWindow()  # Initialize the message window

       def createMessageWindow(self):
              logging.info("Creating messageWindow")
              self.messageWindow = QListWidget()  # Ensure this is set correctly
              self.messageWindow.setWordWrap(True)
              self.messageWindow.setSelectionMode(QListWidget.NoSelection)
              
              # Set a fixed height for 10 items
              self.messageWindow.setFixedHeight(200)  # Use a fixed pixel height instead
              
              logging.info(f"MessageWindow created and added to layout. Is visible: {self.messageWindow.isVisible()}")
              
       def updateOverviewTab(self, message):
              if self.messageWindow is not None:
                     self.messageWindow.addItem(message)
                     if self.messageWindow.count() > 1000:  # Limit to 1000 messages
                            self.messageWindow.takeItem(0)
                     self.messageWindow.scrollToBottom()
                     logging.info(f"Added message to message window: {message}")
              else:
                     logging.warning("Attempted to update message window, but it doesn't exist.")
       
class TraderWindow(QWidget):
 
       def createTraderWindow(self):
              logging.info("Creating traderWindow")
              self.traderWindow = QListWidget()
              self.traderWindow.setWordWrap(True)
              self.traderWindow.setSelectionMode(QListWidget.NoSelection)
              
              # Set a fixed height for 10 items
              self.traderWindow.setFixedHeight(200)  # Use a fixed pixel height instead
              
              logging.info(f"Trader Window created and added to layout. Is visible: {self.traderWindow.isVisible()}")

       def update_metrics(self, metrics_report):
              # Clear existing metrics
              for i in reversed(range(self.metrics_layout.count())): 
                     self.metrics_layout.itemAt(i).widget().setParent(None)

              # Add new metrics
              for metric, value in metrics_report:
                     label = QLabel(f"{metric}: {value}")
                     self.metrics_layout.addWidget(label)