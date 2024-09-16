from PyQt5.QtWidgets import QComboBox, QWidget, QVBoxLayout, QLabel
import pandas as pd
import logging
class DropDownBoxOperations:

    def create_dropdown(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a label for the dropdown
        label = QLabel("Select Market:")
        layout.addWidget(label)
        
        # Create the dropdown (combo box)
        self.market_combo = QComboBox()
        self.populate_market_combo()
        layout.addWidget(self.market_combo)
        
        # Connect the dropdown's change event to a method
        self.market_combo.currentIndexChanged.connect(self.on_market_changed)
        
        return widget

    def populate_market_combo(self):
        self.market_combo.clear()
        self.market_combo.addItem("All Markets")

        if hasattr(self, 'metrics') and hasattr(self.metrics, 'trades'):
            if 'MarketName' in self.metrics.trades.columns:
                markets = sorted(self.metrics.trades['MarketName'].unique())
                self.market_combo.clear()
                self.market_combo.addItem("All Markets")
                self.market_combo.addItems(markets)
            else:
                self.market_combo.clear()
                self.market_combo.addItem("No Markets Available")
        else:
            self.market_combo.clear()
            self.market_combo.addItem("No Markets Available")

    def on_market_changed(self, index):
        selected_market = self.market_combo.currentText()
        if selected_market == "All Markets":
            # Reset to show all markets
            self.metrics.filter_by_market(None)
        else:
            # Filter by selected market
            self.metrics.filter_by_market(selected_market)
        
        # Refresh the metrics
        self.metrics.refresh_metrics_and_ui()
        
        # Refresh the UI to reflect the changes
        self.refresh_ui()

    def create_start_date_calendar(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a label for the dropdown
        label = QLabel("Select Start Date")
        layout.addWidget(label)
        
        # Create the dropdown (combo box)
        self.start_calendar = QComboBox()
        self.populate_start_date()  # Call without arguments
        layout.addWidget(self.start_calendar)
        
        # Connect the dropdown's change event to a method
        self.start_calendar.currentIndexChanged.connect(self.on_date_changed)
        
        return widget

    def populate_start_date(self):
        try:
            # Read the master.csv file
            df = pd.read_csv(self.csv_file_path, parse_dates=['OpenDateUtc'])
            
            if df.empty:
                # If the dataframe is empty, use the current date
                earliest_date = pd.Timestamp.now().date()
            else:
                # Get the earliest date from the 'OpenDateUtc' column
                earliest_date = df['OpenDateUtc'].min().date()
            
            # Set the start date in the calendar
            self.start_calendar.clear()
            self.start_calendar.addItem(earliest_date.strftime('%Y-%m-%d'))
        except Exception as e:
            logging.error(f"Error populating start date: {str(e)}")
            # Set a default date (e.g., 30 days ago)
            default_date = (pd.Timestamp.now() - pd.Timedelta(days=30)).date()
            self.start_calendar.clear()
            self.start_calendar.addItem(default_date.strftime('%Y-%m-%d'))

    def create_end_date_calendar(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a label for the dropdown
        label = QLabel("Select End Date")
        layout.addWidget(label)
        
        # Create the dropdown (combo box)
        self.end_calendar = QComboBox()
        self.populate_end_date()
        layout.addWidget(self.end_calendar)
        
        # Connect the dropdown's change event to a method
        self.end_calendar.currentIndexChanged.connect(self.on_date_changed)
        
        return widget    
   
    def populate_end_date(self):
        try:
            # Read the master.csv file
            df = pd.read_csv(self.csv_file_path, parse_dates=['DateUtc'])
            
            if df.empty:
                # If the dataframe is empty, use the current date
                latest_date = pd.Timestamp.now().date()
            else:
                # Get the latest date from the 'DateUtc' column
                latest_date = df['DateUtc'].max().date()
            
            # Set the end date in the calendar
            self.end_calendar.clear()
            self.end_calendar.addItem(latest_date.strftime('%Y-%m-%d'))
        except Exception as e:
            logging.error(f"Error populating end date: {str(e)}")
            # Set a default date (current date)
            default_date = pd.Timestamp.now().date()
            self.end_calendar.clear()
            self.end_calendar.addItem(default_date.strftime('%Y-%m-%d'))
            
    def on_date_changed(self):
        try:
            selected_date = self.start_calendar.currentText()
            selected_date = pd.to_datetime(selected_date).date()
            
            # Update the end date calendar to ensure it's not before the start date
            current_end_date = self.end_calendar.currentText()
            current_end_date = pd.to_datetime(current_end_date).date()
            
            if current_end_date < selected_date:
                self.end_calendar.setCurrentText(selected_date.strftime('%d/%m/%Y'))
            
            # Update metrics based on new date range
            self.metrics.set_date_range(selected_date, current_end_date)
            self.metrics.refresh_metrics_and_ui()
            
            # Refresh the UI (this should be implemented in FinApp)
            self.refresh_ui()
            
            # Log the change
            logging.info(f"Date range changed. Start date: {selected_date}, End date: {current_end_date}")
            
            # Update message window
            self.updateMessageWindow(f"Date range updated: {selected_date} to {current_end_date}")
        
        except Exception as e:
            logging.error(f"Error in on_date_changed: {str(e)}")
            self.updateMessageWindow(f"<font color='#ff0000'>Error updating date range: {str(e)}</font>")

    def update_date_ranges(self):
        if hasattr(self, 'metrics') and not self.metrics.trades.empty:
            self.populate_start_date()
            self.populate_end_date()
        else:
            self.populate_start_date()
            self.populate_end_date()
