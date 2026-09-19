import asyncio

import httpx

from app.config.settings import settings


class AlphaVantageClient:

    BASE_URL = "https://www.alphavantage.co/query"

    _rate_limit_lock = asyncio.Lock()
    _last_request_time = 0.0
    _min_request_interval = 1.1

    async def _request(self, params: dict) -> dict:
        async with self._rate_limit_lock:
            current_time = asyncio.get_running_loop().time()

            elapsed = current_time - self._last_request_time

            if elapsed < self._min_request_interval:
                await asyncio.sleep(
                    self._min_request_interval - elapsed
                )

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                )

                response.raise_for_status()

                data = response.json()

            self._last_request_time = (
                asyncio.get_running_loop().time()
            )

            return data

    async def get_global_quote(
        self,
        symbol: str,
    ) -> dict:

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol.upper(),
            "apikey": settings.alpha_vantage_api_key,
        }

        return await self._request(params)

    async def get_historical_prices(
        self,
        symbol: str,
        outputsize: str = "compact",
    ) -> dict:

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper(),
            "outputsize": outputsize,
            "apikey": settings.alpha_vantage_api_key,
        }

        return await self._request(params)

    async def get_company_overview(
        self,
        symbol: str,
    ) -> dict:

        params = {
            "function": "OVERVIEW",
            "symbol": symbol.upper(),
            "apikey": settings.alpha_vantage_api_key,
        }

        return await self._request(params)

    async def get_financial_news(
        self,
        ticker: str | None = None,
        limit: int = 10,
    ) -> dict:

        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": settings.alpha_vantage_api_key,
            "limit": limit,
        }

        if ticker:
            params["tickers"] = ticker.upper()

        return await self._request(params)