class PortfolioService:

    def get_demo_portfolio(self) -> list[dict]:
        return [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "average_price": 180.00,
                "current_price": 245.50,
            },
            {
                "symbol": "MSFT",
                "quantity": 8,
                "average_price": 410.00,
                "current_price": 510.25,
            },
            {
                "symbol": "NVDA",
                "quantity": 15,
                "average_price": 120.00,
                "current_price": 175.40,
            },
            {
                "symbol": "GOOGL",
                "quantity": 6,
                "average_price": 165.00,
                "current_price": 285.75,
            },
        ]
