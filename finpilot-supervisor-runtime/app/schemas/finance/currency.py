from pydantic import BaseModel


class CurrencyConversion(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    rate: float
    converted_amount: float
    date: str
