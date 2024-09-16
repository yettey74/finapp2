import os
import logging
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDateEdit, QLabel, QComboBox
from PyQt5.QtCore import QDate
import pandas as pd

class DateOperations:

    def create_date_widget(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        
        # Start Date
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.dateChanged.connect(self.update_metrics)
        layout.addWidget(QLabel("Start:"))
        layout.addWidget(self.start_date_edit)
        
        # End Date
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.dateChanged.connect(self.update_metrics)
        layout.addWidget(QLabel("End:"))
        layout.addWidget(self.end_date_edit)
        
        # Market Selection
        self.market_combo = QComboBox()
        self.populate_market_combo()
        self.market_combo.currentTextChanged.connect(self.update_metrics)
        layout.addWidget(QLabel("Market:"))
        layout.addWidget(self.market_combo)
        
        # Add the existing trader_rating_label
        layout.addWidget(self.trader_rating_label)
        
        DateOperations.set_date_range()
        
        return widget
    
    def set_date_range(self):
        if not self.metrics.trades.empty:
            min_date = self.metrics.trades['DateUtc'].min().date()
            max_date = self.metrics.trades['DateUtc'].max().date()
            self.start_date_edit.setDate(min_date)
            self.end_date_edit.setDate(max_date)
        else:
            # Set default dates if there's no data
            current_date = QDate.currentDate()
            self.start_date_edit.setDate(current_date.addDays(-30))
            self.end_date_edit.setDate(current_date)

    
    def refresh_date_range(self):
        if not self.metrics.trades.empty:
            min_date = self.metrics.trades['DateUtc'].min().date()
            max_date = self.metrics.trades['DateUtc'].max().date()
            self.start_calendar.clear()
            self.start_calendar.addItem(min_date.strftime('%Y-%m-%d'))
            self.end_calendar.clear()
            self.end_calendar.addItem(max_date.strftime('%Y-%m-%d'))
        else:
            current_date = pd.Timestamp.now().date()
            self.start_calendar.clear()
            self.start_calendar.addItem(current_date.strftime('%Y-%m-%d'))
            self.end_calendar.clear()
            self.end_calendar.addItem(current_date.strftime('%Y-%m-%d'))