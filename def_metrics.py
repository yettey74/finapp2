import logging
import numpy as np
import pandas as pd
from scipy import stats
import itertools
import warnings
from PyQt5.QtWidgets import (QWidget, QListWidget, QGridLayout, QLabel, QVBoxLayout, QScrollArea)
from def_windows import WindowOperations

def safe_divide(numerator, denominator):
    if denominator == 0 or pd.isna(denominator):
        return float('inf')
    return numerator / denominator

def format_value(value):
    if pd.isna(value) or value == float('inf'):
        return "∞"
    return value

class TradingMetrics:
    def __init__(self, trades):

        if isinstance(trades, pd.DataFrame) and not trades.empty:
            self.trades = trades
            self.filtered_trades = trades[trades['Transaction type'] == 'DEAL'].copy()
            
            # Ensure 'PL Amount' is numeric
            self.filtered_trades['PL Amount'] = pd.to_numeric(self.filtered_trades['PL Amount'].replace({',': ''}, regex=True), errors='coerce')
            
            # Calculate balance if it doesn't exist
            if 'Balance' not in self.filtered_trades.columns:
                # self.filtered_trades['PL Amount'] = self.filtered_trades['PL Amount'].cumsum()
                self.filtered_trades['Balance'] = self.filtered_trades['PL Amount'].cumsum()
            
            logging.info(f"Filtered trades: {len(self.filtered_trades)} out of {len(self.trades)} total rows")
            
            # Set start_date and end_date
            self.start_date = self.filtered_trades['DateUtc'].min().date()
            self.end_date = self.filtered_trades['DateUtc'].max().date()
        else:
            logging.warning("Invalid input for TradingMetrics. Initializing with empty DataFrame.")
            self.trades = pd.DataFrame()
            self.filtered_trades = pd.DataFrame()
            self.start_date = None
            self.end_date = None
        
        logging.debug(f"TradingMetrics initialized with trades shape: {self.trades.shape}")
        logging.debug(f"TradingMetrics filtered trades shape: {self.filtered_trades.shape}")
        logging.debug(f"TradingMetrics filtered trades head: {self.filtered_trades.head()}")
        logging.debug(f"TradingMetrics filtered trades columns: {self.filtered_trades.columns}")
        
        self.risk_free_rate = 0.02  # Set a default value, e.g., 2%
        
        if not self.filtered_trades.empty:
            self.calculate_metrics()
        else:
            logging.warning("No trades available for metric calculation")    

    def set_risk_free_rate(self, rate):
        self.risk_free_rate = rate
        self.calculate_metrics()  # Recalculate metrics with the new rate

    def create_metrics_widget(self):
        logging.info("Creating Metric Widgets")
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container_widget = QWidget()
        scroll_area.setWidget(container_widget)
        
        main_layout = QVBoxLayout(container_widget)
        
        # Add some spacing between the date_rating_widget and the metrics grid
        main_layout.addSpacing(10)
        
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)
        
        if self.metrics.filtered_trades.empty:
            no_data_label = QLabel("No trade data available. Please update the master file.")
            no_data_label.setStyleSheet("color: #ff0000; font-size: 14px;")
            grid_layout.addWidget(no_data_label, 0, 0)
            logging.warning("No trade data available")
        else:
            metrics = self.metrics.generate_report()
            
            row, col = 0, 0
            for title, metric_func in metrics:
                try:
                    value = metric_func()
                    metric_widget = self.create_metric_widget(title, value)
                    grid_layout.addWidget(metric_widget, row, col)
                    col += 1
                    if col == 3:
                        col = 0
                        row += 1
                    logging.info(f"Added metric: {title} = {value}")
                except Exception as e:
                    logging.error(f"Error calculating metric {title}: {str(e)}")
        
        logging.info(f"Metrics Widgets created. Is visible: {scroll_area.isVisible()}")
        
        return scroll_area

    def get_metric_explanation(self, metric):
        explanations = {
            'Total Trades': "The total number of trades executed in the trading period.",
            'Total Deposits': "The total amount of money deposited into the trading account.",
            'Total Withdrawals': "The total amount of money withdrawn from the trading account.",
            'Gross Profit': "The total amount of money Deposited minus total amount of money withdrawn from the trading account.",
            'Net Profit': "The total amount of Gross profit - charges and fees.",
            'CFD Funding Paid': "Amount of money paid when holding a Contract For Difference",
            'CFD Funding Received': "Amount of money received when holding a Contract For Difference",
            'Net Profit': "The difference between total deposits and Net Withdrawals.",
            'Win Rate': "The percentage of trades that resulted in a profit.",
            'Profit Factor': "The ratio of gross profit to gross loss. Values above 1 indicate overall profitability.",
            'Sharpe Ratio': "A measure of risk-adjusted return. Higher values indicate better risk-adjusted performance.",
            'Max Drawdown %': "The largest peak-to-trough decline in the account balance, expressed as a percentage.",
            'Max Drawdown $': "The largest peak-to-trough decline in the account balance, expressed in dollars.",
            'Average Trade': "The average profit or loss per trade.",
            'Expectancy': "The average amount you can expect to win (or lose) per trade.",
            'Risk-Reward Ratio': "The ratio of the average win to the average loss.",
            'Sortino Ratio': "Similar to Sharpe ratio, but only considers downside deviation.",
            'Calmar Ratio': "The ratio of average annual rate of return to maximum drawdown.",
            'Omega Ratio': "A probability-weighted ratio of gains versus losses for a threshold return target.",
            'Kappa Three': "A measure of downside risk-adjusted performance.",
            'Gain to Pain Ratio': "The ratio of the sum of all returns to the absolute value of all losses.",
            'Van Sharpe Ratio': "A variation of the Sharpe ratio using logarithmic returns.",
            'Information Ratio': "Measures the risk-adjusted returns of an investment compared to a benchmark.",
            'Maximum Consecutive Wins': "The highest number of winning trades in a row.",
            'Maximum Consecutive Losses': "The highest number of losing trades in a row.",
            'Payoff Ratio': "The ratio of average winning trade to average losing trade.",
            'Profit per Day': "The average daily profit over the trading period.",
            'R-Squared': "Indicates how well the trading performance correlates with a benchmark.",
            'Skewness': "Measures the asymmetry of the return distribution.",
            'Kurtosis': "Measures the 'tailedness' of the return distribution.",
            'Value at Risk (95%)': "The maximum loss expected with 95% confidence over a specific time frame.",
            'Expected Shortfall (95%)': "The expected loss in the worst 5% of cases.",
            'Modified Sharpe Ratio': "An adjusted Sharpe ratio that accounts for skewness and kurtosis.",
            'Sterling Ratio': "A risk-adjusted return metric that uses average drawdown instead of standard deviation.",
            'Burke Ratio': "A performance measurement that uses downside risk to determine reward.",
            'Tail Ratio': "The ratio of the 95th percentile of returns to the absolute value of the 5th percentile.",
            'Upside Potential Ratio': "The ratio of upside returns to downside risk.",
            'Rachev Ratio': "A ratio of expected tail gain to expected tail loss.",
            'Pain Index': "The average of all drawdowns over the period.",
            'Ulcer Performance Index': "A risk-adjusted return measure that penalizes deep and long-lasting drawdowns.",
            'Serenity Index': "A risk-adjusted performance measure that accounts for the length of the track record.",
            'Bernardo Ledoit Ratio': "The ratio of the average gain to the average loss.",
            'K-Ratio': "Measures the consistency of returns over time.",
            'Prospect Ratio': "A ratio that incorporates behavioral finance concepts into performance measurement.",
            'Tracking Error': "The standard deviation of the difference between the strategy's returns and the benchmark's returns.",
            'Jensen\'s Alpha': "The average return on the portfolio over and above that predicted by the capital asset pricing model (CAPM).",
        }
        return explanations.get(metric, "No explanation available for this metric.")
    
        
    # def update_metrics(self, metrics_report):
    #         # Clear existing metrics
    #         for i in reversed(range(self.metrics_layout.count())): 
    #                 self.metrics_layout.itemAt(i).widget().setParent(None)
    #                 self.metrics_layout.itemAt(i) = 0

    #         # Add new metrics
    #         for metric, value in metrics_report:
    #                 label = QLabel(f"{metric}: {value}")
    #                 self.metrics_layout.addWidget(label)

    def update_metrics(self):
        if self.filtered_trades.empty:
            logging.warning("No trades available for metric calculation")
            # Set default values for metrics
            self.total_trades_count = 0
            self.win_rate_value = 0
            self.profit_factor_value = 0
            self.sharpe_ratio_value = 0
            self.max_drawdown_percentage = 0
            self.max_drawdown_dollar = 0
            self.average_trade_value = 0
            self.expectancy_value = 0
            self.sortino_ratio_value = 0
            self.calmar_ratio_value = 0
            self.omega_ratio_value = 0
                
            return
        
        self.updating_metrics = True
        try:
            self.returns = self.calculate_returns()
            self.start_date = self.filtered_trades['DateUtc'].min().date() if not self.filtered_trades.empty else None
            self.end_date = self.filtered_trades['DateUtc'].max().date() if not self.filtered_trades.empty else None
            
            # Recalculate basic metrics
            self.total_trades_count = self.total_trades()
            self.win_rate_value = format_value(self.win_rate())
            self.profit_factor_value = format_value(self.profit_factor())
            self.sharpe_ratio_value = format_value(self.sharpe_ratio())
            self.max_drawdown_percentage = format_value(self.max_drawdown())
            self.max_drawdown_dollar = format_value(self.max_drawdown_dollars())
            self.average_trade_value = format_value(self.average_trade())
            self.expectancy_value = format_value(self.expectancy())
            
            # Recalculate advanced metrics
            self.sortino_ratio_value = format_value(self.sortino_ratio())
            self.calmar_ratio_value = format_value(self.calmar_ratio())
            self.omega_ratio_value = format_value(self.omega_ratio())
            # ... (other metrics)

            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            if start_date > end_date:
                self.end_date_edit.setDate(self.start_date_edit.date())
                end_date = start_date

            selected_market = self.market_combo.currentText()

            if selected_market != "All Markets":
                self.filter_by_market(selected_market)
            else:
                self.reset_market_filter()
            
            self.refresh_metrics_and_ui()
            self.update_trader_rating()

        # Add a message to indicate the update
            WindowOperations.updateMessageWindow(self, f"Metrics updated for {selected_market} from {start_date} to {end_date}")
        except Exception as e:
            logging.error(f"Error updating metrics: {str(e)}")
            WindowOperations.updateMessageWindow(self, f"<font color='#ff0000'>Error updating metrics: {str(e)}</font>")
        finally:
            self.updating_metrics = False

    def refresh_metrics_and_ui(self):
        logging.info("Refreshing metrics and UI")
        
        # Remove the old other_widget
        if hasattr(self, 'other_widget'):
            self.main_layout.removeWidget(self.other_widget)
            self.other_widget.deleteLater()
        
        # Create and add the new other_widget (which is now a QScrollArea)
        self.other_widget = self.create_metrics_widget()
        self.main_layout.addWidget(self.other_widget)
        self.main_layout.setStretchFactor(self.other_widget, 1)
        
        # Update the trader rating
        self.update_trader_rating()
        
        logging.info("Metrics and UI refreshed")


