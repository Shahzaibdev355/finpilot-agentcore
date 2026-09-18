import httpx

from app.config.settings import settings


class FrankfurterClient:

    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> dict:

        url = (
            f"{settings.frankfurter_base_url}"
            f"/rate/{from_currency.upper()}/{to_currency.upper()}"
        )

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)

            response.raise_for_status()

            return response.json()
