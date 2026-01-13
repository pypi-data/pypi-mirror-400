"""Main client class for the Prediction Markets API."""

from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class Client:
    """
    Client for interacting with the Prediction Markets API.

    Usage:
        client = Client(api_key="pk_live_your_key")
        markets = client.get_markets(venue="kalshi", limit=50)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://predictmarket-api.fragrant-pond-ef3c.workers.dev",
        timeout: float = 60.0,
    ):
        """
        Initialize the API client.

        Args:
            api_key: Your API key (starts with pk_live_)
            base_url: Base URL of the API (default: production URL)
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValueError("API key is required")

        if not api_key.startswith("pk_live_") and not api_key.startswith("pk_test_"):
            raise ValueError("Invalid API key format. Must start with pk_live_ or pk_test_")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "User-Agent": "prediction-markets-python/0.1.0",
            },
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/v1/raw/markets-universe")
            params: Query parameters
            json: JSON body

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: Invalid API key
            ValidationError: Invalid parameters
            NotFoundError: Resource not found
            RateLimitError: Rate limit exceeded
            ServerError: Server error
            APIError: Other API errors
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
            )

            # Handle error responses
            if response.status_code >= 400:
                self._handle_error(response)

            return response.json()

        except httpx.TimeoutException:
            raise APIError("Request timed out", status_code=408)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")

    def _handle_error(self, response: httpx.Response):
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            message = error_data.get("message", "Unknown error")
            error_type = error_data.get("error", "Unknown")
        except Exception:
            message = response.text or f"HTTP {response.status_code}"
            error_type = "Unknown"

        if response.status_code == 401:
            raise AuthenticationError(
                message or "Invalid or missing API key",
                status_code=401,
                response=error_data if 'error_data' in locals() else None,
            )
        elif response.status_code == 400:
            raise ValidationError(
                message or "Invalid request parameters",
                status_code=400,
                response=error_data if 'error_data' in locals() else None,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                message or "Resource not found",
                status_code=404,
                response=error_data if 'error_data' in locals() else None,
            )
        elif response.status_code == 429:
            raise RateLimitError(
                message or "Rate limit exceeded",
                status_code=429,
                response=error_data if 'error_data' in locals() else None,
            )
        elif response.status_code >= 500:
            raise ServerError(
                message or "Server error",
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None,
            )
        else:
            raise APIError(
                message,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None,
            )

    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        limit_per_page: int = 100,
        max_items: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Automatically paginate through all results.

        Args:
            endpoint: API endpoint
            params: Query parameters
            limit_per_page: Items per page
            max_items: Maximum total items to fetch (None = all)

        Returns:
            List of all items
        """
        params = params or {}
        all_items = []
        offset = 0

        while True:
            params["limit"] = limit_per_page
            params["offset"] = offset

            response = self._request("GET", endpoint, params=params)
            items = response.get("items", [])

            if not items:
                break

            all_items.extend(items)

            # Check if we've reached max items
            if max_items and len(all_items) >= max_items:
                return all_items[:max_items]

            # Check if there are more results
            has_more = response.get("has_more", False)
            if not has_more:
                break

            offset += len(items)

        return all_items

    # ===== RAW ENDPOINTS =====

    def get_markets(
        self,
        venue: Optional[str] = None,
        factor_category: Optional[str] = None,
        tags: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        auto_paginate: bool = False,
    ) -> Dict[str, Any]:
        """
        Get markets from the markets_universe table.

        Args:
            venue: Filter by venue (e.g., "kalshi", "polymarket")
            factor_category: Filter by factor category
            tags: Filter by tags (markets containing this tag)
            limit: Maximum results per page
            offset: Number of results to skip
            auto_paginate: Automatically fetch all pages

        Returns:
            Response with markets data

        Example:
            markets = client.get_markets(venue="kalshi", limit=50)
            for market in markets["items"]:
                print(market["title"])
        """
        params = {"venue": venue, "factor_category": factor_category, "tags": tags}
        params = {k: v for k, v in params.items() if v is not None}

        if auto_paginate:
            items = self._paginate("/v1/raw/markets-universe", params, limit)
            return {"items": items, "total": len(items)}

        params["limit"] = limit
        params["offset"] = offset
        return self._request("GET", "/v1/raw/markets-universe", params=params)

    def get_trades(
        self,
        venue: Optional[str] = None,
        venue_ticker: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        auto_paginate: bool = False,
    ) -> Dict[str, Any]:
        """
        Get trade history from trades table.

        Args:
            venue: Filter by venue (e.g., "kalshi", "polymarket")
            venue_ticker: Filter by market ticker
            start_date: Filter trades after this date (ISO format)
            end_date: Filter trades before this date (ISO format)
            limit: Maximum results per page
            offset: Number of results to skip
            auto_paginate: Automatically fetch all pages

        Returns:
            Response with trades data

        Example:
            trades = client.get_trades(
                venue="kalshi",
                venue_ticker="KXBTC-24DEC29",
                limit=1000
            )
        """
        params = {
            "venue": venue,
            "venue_ticker": venue_ticker,
            "start_date": start_date,
            "end_date": end_date,
        }
        params = {k: v for k, v in params.items() if v is not None}

        if auto_paginate:
            items = self._paginate("/v1/raw/trades", params, limit)
            return {"items": items, "total": len(items)}

        params["limit"] = limit
        params["offset"] = offset
        return self._request("GET", "/v1/raw/trades", params=params)

    def get_market_daily_prices(
        self,
        venue: Optional[str] = None,
        venue_ticker: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get daily market prices.

        Args:
            venue: Filter by venue
            venue_ticker: Filter by market ticker
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum results
            offset: Results to skip

        Returns:
            Response with daily price data
        """
        params = {
            "venue": venue,
            "venue_ticker": venue_ticker,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/raw/market-daily-prices", params=params)

    def get_factor_returns(
        self,
        factor_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get factor returns time series.

        Args:
            factor_name: Specific factor to filter by
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum results
            offset: Results to skip

        Returns:
            Response with factor returns data
        """
        params = {
            "factor_name": factor_name,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/raw/factor-returns", params=params)

    def get_factor_summary(
        self,
        factor_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get factor summary statistics.

        Args:
            factor_name: Specific factor to filter by
            limit: Maximum results
            offset: Results to skip

        Returns:
            Response with factor summary data
        """
        params = {"factor_name": factor_name, "limit": limit, "offset": offset}
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/raw/factor-summary", params=params)

    def get_stock_factor_betas(
        self,
        stock_ticker: Optional[str] = None,
        factor_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get stock-to-factor beta estimates.

        Args:
            stock_ticker: Filter by stock ticker
            factor_name: Filter by factor name
            limit: Maximum results
            offset: Results to skip

        Returns:
            Response with beta estimates
        """
        params = {
            "stock_ticker": stock_ticker,
            "factor_name": factor_name,
            "limit": limit,
            "offset": offset,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/raw/stock-factor-betas", params=params)

    def get_thematic_correlations(
        self,
        theme: Optional[str] = None,
        stock_ticker: Optional[str] = None,
        market_ticker: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get thematic correlations between stocks and markets.

        Args:
            theme: Filter by theme
            stock_ticker: Filter by stock ticker
            market_ticker: Filter by market ticker
            limit: Maximum results
            offset: Results to skip

        Returns:
            Response with correlation data
        """
        params = {
            "theme": theme,
            "stock_ticker": stock_ticker,
            "market_ticker": market_ticker,
            "limit": limit,
            "offset": offset,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/raw/thematic-correlations", params=params)

    def get_markets_by_tags(
        self,
        tag: Optional[str] = None,
        venue: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get markets grouped by tags.

        Args:
            tag: Filter by tag (markets containing this tag)
            venue: Filter by venue
            limit: Maximum results
            offset: Results to skip

        Returns:
            Response with tagged markets
        """
        params = {"tag": tag, "venue": venue, "limit": limit, "offset": offset}
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/raw/custom-markets-by-tags", params=params)

    # ===== PROCESSED ENDPOINTS =====

    def get_processed_market_prices(
        self,
        venue_ticker: str,
        venue: Optional[str] = None,
        days_back: int = 365,
    ) -> Dict[str, Any]:
        """
        Get processed daily prices for a market with enhanced analytics.

        Args:
            venue_ticker: Market ticker (required)
            venue: Venue name
            days_back: Number of days of history

        Returns:
            Response with processed price data including summary statistics
        """
        # Note: API expects 'ticker' parameter, not 'venue_ticker'
        params = {"ticker": venue_ticker, "venue": venue, "days_back": days_back}
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/processed/market-daily-prices", params=params)

    def get_processed_factor_returns(
        self,
        factor_name: Optional[str] = None,
        days_back: int = 365,
    ) -> Dict[str, Any]:
        """
        Get processed factor returns with summary statistics.

        Args:
            factor_name: Specific factor
            days_back: Number of days of history

        Returns:
            Response with factor returns and summary
        """
        params = {"factor_name": factor_name, "days_back": days_back}
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/processed/factor-returns", params=params)

    def get_processed_correlations(
        self,
        theme: Optional[str] = None,
        stock_ticker: Optional[str] = None,
        market_ticker: Optional[str] = None,
        min_correlation: Optional[float] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get processed thematic correlations with filtering.

        Args:
            theme: Filter by theme
            stock_ticker: Filter by stock
            market_ticker: Filter by market ticker
            min_correlation: Minimum Pearson correlation threshold
            limit: Maximum results

        Returns:
            Response with filtered correlations (ordered by pearson_correlation)
        """
        params = {
            "theme": theme,
            "stock_ticker": stock_ticker,
            "market_ticker": market_ticker,
            "min_correlation": min_correlation,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/processed/thematic-correlations", params=params)

    def get_processed_stock_betas(
        self,
        stock_ticker: str,
        min_r_squared: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get processed stock factor betas with R² filtering.

        Args:
            stock_ticker: Stock ticker (required)
            min_r_squared: Minimum R² threshold

        Returns:
            Response with beta estimates
        """
        params = {"stock_ticker": stock_ticker, "min_r_squared": min_r_squared}
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/v1/processed/stock-factor-betas", params=params)

    def get_factor_trade_impacts(
        self,
        stock_ticker: str,
        top_n: Optional[int] = None,
        factor_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the prediction markets that contributed to a stock's factor betas.

        This endpoint identifies which specific prediction markets drive the
        factor exposures for a given stock, showing their relative contributions
        and recent price movements.

        Args:
            stock_ticker: Stock ticker (required)
            top_n: Number of top contributing markets to return (optional, default: 20 on server)
            factor_filter: Optional factor to filter by (e.g., "Tech", "Politics", "Macro", "Crypto")

        Returns:
            Response with:
            - success: Boolean indicating success
            - stockTicker: The requested stock ticker
            - betas: Dictionary of the stock's factor betas
            - topImpacts: List of top N markets by contribution
            - impactsByFactor: Breakdown of impacts by factor category
            - totalMarketsAnalyzed: Total number of markets analyzed

        Example:
            # Get top contributing markets for NVDA (uses server default)
            impacts = client.get_factor_trade_impacts(stock_ticker="NVDA")

            # Get top 10 contributing markets for NVDA
            impacts = client.get_factor_trade_impacts(
                stock_ticker="NVDA",
                top_n=10
            )

            # Filter for only Tech factor impacts
            tech_impacts = client.get_factor_trade_impacts(
                stock_ticker="NVDA",
                top_n=5,
                factor_filter="Tech"
            )

            # Process results
            for impact in impacts["topImpacts"]:
                print(f"{impact['marketTitle']}: {impact['contribution']:.4f}")
                print(f"  Factor: {impact['factorCategory']}")
                print(f"  Relative Weight: {impact['relativeWeight']:.2%}")
        """
        params = {"stock_ticker": stock_ticker}

        if top_n is not None:
            params["top_n"] = top_n
        if factor_filter:
            params["factor_filter"] = factor_filter

        return self._request("GET", "/v1/processed/factor-trade-impacts", params=params)

    # ===== UTILITY METHODS =====

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.

        Returns:
            Health check response
        """
        return self._request("GET", "/health")
