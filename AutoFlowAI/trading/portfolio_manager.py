"""
إدارة المحفظة
"""

class PortfolioManager:
    def __init__(self, initial_balance=100000):
        self.initial_balance = initial_balance
        self.cash_balance = initial_balance
        self.positions = {}
        self.value_history = [initial_balance]

    def get_total_value(self):
        return self.cash_balance + sum(p.current_value for p in self.positions.values())

    def rebalance_portfolio(self, target_allocation):
        print("⚖️ إعادة توازن المحفظة...")
        return []

class Transaction:
    def __init__(self, id, symbol, side, quantity, price, fee=0.0):
        self.id = id
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.fee = fee
