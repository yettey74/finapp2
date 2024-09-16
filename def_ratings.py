from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class RatingOperations:

    def __init__(self):
        self.trader_rating_label = None
        self.trader_rating_widget = None

    def create_trader_rating_widget(self):
        self.trader_rating_widget = QWidget()
        layout = QVBoxLayout(self.trader_rating_widget)
        self.trader_rating_label = QLabel("Trader Rating: N/A")
        self.trader_rating_label.setStyleSheet("font-weight: bold; color: #00ff00; font-size: 14px;")
        layout.addWidget(self.trader_rating_label)
        return self.trader_rating_widget
    
    def create_trader_rating(self):
        if self.metrics.filtered_trades.empty:
            return 0.0
        
        weights = {
            'win_rate': 0.15,           
        }
        scores = {
            'win_rate': min(self.metrics.win_rate(), 1),            
        }
        
        return sum(weights[metric] * scores[metric] for metric in weights)

    def calculate_trader_rating(self):
        if self.metrics.filtered_trades.empty:
            return 0.0
        
        weights = {
            'win_rate': 0.15,
            'profit_factor': 0.15,
            'sharpe_ratio': 0.15,
            'sortino_ratio': 0.15,
            'calmar_ratio': 0.15,
            'net_deposits_ratio': 0.25  # New weight for net deposits ratio
        }
        
        net_deposits = self.metrics.net_deposits()
        total_profit = self.metrics.total_profit()
        net_deposits_ratio = total_profit / net_deposits if net_deposits > 0 else 0

        scores = {
            'win_rate': min(self.metrics.win_rate(), 1),
            'profit_factor': min(self.metrics.profit_factor() / 3, 1) if self.metrics.profit_factor() not in [float('inf'), float('-inf')] else 1,
            'sharpe_ratio': min(max(self.metrics.sharpe_ratio(), 0) / 3, 1) if self.metrics.sharpe_ratio() not in [float('inf'), float('-inf')] else 1,
            'sortino_ratio': min(max(self.metrics.sortino_ratio(), 0) / 3, 1) if self.metrics.sortino_ratio() not in [float('inf'), float('-inf')] else 1,
            'calmar_ratio': min(max(self.metrics.calmar_ratio(), 0) / 3, 1) if self.metrics.calmar_ratio() not in [float('inf'), float('-inf')] else 1,
            'net_deposits_ratio': min(net_deposits_ratio, 1)  # New score for net deposits ratio
        }
        
        return sum(weights[metric] * scores[metric] for metric in weights)
    
    def update_trader_rating(self):
        if not self.metrics.filtered_trades.empty:
            rating = self.calculate_trader_rating()
            self.trader_rating_label.setText(f"Trader Rating: {rating:.2%}")
        else:
            self.trader_rating_label.setText("Trader Rating: N/A")

    def delete_trader_rating(self):
        if self.trader_rating_label:
            self.trader_rating_label.setText("Trader Rating: N/A")

   