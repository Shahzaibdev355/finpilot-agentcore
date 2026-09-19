from langchain_core.tools import tool

from app.schemas.finance.currency import CurrencyConversion
from app.services.frankfurter.client import FrankfurterClient


client = FrankfurterClient()


@tool
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> CurrencyConversion:
    """
    Convert an amount from one currency to another using
    the latest available exchange rate.

    Args:
        amount: Amount to convert.
        from_currency: Three-letter source currency code, such as USD.
        to_currency: Three-letter target currency code, such as EUR.
    """

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    data = await client.get_exchange_rate(
        from_currency=from_currency,
        to_currency=to_currency,
    )

    rate = float(data["rate"])
    converted_amount = amount * rate

    return CurrencyConversion(
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency,
        rate=rate,
        converted_amount=converted_amount,
        date=data["date"],
    )
