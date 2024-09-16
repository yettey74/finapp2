from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QFrame, QVBoxLayout, QDateEdit, QHBoxLayout, QComboBox)

class WidgetOperations:

    def create_metric_widget(self, title, value):
        widget = QFrame(self)
        widget.setFrameStyle(QFrame.Box | QFrame.Raised)
        widget.setLineWidth(2)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; color: #00ff00; font-size: 12px;")
        
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("font-size: 18px; color: #ffffff;")
        
        explanation = self.get_metric_explanation(title)
        explanation_label = QLabel(explanation)
        explanation_label.setWordWrap(True)
        explanation_label.setAlignment(Qt.AlignJustify)
        explanation_label.setStyleSheet("font-size: 10px; color: #aaaaaa;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(explanation_label)
        
        return widget
    
    @classmethod
    def create_trader_rating_widget(cls):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Trader Rating: N/A")
        layout.addWidget(label)
        widget.setLayout(layout)
        
        # If you need to access instance methods or attributes, you'll need to pass the instance:
        def update_rating(instance):
            instance.update_trader_rating()
        
        return widget, update_rating