#############################
## Value Value Metrics
##
#############################
    
    def total_trades(self):
        if self.filtered_trades.empty:
            return 0
        total_trades = self.filtered_trades[
            (self.filtered_trades['Transaction type'] == 'DEAL') &
            (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
            (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
        ]

        print("Total trades:")
        print(total_trades)
        
        return len(total_trades) 

    def std_dev(self):
        return np.std(self.returns)

    def trade_days(self):
        return len(self.returns)   
    
    def maximum_consecutive_wins(self):
        deal_trades = self.filtered_trades[self.filtered_trades['Transaction type'] == 'DEAL']
        if deal_trades.empty:
            return 0
        consecutive_wins = (deal_trades['PL Amount'] > 0).astype(int)
        return max((sum(1 for _ in group) for key, group in itertools.groupby(consecutive_wins) if key), default=0)  

    def profitable_trades(self):
        if self.filtered_trades.empty:
            return 0
        return sum( (self.filtered_trades['PL Amount'] > 0) & 
                    (self.filtered_trades['Transaction type'] == 'DEAL')&
                    (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
                    (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
                )

    def losing_trades(self):
        return sum((self.filtered_trades['PL Amount'] <= 0) & 
                    (self.filtered_trades['Transaction type'] == 'DEAL')& 
                    (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
                    (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
                ) 

    def maximum_consecutive_losses(self):
        deal_trades = self.filtered_trades[self.filtered_trades['Transaction type'] == 'DEAL']
        if deal_trades.empty:
            return 0
        consecutive_losses = (deal_trades['PL Amount'] < 0).astype(int)
        return max((sum(1 for _ in group) for key, group in itertools.groupby(consecutive_losses) if key), default=0)
    
#############################
## Percentage Value Metrics
##
#############################

    def cash_rate(self):
        # return self.risk_free_rate / 252  # Daily risk-free rate
        return self.risk_free_rate / 365  # Daily risk-free rate
    
    def win_rate(self):
        total = self.total_trades()
        return safe_divide(self.profitable_trades(), total)

    def loss_rate(self):
        return 1 - self.win_rate()
    
#############################
## Dollar Value Metrics
##
#############################    
    
    def average_trade(self):
        deal_trades = self.filtered_trades[self.filtered_trades['Transaction type'] == 'DEAL']
        return np.mean(deal_trades['PL Amount']) if not deal_trades.empty else 0

    def avg_daily_return(self):
        return np.mean(self.returns)

    def average_holding_period(self):
        return np.mean(self.filtered_trades['duration'])

    def avg_win(self):
        profitable_trades = self.profitable_trades()
        return safe_divide(self.profitable_amount(), profitable_trades)

    def avg_loss(self):
        losing_trades = self.losing_trades()
        return safe_divide(self.loss_amount(), losing_trades)    

    def calculate_funding_interest_paid(self):
        if self.trades.empty:
            return pd.Series()
        cdf_funding_paid_sum = self.filtered_trades[
            (self.filtered_trades['Summary'] == 'CFD funding Interest Paid') &
            (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
            (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
        ]['PL Amount'].sum()
        if pd.notnull(cdf_funding_paid_sum):
            return cdf_funding_paid_sum
        else:
            return pd.Series()

    def calculate_funding_interest_recieved(self):
        if self.trades.empty:
            return pd.Series()
        cdf_funding_recieved_sum = self.filtered_trades[
            (self.filtered_trades['Summary'] == 'CFD funding Interest Recieved') &
            (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
            (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
        ]['PL Amount'].sum()
        if pd.notnull(cdf_funding_recieved_sum):
            return cdf_funding_recieved_sum
        else:
            return pd.Series()

    def calculate_returns(self):
        if self.filtered_trades.empty or self.start_date is None or self.end_date is None:
            return pd.Series()

        deal_trades = self.filtered_trades[
            (self.filtered_trades['Transaction type'] == 'DEAL') &
            (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
            (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
        ]

        daily_returns = deal_trades.groupby(deal_trades['DateUtc'].dt.date)['PL Amount'].sum()

        if len(deal_trades) > 0 and 'Balance' in deal_trades.columns:
            return daily_returns / deal_trades['Balance'].iloc[0]
        else:
            return pd.Series()

    def daily_cash(self):
        return np.mean(self.filtered_trades['Balance']) 

    def largest_winning_trade(self):
        return self.filtered_trades['PL Amount'].max()

    def largest_losing_trade(self):
        return self.filtered_trades['PL Amount'].min()
     
    def loss_amount(self):
        deal_trades = self.filtered_trades[
            (self.filtered_trades['Transaction type'] == 'DEAL') & 
            (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
            (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
        ]
        return sum(deal_trades[deal_trades['PL Amount'] < 0]['PL Amount'])

    def max_drawdown(self):
        if self.filtered_trades.empty:
            return 0
        cumulative_returns = (1 + self.returns).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns / peak) - 1
        max_dd = drawdown.min()
        return max(min(max_dd, 0), -1)  # Limit max drawdown to -100%

    def max_drawdown_dollars(self):
        if self.filtered_trades.empty:
            return 0
        balance = self.filtered_trades['Balance']  # Note the capital 'B'
        peak = balance.cummax()
        drawdown = peak - balance
        return drawdown.max()

    def profitable_amount(self):
        deal_trades = self.filtered_trades[
            (self.filtered_trades['Transaction type'] == 'DEAL') & 
            (self.filtered_trades['DateUtc'].dt.date >= self.start_date) &
            (self.filtered_trades['DateUtc'].dt.date <= self.end_date)
        ]
        return sum(deal_trades[deal_trades['PL Amount'] > 0]['PL Amount'])
    
    def profit_factor(self):
        return safe_divide(self.profitable_amount(), self.loss_amount())
    
    ########################################################
    ## LEAVE this comment section here start of Ratio def's 
    ## RATIO METRICS SECTION
    ########################################################
    def burke_ratio(self):
        drawdowns = 1 - self.filtered_trades['Balance'] / self.filtered_trades['Balance'].cummax()
        sum_squared_drawdowns = np.sum(drawdowns**2)
        if sum_squared_drawdowns == 0:
            return float('inf')
        return safe_divide(self.return_rate(), np.sqrt(sum_squared_drawdowns))

    def bernardo_ledoit_ratio(self):
        positive_returns = self.returns[self.returns > 0]
        negative_returns = self.returns[self.returns < 0]
        return safe_divide(np.mean(positive_returns), abs(np.mean(negative_returns)))

    def calmar_ratio(self):
        max_dd = self.max_drawdown()
        if max_dd == 0:
            return float('inf')
        return safe_divide(self.return_rate(), abs(max_dd))
    def downside_deviation(self, threshold=0):
        downside_returns = self.returns[self.returns < threshold]
        return np.sqrt(np.mean(downside_returns**2))

    def expected_shortfall(self, confidence=0.95):
        var = self.value_at_risk(confidence)
        returns_below_var = self.returns[self.returns <= var]
        if len(returns_below_var) == 0:
            return np.nan
        return np.mean(returns_below_var)
    def expectancy(self):
        return (self.win_rate() * self.avg_win()) - (self.loss_rate() * self.avg_loss())
    def exposure(self):
        return np.mean(self.filtered_trades['in_position'])
    def equity_curve(self):
        return self.filtered_trades['Balance']

    def gain_to_pain_ratio(self):
        negative_returns = self.returns[self.returns < 0]
        return safe_divide(sum(self.returns), abs(sum(negative_returns)))

    def jensens_alpha(self):
        # Assuming market returns are 0 and beta is 1 for simplicity
        market_returns = np.zeros_like(self.returns)
        beta = 1
        return self.avg_daily_return() - (self.cash_rate() + beta * (np.mean(market_returns) - self.cash_rate()))
    
    def kappa_three(self):
        downside_deviation = np.std(self.returns[self.returns < 0])
        return safe_divide(self.avg_daily_return() - self.cash_rate(), downside_deviation**3)    
    def kurtosis(self):
        return stats.kurtosis(self.returns)
    def k_ratio(self):
        x = np.arange(len(self.returns))
        slope, _, _, _, _ = stats.linregress(x, np.cumsum(self.returns))
        return safe_divide(slope, self.std_dev())
    
    def information_ratio(self):
        # Assuming benchmark returns are 0 for simplicity
        benchmark_returns = np.zeros_like(self.returns)
        return safe_divide(self.avg_daily_return() - np.mean(benchmark_returns), np.std(self.returns - benchmark_returns))

    def mae(self):
        if 'max_adverse_excursion' in self.filtered_trades.columns:
            return self.filtered_trades['max_adverse_excursion'].max()
        else:
            print("'max_adverse_excursion' column not found in trades DataFrame")
            return None        
    def monte_carlo_simulation(self, num_simulations=1000, num_periods=252):
        simulated_returns = np.random.normal(self.avg_daily_return(), self.std_dev(), (num_simulations, num_periods))
        return np.cumprod(1 + simulated_returns, axis=1)
    def modified_sharpe_ratio(self):
        if self.filtered_trades.empty:
            return 0
        return self.sharpe_ratio() / (1 + (self.skewness() / 6) * self.sharpe_ratio() - (self.kurtosis() - 3) / 24 * self.sharpe_ratio()**2)
    
    def omega_ratio(self):
        threshold = self.cash_rate()
        returns_above_threshold = self.returns[self.returns > threshold]
        returns_below_threshold = self.returns[self.returns <= threshold]
        return safe_divide(sum(returns_above_threshold), abs(sum(returns_below_threshold)))
    
    def pain_index(self):
        drawdowns = 1 - self.filtered_trades['Balance'] / self.filtered_trades['Balance'].cummax()
        return np.mean(drawdowns)
    def payoff_ratio(self):
        return safe_divide(abs(self.avg_win()), self.avg_loss())
   
    def prospect_ratio(self, threshold=0, loss_aversion=2.25):
        gains = self.returns[self.returns > threshold]
        losses = self.returns[self.returns <= threshold]
        return safe_divide((np.mean(gains)**0.88), (loss_aversion * abs(np.mean(losses))**0.88))

    def risk_reward_ratio(self):
        avg_loss = self.avg_loss()
        return safe_divide(self.avg_win(), avg_loss)
    def recovery_factor(self):
        max_dd = self.max_drawdown()
        return safe_divide(abs(self.return_rate()), abs(max_dd))
    def r_squared(self):
        # Assuming benchmark returns are 0 for simplicity
        benchmark_returns = np.zeros_like(self.returns)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return stats.pearsonr(self.returns, benchmark_returns)[0]**2
    def rachev_ratio(self, confidence=0.95):
        if len(self.returns) == 0:
            return float('inf')
        positive_returns = self.returns[self.returns > 0]
        negative_returns = self.returns[self.returns < 0]
        if len(positive_returns) == 0 or len(negative_returns) == 0:
            return float('inf')
        var_gain = np.percentile(positive_returns, 100 * (1 - confidence))
        var_loss = abs(np.percentile(negative_returns, 100 * confidence))
        return safe_divide(var_gain, var_loss)
    def skewness(self):
        return stats.skew(self.returns)
    def sterling_ratio(self):
        avg_drawdown = np.mean(1 - self.filtered_trades['Balance'] / self.filtered_trades['Balance'].cummax())
        if avg_drawdown == 0:
            return float('inf')
        return safe_divide(self.return_rate(), avg_drawdown)
    def sharpe_ratio(self):
        return safe_divide(self.avg_daily_return() - self.cash_rate(), self.std_dev())
    def sortino_ratio(self):
        downside_returns = self.returns[self.returns < 0]
        downside_deviation = np.std(downside_returns)
        return safe_divide(self.avg_daily_return() - self.cash_rate(), downside_deviation)
    def serenity_index(self):
        return self.sharpe_ratio() * np.sqrt(self.trade_days())

    def tail_ratio(self):
        return abs(np.percentile(self.returns, 95)) / abs(np.percentile(self.returns, 5))
    def treynor_ratio(self):
        # Assuming beta is 1 for simplicity
        beta = 1
        return safe_divide(self.avg_daily_return() - self.cash_rate(), beta)
    def ulcer_index(self):
        drawdown = 1 - self.filtered_trades['Balance'] / self.filtered_trades['Balance'].cummax()
        return np.sqrt(np.mean(drawdown**2))
    def upside_potential_ratio(self, threshold=0):
        upside_returns = self.returns[self.returns > threshold]
        downside_dev = self.downside_deviation(threshold)
        return safe_divide(np.mean(upside_returns), downside_dev)
    def van_sharpe_ratio(self):
        return safe_divide(np.log(1 + self.avg_daily_return()), np.log(1 + self.std_dev()))
    def ulcer_performance_index(self):
        return safe_divide(self.avg_daily_return() - self.cash_rate(), self.ulcer_index())
    def value_at_risk(self, confidence=0.95):
        if len(self.returns) == 0:
            return np.nan
        return np.percentile(self.returns, 100 * (1 - confidence))

###################
## END METRICS CALCS 
####################
    def tracking_error(self):
        # Assuming benchmark returns are 0 for simplicity
        benchmark_returns = np.zeros_like(self.returns)
        return np.std(self.returns - benchmark_returns)

    def generate_report(self):
        if self.filtered_trades.empty:
            print("No trade data available. Unable to generate report.")
            return []

        metrics = [
            ('Total Trades', self.total_trades),
            ('Total Deposits', lambda: f"${self.get_deposits():.2f}"),
            ('Total Withdrawals', lambda: f"${self.get_withdrawals():.2f}" if not np.isnan(self.get_withdrawals()) else "N/A"),
            ('Gross Profit', lambda: f"${self.get_deposits() - self.get_withdrawals():.2f}" if self.get_deposits() - self.get_withdrawals() != float('inf') else "N/A"),
            ('Net Deposits', lambda: f"${self.net_deposits():.2f}" if not np.isnan(self.net_deposits()) else "N/A"),
            ('CFD Funding Paid', lambda: f"${self.calculate_funding_interest_paid():.2f}" if not np.isnan(self.calculate_funding_interest_paid()) else "N/A"),
            ('CFD Funding Received', lambda: f"${self.calculate_funding_interest_recieved():.2f}" if not np.isnan(self.calculate_funding_interest_recieved()) else "N/A"),
            ('Maximum Consecutive Wins', lambda: f"{self.maximum_consecutive_wins()}" if not np.isnan(self.maximum_consecutive_wins()) else "N/A"),
            ('Maximum Consecutive Losses', lambda: f"{self.maximum_consecutive_losses()}" if not np.isnan(self.maximum_consecutive_losses()) else "N/A"),
            ('Win Rate', lambda: f"{self.win_rate():.2%}" if self.win_rate() != float('inf') else "∞"),
            ('Average Trade', lambda: f"${self.average_trade()}" if self.average_trade() != float('inf') else "∞"),
            ('Profit Factor', lambda: f"{self.profit_factor():.2f}" if self.profit_factor() != float('inf') else "∞"),
            ('Sharpe Ratio', lambda: f"{self.sharpe_ratio():.2f}" if self.sharpe_ratio() != float('inf') else "∞"),
            ('Max Drawdown %', lambda: f"{self.max_drawdown():.2%}" if self.max_drawdown() != float('inf') else "∞"),
            ('Max Drawdown $', lambda: f"${self.max_drawdown_dollars():.2f}" if self.max_drawdown_dollars() != float('inf') else "∞"),
            ('Expectancy', lambda: f"${self.expectancy():.2f}" if self.expectancy() != float('inf') else "∞"),
            ('Risk-Reward Ratio', lambda: f"{self.risk_reward_ratio():.2f}" if self.risk_reward_ratio() != float('inf') else "∞"),
            ('Sortino Ratio', lambda: f"{self.sortino_ratio():.2f}" if self.sortino_ratio() != float('inf') else "∞"),
            ('Calmar Ratio', lambda: f"{self.calmar_ratio():.2f}" if self.calmar_ratio() != float('inf') else "∞"),
            ('Omega Ratio', lambda: f"{self.omega_ratio():.2f}" if self.omega_ratio() != float('inf') else "∞"),
            ('Kappa Three', lambda: f"{self.kappa_three():.2f}" if self.kappa_three() != float('inf') else "∞"),
            ('Gain to Pain Ratio', lambda: f"{self.gain_to_pain_ratio():.2f}" if self.gain_to_pain_ratio() != float('inf') else "∞"),
            ('Van Sharpe Ratio', lambda: f"{self.van_sharpe_ratio():.2f}" if self.van_sharpe_ratio() != float('inf') else "∞"),
            ('Information Ratio', lambda: f"{self.information_ratio():.2f}" if self.information_ratio() != float('inf') else "∞"),
            ('Payoff Ratio', lambda: f"{self.payoff_ratio():.2f}" if self.payoff_ratio() != float('inf') else "∞"),
            ('Profit per Day', lambda: f"${self.profit_per_day():.2f}" if self.profit_per_day() != float('inf') else "∞"),
            ('R-Squared', lambda: f"{self.r_squared():.2f}" if not np.isnan(self.r_squared()) else "N/A"),
            ('Skewness', lambda: f"{self.skewness():.2f}" if self.skewness() != float('inf') else "∞"),
            ('Kurtosis', lambda: f"{self.kurtosis():.2f}" if self.kurtosis() != float('inf') else "∞"),
            ('Value at Risk (95%)', lambda: f"{self.value_at_risk():.2%}" if self.value_at_risk() != float('inf') else "∞"),
            ('Expected Shortfall (95%)', lambda: f"{self.expected_shortfall():.2%}" if self.expected_shortfall() != float('inf') else "∞"),
            ('Modified Sharpe Ratio', lambda: f"{self.modified_sharpe_ratio():.2f}" if self.modified_sharpe_ratio() != float('inf') else "∞"),
            ('Sterling Ratio', lambda: f"{self.sterling_ratio():.2f}" if self.sterling_ratio() != float('inf') else "∞"),
            ('Burke Ratio', lambda: f"{self.burke_ratio():.2f}" if self.burke_ratio() != float('inf') else "∞"),
            ('Tail Ratio', lambda: f"{self.tail_ratio():.2f}" if self.tail_ratio() != float('inf') else "∞"),
            ('Upside Potential Ratio', lambda: f"{self.upside_potential_ratio():.2f}" if not np.isnan(self.upside_potential_ratio()) else "N/A"),
            ('Rachev Ratio', lambda: f"{self.rachev_ratio():.2f}" if self.rachev_ratio() != float('inf') else "∞"),
            ('Pain Index', lambda: f"{self.pain_index():.2f}" if self.pain_index() != float('inf') else "∞"),
            ('Ulcer Performance Index', lambda: f"{self.ulcer_performance_index():.2f}" if self.ulcer_performance_index() != float('inf') else "∞"),
            ('Serenity Index', lambda: f"{self.serenity_index():.2f}" if self.serenity_index() != float('inf') else "∞"),
            ('Bernardo Ledoit Ratio', lambda: f"{self.bernardo_ledoit_ratio():.2f}" if self.bernardo_ledoit_ratio() != float('inf') else "∞"),
            ('K-Ratio', lambda: f"{self.k_ratio():.2f}" if self.k_ratio() != float('inf') else "∞"),
            ('Prospect Ratio', lambda: f"{self.prospect_ratio():.2f}" if self.prospect_ratio() != float('inf') else "∞"),
            ('Jensen\'s Alpha', lambda: f"{self.jensens_alpha():.2f}" if self.jensens_alpha() != float('inf') else "∞"),
            ('Tracking Error', lambda: f"{self.tracking_error():.2f}" if self.tracking_error() != float('inf') else "∞"),
        ]
        return metrics

    def filter_by_market(self, market):
        if self.trades.empty:
            self.filtered_trades = self.trades
            return
        if market and market != "All Markets":
            self.filtered_trades = self.trades[
            (self.trades['MarketName'] == market) &
            (self.trades['DateUtc'].dt.date >= self.start_date) &
            (self.trades['DateUtc'].dt.date <= self.end_date)
            ]
        else:
            self.filtered_trades = self.trades[
            (self.trades['DateUtc'].dt.date >= self.start_date) &
            (self.trades['DateUtc'].dt.date <= self.end_date)
            ]
                   
        self.calculate_metrics()

    def reset_market_filter(self):
        self.filtered_trades = self.trades.copy()
        self.calculate_metrics()

    def calculate_metrics(self):
        if self.filtered_trades.empty:
            logging.warning("No trades available for metric calculation")
            return

        self.returns = self.calculate_returns()
        self.start_date = self.filtered_trades['DateUtc'].min().date() if not self.filtered_trades.empty else None
        self.end_date = self.filtered_trades['DateUtc'].max().date() if not self.filtered_trades.empty else None
        
        # Recalculate basic metrics
        self.total_trades_count = self.total_trades()
        self.win_rate_value = format_value(self.win_rate())
        self.profit_factor_value = format_value(self.profit_factor())
        self.sharpe_ratio_value = format_value(self.sharpe_ratio())
        self.max_drawdown_percentage = format_value(self.max_drawdown())
        self.max_drawdown_dollar = format_value(self.max_drawdown_dollars())
        self.average_trade_value = format_value(self.average_trade())
        self.expectancy_value = format_value(self.expectancy())
        
        # Recalculate advanced metrics
        self.sortino_ratio_value = format_value(self.sortino_ratio())
        self.calmar_ratio_value = format_value(self.calmar_ratio())
        self.omega_ratio_value = format_value(self.omega_ratio())
        self.information_ratio_value = format_value(self.information_ratio())
        
        # Calculate Net Deposits
        try:
            self.net_deposits_value = format_value(self.net_deposits())
        except Exception as e:
            logging.error(f"Error calculating Net Deposits: {str(e)}")
            self.net_deposits_value = "N/A"
        
        # Calculate Net Withdrawls
        try:
            self.net_withdrawls_value = format_value(self.net_withdrawls())
        except Exception as e:
            logging.error(f"Error calculating Net Withdrawls: {str(e)}")
            self.net_deposits_value = "N/A"

        # Add more metrics here as needed

    def get_deposits(self):
        try:
            deposits = self.filtered_trades[(self.filtered_trades['Summary'] == 'Cash In')]
            return deposits['PL Amount'].sum()
        except Exception as e:
            logging.error(f"Error in get_deposits: {str(e)}")
            return 0

    def get_withdrawals(self):
        try:
            withdrawals = self.filtered_trades[(self.filtered_trades['Summary'] == 'Cash Out')]
            return withdrawals['PL Amount'].sum()
        except Exception as e:
            logging.error(f"Error in get_withdrawals: {str(e)}")
            return 0

    def net_deposits(self):
        try:
            deposits = self.get_deposits()
            withdrawals = self.get_withdrawals()
            return deposits - withdrawals
        except Exception as e:
            logging.error(f"Error in net_deposits calculation: {str(e)}")
            return float('nan')

    def net_withdrawls(self):
        try:
            deposits = self.get_deposits()
            withdrawals = self.get_withdrawals()
            return deposits - withdrawals
        except Exception as e:
            logging.error(f"Error in net_deposits calculation: {str(e)}")
            return float('nan')

    def get_deal_trades(self):
        return self.filtered_trades[self.filtered_trades['Transaction type'] == 'DEAL']
        
    def total_profit(self):
        return self.profitable_amount() - self.loss_amount()

    def return_rate(self):
        if self.filtered_trades.empty or len(self.filtered_trades) < 2:
            return 0
        initial_balance = self.filtered_trades['Balance'].iloc[0]
        final_balance = self.filtered_trades['Balance'].iloc[-1]
        return (final_balance / initial_balance) - 1

    def profit_per_day(self):
        if self.filtered_trades.empty:
            return 0
        total_profit = self.total_profit()
        days = (self.filtered_trades['DateUtc'].max() - self.filtered_trades['DateUtc'].min()).days + 1
        return total_profit / max(days, 1)  # Avoid division by zero

# Example usage:
# metrics = TradingMetrics('trades.csv')
# metrics.generate_report()