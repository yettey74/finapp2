import logging
import pandas as pd

class DataFrameOperations:

    def process_dataframe(self, df):
        logging.debug(f"Original DataFrame shape: {df.shape}")
        logging.debug(f"Original DataFrame columns: {df.columns}")

        # Convert 'DateUtc' and 'OpenDateUtc' to datetime
        df['DateUtc'] = pd.to_datetime(df['DateUtc'], errors='coerce')
        df['OpenDateUtc'] = pd.to_datetime(df['OpenDateUtc'], errors='coerce')

        # Check for NaT values
        if df['DateUtc'].isnull().any() or df['OpenDateUtc'].isnull().any():
            logging.warning("There are NaT values in the DateUtc or OpenDateUtc columns after conversion.")
            logging.debug(f"NaT count in DateUtc: {df['DateUtc'].isnull().sum()}")
            logging.debug(f"NaT count in OpenDateUtc: {df['OpenDateUtc'].isnull().sum()}")

            # Optionally, log the rows with NaT values for further inspection
            logging.debug("Rows with NaT in DateUtc:")
            logging.debug(df[df['DateUtc'].isnull()])

            logging.debug("Rows with NaT in OpenDateUtc:")
            logging.debug(df[df['OpenDateUtc'].isnull()])

        # Log the data types after conversion
        logging.debug(f"Data types after conversion: {df.dtypes}")
        logging.debug(f"First few entries of DateUtc after conversion: {df['DateUtc'].head()}")

        # Sort the dataframe by date
        df = df.sort_values('DateUtc')

        # Convert 'PL Amount' to float, handling comma-separated numbers
        df['PL Amount'] = df['PL Amount'].replace({',': ''}, regex=True).astype(float)

        # Calculate 'Balance' if it doesn't exist
        if 'Balance' not in df.columns:
            df['Balance'] = df['PL Amount'].cumsum()
        else:
            df['Balance'] = df['Balance'].replace({',': ''}, regex=True).astype(float)        
        
        # Calculate daily returns
        df['Daily Return'] = df.groupby(df['DateUtc'].dt.date)['Balance'].pct_change()
        
        # Prepare the returns array
        self.returns = df['Daily Return'].dropna().values
        
        # Prepare the trades dataframe
        self.trades = df[df['Transaction type'] == 'DEAL'].copy()
        self.trades['profit'] = self.trades['PL Amount']
        self.trades['balance'] = self.trades['Balance']
        self.trades['duration'] = (self.trades['DateUtc'] - self.trades['OpenDateUtc']).dt.total_seconds() / 3600  # duration in hours
        self.trades['in_position'] = self.trades['Size'] != 0
        
        logging.debug(f"Processed DataFrame shape: {self.trades.shape}")
        logging.debug(f"Trades DataFrame columns: {self.trades.columns}")
        logging.debug(f"Trades DataFrame head: {self.trades.head()}")