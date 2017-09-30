from ._classes import Strategy, Order

import random

class RandomStrategy(Strategy):
    """
    This strategy is used for testing the simulator
    """

    def __init__(self, money, portfolio, from_date, to_date):
        super().__init__(money, portfolio, from_date, to_date)

    def execute(self, today):
        super().execute(today)

        # select a random ticker
        tickers = self.get_tickers()
        ticker = random.choice(tickers)

        instrument = self.get_instrument(ticker)

        # random input
        action = random.choice(["buy", "sell"])
        quantity = random.randint(1,100)
        price = instrument.get_price(today)
        if random.random() < 0.2:
            price = None
        
        order = Order(ticker, action, quantity, price)
        
        return [order]