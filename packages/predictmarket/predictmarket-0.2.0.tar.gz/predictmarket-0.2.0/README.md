# Prediction Markets API - Python Client

Official Python client library for the Prediction Markets API.

## Installation

```bash
pip install predictmarket
```

## Quick Start

```python
from predictmarket import Client

# Initialize client with your API key
client = Client(api_key="pk_live_your_key_here")

# Get markets from Kalshi
markets = client.get_markets(venue="kalshi", limit=50)
for market in markets["items"]:
    print(f"{market['venue_ticker']}: {market['title']}")

# Get recent trades
trades = client.get_trades(
    venue="kalshi",
    start_date="2025-01-01",
    limit=1000
)

# Get factor returns with summary
factor_data = client.get_processed_factor_returns(
    factor_name="Macro",
    days_back=90
)
print(f"Returns: {factor_data['returns']}")
print(f"Summary: {factor_data['summary']}")
```

## Features

- ✅ **Complete API Coverage**: Access all raw and processed endpoints
- ✅ **Automatic Pagination**: Fetch all results automatically
- ✅ **Type-Safe**: Full type hints for better IDE support
- ✅ **Error Handling**: Detailed exceptions for different error types
- ✅ **Easy to Use**: Intuitive Pythonic interface

## Getting Your API Key

1. Contact us at info@predictmarket.ai to request API access
2. Provide your name, organization, and use case
3. Once approved, you'll receive an API key (starts with `pk_live_`)
4. Keep your API key secure - treat it like a password!

## Available Methods

### Raw Data Endpoints

```python
# Markets
client.get_markets(venue=None, factor_category=None, tags=None)

# Trades
client.get_trades(venue=None, venue_ticker=None, start_date=None, end_date=None)

# Daily Prices
client.get_market_daily_prices(venue=None, venue_ticker=None, start_date=None, end_date=None)

# Factor Data
client.get_factor_returns(factor_name=None, start_date=None, end_date=None)
client.get_factor_summary(factor_name=None)

# Stock-Factor Relationships
client.get_stock_factor_betas(stock_ticker=None)

# Correlations
client.get_thematic_correlations(theme=None, stock_ticker=None, market_ticker=None)

# Markets by Tags
client.get_markets_by_tags(tag=None, venue=None)
```

### Processed Analytics Endpoints

```python
# Enhanced daily prices with analytics
client.get_processed_market_prices(venue_ticker="KXBTC-24DEC29", days_back=365)

# Factor returns with summary statistics
client.get_processed_factor_returns(factor_name="Macro", days_back=90)

# Filtered correlations
client.get_processed_correlations(theme="crypto", min_correlation=0.5)

# Stock betas with R² filtering
client.get_processed_stock_betas(stock_ticker="AAPL", min_r_squared=0.3)

# Factor trade impacts - see which markets drive stock factor betas
client.get_factor_trade_impacts(stock_ticker="NVDA", top_n=10, factor_filter="Tech")
```

## Advanced Usage

### Automatic Pagination

```python
# Fetch all markets across all pages
markets = client.get_markets(venue="kalshi", auto_paginate=True)
print(f"Total markets: {len(markets['items'])}")
```

### Context Manager

```python
# Automatically close connection
with Client(api_key="pk_live_xxx") as client:
    markets = client.get_markets(limit=100)
    # Process markets...
# Connection automatically closed
```

### Error Handling

```python
from predictmarket import (
    Client,
    AuthenticationError,
    ValidationError,
    RateLimitError
)

try:
    client = Client(api_key="pk_live_xxx")
    markets = client.get_markets(limit=50)
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid parameters: {e.message}")
except RateLimitError:
    print("Rate limit exceeded - please wait")
```

## Examples

### Example 1: Track Market Sentiment

```python
from predictmarket import Client
from datetime import datetime, timedelta

client = Client(api_key="pk_live_xxx")

# Get markets about AI
ai_markets = client.get_markets_by_tags(tag="ai", limit=100)

for market in ai_markets["items"]:
    # Get recent price history
    prices = client.get_market_daily_prices(
        venue_ticker=market["venue_ticker"],
        start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    )

    if prices["items"]:
        latest = prices["items"][0]
        print(f"{market['title']}: {latest['close_price']:.2f}")
```

### Example 2: Analyze Factor Performance

```python
from predictmarket import Client

client = Client(api_key="pk_live_xxx")

# Get factor returns with summary
factors = ["Macro", "Tech", "Crypto"]

for factor in factors:
    data = client.get_processed_factor_returns(
        factor_name=factor,
        days_back=365
    )

    summary = data["summary"]
    print(f"\n{factor} Factor:")
    print(f"  Mean Return: {summary['mean_return']}")
    print(f"  Sharpe Ratio: {summary['sharpe_ratio']}")
    print(f"  Observations: {summary['num_observations']}")
```

### Example 3: Find Stock-Market Correlations

```python
from predictmarket import Client

client = Client(api_key="pk_live_xxx")

# Find strong correlations for AAPL
correlations = client.get_processed_correlations(
    stock_ticker="AAPL",
    min_correlation=0.7  # Only strong correlations
)

print(f"Found {len(correlations['items'])} strong correlations for AAPL:")
for corr in correlations["items"][:10]:
    print(f"  {corr['market_ticker']}: {corr['pearson_correlation']:.3f}")
```

### Example 4: Analyze Which Markets Drive Stock Factor Exposures

```python
from predictmarket import Client

client = Client(api_key="pk_live_xxx")

# Get the top markets driving NVDA's factor exposures
impacts = client.get_factor_trade_impacts(
    stock_ticker="NVDA",
    top_n=10
)

print(f"\nStock: {impacts['stockTicker']}")
print(f"Factor Betas: {impacts['betas']}")
print(f"\nTop {len(impacts['topImpacts'])} Contributing Markets:")

for impact in impacts["topImpacts"]:
    print(f"\n{impact['marketTitle']}")
    print(f"  Factor: {impact['factorCategory']}")
    print(f"  Beta: {impact['beta']:.6f}")
    print(f"  Relative Weight: {impact['relativeWeight']:.2%}")
    print(f"  Contribution: {impact['contribution']:.6f}")
    if impact['recentPrice']:
        print(f"  Recent Price: {impact['recentPrice']:.2f}")
    if impact['priceChange']:
        print(f"  Price Change: {impact['priceChange']:.2f}%")

# Get impacts for a specific factor only
tech_impacts = client.get_factor_trade_impacts(
    stock_ticker="NVDA",
    top_n=5,
    factor_filter="Tech"
)

print(f"\nTop Tech Factor Markets for NVDA:")
for impact in tech_impacts["impactsByFactor"]["Tech"]["topImpacts"]:
    print(f"  - {impact['marketTitle']}: {impact['relativeWeight']:.2%}")
```

## API Reference

For complete API documentation and data schemas, visit the [GitHub repository](https://github.com/predict-market/api-python)

## Requirements

- Python 3.8+
- `httpx` (automatically installed)

## License

MIT License - see LICENSE file for details

## Support

- Documentation: [GitHub README](https://github.com/predict-market/api-python/blob/main/README.md)
- Issues: [GitHub Issues](https://github.com/predict-market/api-python/issues)
- Email: info@predictmarket.ai
