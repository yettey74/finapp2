import os
import logging
from PyQt5.QtWidgets import ( QMessageBox, QFileDialog )
import pandas as pd
from def_metrics import TradingMetrics
from def_dates import DateOperations
from def_ratings import RatingOperations

class FileOperations:

    def __init__(self, window_operations, csv_file_path):  # Add tab_widget as a parameter
        self.window_operations = window_operations
        self.csv_file_path = csv_file_path

    def create_empty_csv(file_path):
        headers = [
            'TextDate', 'Summary', 'MarketName', 'Period', 'ProfitAndLoss', 'Transaction type',
            'Reference', 'Open level', 'Close level', 'Size', 'Currency', 'PL Amount',
            'Cash transaction', 'DateUtc', 'OpenDateUtc', 'CurrencyIsoCode'
        ]
        df = pd.DataFrame(columns=headers)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_csv(file_path, index=False)
            logging.info(f"Created empty CSV file at {file_path}")
        except Exception as e:
            logging.info(f"Failed to create empty CSV file at {file_path}")
            logging.warning(e)

    def updateFile(self):
        logging.info("updateFile method called")
        
        if self.window_operations is not None:  # Check if window_operations is set
            logging.info("window_operations is set correctly.")
            self.window_operations.updateOverviewTab("Updating file...")
        else:
            logging.warning("window_operations is None.")
            return  # Exit if window_operations is not set

        logging.info("Opening file dialog")
        # Pass the main window as the parent instead of window_operations
        file_path, _ = QFileDialog.getOpenFileName(self.window_operations.parent(), "Select File to Update From", "", "CSV Files (*.csv)")
        
        if not file_path:
            logging.info("No file selected, update cancelled")
            self.window_operations.updateOverviewTab("Update cancelled.")
            return

        logging.info(f"Selected file: {file_path}")
        
        try:
            logging.info(f"Getting new data ...")   
            new_data = pd.read_csv(file_path)
            logging.info(f"New data loaded successfully. Shape: {new_data.shape}")           

            # Convert 'DateUtc' and 'OpenDateUtc' to datetime with a specified format
            new_data['DateUtc'] = pd.to_datetime(new_data['DateUtc'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            new_data['OpenDateUtc'] = pd.to_datetime(new_data['OpenDateUtc'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

            # Check for NaT values after conversion
            if new_data['DateUtc'].isnull().any() or new_data['OpenDateUtc'].isnull().any():
                logging.warning(f"NaT in OpenDateUtc: {new_data['DateUtc']}")
                logging.warning(f"NaT in OpenDateUtc: {new_data['OpenDateUtc']}")
                logging.warning("There are NaT values in DateUtc or OpenDateUtc after conversion.")
                logging.warning(f"NaT count in DateUtc: {new_data['DateUtc'].isnull().sum()}")
                logging.warning(f"NaT count in OpenDateUtc: {new_data['OpenDateUtc'].isnull().sum()}")
                self.window_operations.updateOverviewTab("<font color='#ff0000'>There are NaT values in DateUtc or OpenDateUtc after conversion.</font>")
                return

            # Log the data types after conversion
            logging.warning(f"Data types after conversion: {new_data.dtypes}")
            logging.warning(f"First few entries of DateUtc after conversion: {new_data['DateUtc'].head()}")

            # Convert DateUtc and OpenDateUtc to Unix time format with 'T'
            # new_data['DateUtc'] = new_data['DateUtc'].apply(lambda x: f"{int(x.timestamp())}T" if pd.notnull(x) else 'NaT')
            # new_data['OpenDateUtc'] = new_data['OpenDateUtc'].apply(lambda x: f"{int(x.timestamp())}T" if pd.notnull(x) else 'NaT')
            
            # Process the new data
            new_data['PL Amount'] = new_data['PL Amount'].replace({',': ''}, regex=True).astype(float)
            
            if 'Balance' not in new_data.columns:
                new_data['Balance'] = new_data['PL Amount'].cumsum()
            else:
                new_data['Balance'] = new_data['Balance'].replace({',': ''}, regex=True).astype(float)
            
            # Ensure DateUtc is still in datetime format for grouping
            # new_data['DateUtc'] = pd.to_datetime(new_data['DateUtc'], errors='coerce')

            # Check again for NaT values after conversion to Unix time format
            # if new_data['DateUtc'].isnull().any():
            #     logging.warning("There are NaT values in DateUtc after converting to Unix time format.")
            #     self.window_operations.updateOverviewTab("<font color='#ff0000'>There are NaT values in DateUtc after converting to Unix time format.</font>")
            #     return

            new_data = new_data.sort_values('DateUtc')
            
            # Calculate daily returns
            new_data['Daily Return'] = new_data.groupby(new_data['DateUtc'].dt.date)['Balance'].pct_change(fill_method=None)
            
            # Update the file
            try:
                master_data = pd.read_csv(self.csv_file_path, parse_dates=['DateUtc', 'OpenDateUtc'])
                logging.info(f"Data loaded successfully. Shape: {master_data.shape}")
            except Exception as e:
                logging.error(f"Error reading data file: {str(e)}")
                self.window_operations.updateOverviewTab(f"<font color='#ff0000'>Error reading master data file: {str(e)}</font>")
                return
            
            combined_data = pd.concat([master_data, new_data], ignore_index=True)
            combined_data = combined_data.sort_values('DateUtc').reset_index(drop=True)
            combined_data.to_csv(self.csv_file_path, index=False)
            logging.info(f"File updated successfully. {len(new_data)} new rows added.")
            
            self.window_operations.updateOverviewTab(f"<font color='#00ff00'>Master file updated successfully. {len(new_data)} new rows added.</font>")
            
            # Reinitialize TradingMetrics with the updated file
            self.metrics = TradingMetrics(self.csv_file_path)
            
            # Reset date range and market filter
            DateOperations.set_date_range(self)
            self.populate_market_combo()
            
            # Refresh the UI
            TradingMetrics.refresh_metrics_and_ui(self)
            RatingOperations.update_trader_rating(self)

            # After processing, update the tab text
            self.tab_widget.setTabText(self.tab_widget.indexOf(self.window_operations.overviewTab), "Updated Overview")

        except Exception as e:
            logging.error(f"Error reading new data file: {str(e)}")
            self.window_operations.updateOverviewTab(f"<font color='#ff0000'>Error reading new data file: {str(e)}</font>")
            return

    def deleteFile(self):
        reply = QMessageBox.question(self.window_operations, 'Delete File',
                                     "Are you sure you want to delete the master file and create an empty one?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Create an empty DataFrame with the correct headers
                empty_df = pd.DataFrame(columns=[
                    'TextDate', 'Summary', 'MarketName', 'Period', 'ProfitAndLoss', 'Transaction type',
                    'Reference', 'Open level', 'Close level', 'Size', 'Currency', 'PL Amount',
                    'Cash transaction', 'DateUtc', 'OpenDateUtc', 'CurrencyIsoCode'
                ])
                
                # Save the empty DataFrame to the master.csv file
                empty_df.to_csv(self.csv_file_path, index=False)
                
                self.window_operations.updateOverviewTab("<font color='#00ff00'>Master file deleted and replaced with an empty file containing headers.</font>")
                
                # Reinitialize TradingMetrics with the empty file
                self.metrics = TradingMetrics(self.csv_file_path)
                
                # Reset date range and market filter
                self.set_date_range()
                self.populate_market_combo()
                
                # Refresh the UI
                self.refresh_metrics_and_ui()
                
            except Exception as e:
                logging.error(f"Error deleting master file: {str(e)}")
                self.window_operations.updateOverviewTab(f"<font color='#ff0000'>Error deleting master file: {str(e)}</font>")
        else:
            self.window_operations.updateOverviewTab("Delete master file operation cancelled.")