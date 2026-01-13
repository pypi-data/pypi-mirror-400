# Unofficial GuruFocus MCP Server

An MCP (Model Context Protocol) server that exposes GuruFocus financial data to AI assistants like Claude. Built with FastMCP for seamless integration with Claude Desktop and other MCP clients.

## Features

- **54 Analysis Tools**: Stocks, gurus, insiders, politicians, economic data, and more
- **Data Resources**: Direct access to formatted financial data via URI templates
- **JMESPath Query Support**: Filter and transform responses inline to reduce context usage
- **Schema Resources**: AI agents can discover data structures to write correct queries
- **Multiple Transports**: stdio (Claude Desktop), HTTP/SSE, WebSocket
- **Error Handling**: Graceful handling of invalid symbols, rate limits, and API errors
- **TOON Format**: 30-60% token reduction vs JSON for efficient LLM contexts

## Requirements

- Python 3.11+
- GuruFocus API token ([Get one here](https://www.gurufocus.com/api.php))

## Installation

```bash
pip install gurufocus-mcp
```

Or with uv:

```bash
uv add gurufocus-mcp
```

## Quick Start

### 1. Set your API token

```bash
export GURUFOCUS_API_TOKEN=your-token-here
```

### 2. Run the server

```bash
# Default stdio transport (for Claude Desktop)
gurufocus-mcp

# HTTP transport for web clients
gurufocus-mcp --transport http --port 8000
```

## Claude Desktop Integration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gurufocus": {
      "command": "gurufocus-mcp",
      "env": {
        "GURUFOCUS_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

If using uv or a virtual environment:

```json
{
  "mcpServers": {
    "gurufocus": {
      "command": "uv",
      "args": ["run", "gurufocus-mcp"],
      "env": {
        "GURUFOCUS_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

After adding the configuration, restart Claude Desktop. You should see the GuruFocus tools available in Claude's interface.

## Available Tools

### Stock Tools (21 tools)

| Tool                          | Description                                                      |
| ----------------------------- | ---------------------------------------------------------------- |
| `get_stock_summary`           | Comprehensive overview: price, valuation, GF Score               |
| `get_stock_financials`        | Financial statements (income, balance sheet, cash flow)          |
| `get_stock_keyratios`         | Key financial ratios (profitability, liquidity, growth)          |
| `get_stock_quote`             | Real-time stock quote with OHLCV data                            |
| `get_stock_price_history`     | Historical price data                                            |
| `get_stock_price_ohlc`        | Historical OHLC price bars for technical analysis                |
| `get_stock_volume`            | Historical trading volume data                                   |
| `get_stock_unadjusted_price`  | Historical unadjusted (pre-split) prices                         |
| `get_stock_dividends`         | Dividend history                                                 |
| `get_stock_current_dividend`  | Current dividend yield and payment info                          |
| `get_stock_analyst_estimates` | Analyst earnings/revenue estimates                               |
| `get_stock_insider_trades`    | Insider trading activity for a stock                             |
| `get_stock_gurus`             | Guru holdings in a specific stock                                |
| `get_stock_executives`        | Company executives and directors                                 |
| `get_stock_trades_history`    | Guru trades history for a stock                                  |
| `get_stock_operating_data`    | Operating metrics and KPIs                                       |
| `get_stock_segments_data`     | Business and geographic segment breakdown                        |
| `get_stock_ownership`         | Ownership breakdown (institutional, insider, float)              |
| `get_stock_indicator_history` | Historical ownership indicators                                  |
| `get_stock_indicators`        | List of 240+ available stock indicators                          |
| `get_stock_indicator`         | Time series data for a specific indicator                        |

### Insider Tools (7 tools)

| Tool                      | Description                              |
| ------------------------- | ---------------------------------------- |
| `get_insider_updates`     | Recent insider transaction updates       |
| `get_insider_ceo_buys`    | CEO buy transactions (bullish signal)    |
| `get_insider_cfo_buys`    | CFO buy transactions                     |
| `get_insider_cluster_buys`| Cluster buy signals (multiple insiders)  |
| `get_insider_double_buys` | Double-down buy signals                  |
| `get_insider_triple_buys` | Triple-down buy signals                  |
| `get_insider_list`        | Browse known insiders                    |

### Guru Tools (4 tools)

| Tool                    | Description                               |
| ----------------------- | ----------------------------------------- |
| `get_gurulist`          | List all tracked super investors          |
| `get_guru_picks`        | Guru's stock picks and trading activity   |
| `get_guru_aggregated`   | Guru's complete portfolio with holdings   |
| `get_guru_realtime_picks`| Recent trading activity across all gurus |

### Politician Tools (2 tools)

| Tool                         | Description                            |
| ---------------------------- | -------------------------------------- |
| `get_politicians`            | List tracked politicians               |
| `get_politician_transactions`| Politician stock transactions          |

### Reference Data Tools (6 tools)

| Tool                  | Description                               |
| --------------------- | ----------------------------------------- |
| `get_exchange_list`   | List worldwide stock exchanges            |
| `get_exchange_stocks` | Stocks listed on a specific exchange      |
| `get_index_list`      | List worldwide market indexes             |
| `get_index_stocks`    | Constituent stocks in a market index      |
| `get_country_currency`| Country currency mapping                  |
| `get_funda_updated`   | Recently updated fundamentals             |

### Economic Data Tools (3 tools)

| Tool                     | Description                            |
| ------------------------ | -------------------------------------- |
| `get_economic_indicators`| List available economic indicators     |
| `get_economic_indicator` | Time series for economic indicator     |
| `get_financial_calendar` | Financial calendar (earnings, IPOs)    |

### Personal/Account Tools (6 tools)

| Tool                   | Description                               |
| ---------------------- | ----------------------------------------- |
| `get_api_usage`        | API usage statistics                      |
| `get_user_screeners`   | User's saved screeners                    |
| `get_screener_results` | Run a saved screener                      |
| `get_portfolios`       | User's portfolios                         |
| `get_portfolio_detail` | Portfolio holdings and performance        |
| `get_portfolio_changes`| Portfolio changes over time               |

### ETF Tools (2 tools)

| Tool                  | Description                               |
| --------------------- | ----------------------------------------- |
| `get_etf_list`        | List available ETFs                       |
| `get_etf_sector_weighting` | ETF sector allocation               |

### Analysis Tools (2 tools)

| Tool                  | Description                               |
| --------------------- | ----------------------------------------- |
| `compare_stocks`      | Compare multiple stocks side-by-side      |
| `get_stock_news`      | Recent news for a stock                   |

### Schema Tools (3 tools)

| Tool                       | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `list_schemas`             | List all available model schemas with categories |
| `get_schema`               | Get JSON schema for a specific model           |
| `get_schemas_by_category`  | Get all schemas in a category                  |

## Available Resources

Resources provide direct data access via URI templates:

### Stock Resources

```
gurufocus://stock/{symbol}/summary      - Company overview
gurufocus://stock/{symbol}/gf-score     - GF Score details
gurufocus://stock/{symbol}/valuation    - Valuation metrics
gurufocus://stock/{symbol}/financials   - Financial statements
gurufocus://stock/{symbol}/ratios       - Key financial ratios
gurufocus://stock/{symbol}/dividends    - Dividend information
gurufocus://stock/{symbol}/insiders     - Insider trading
gurufocus://stock/{symbol}/estimates    - Analyst estimates
```

### Guru Resources

```
gurufocus://gurus                       - List of tracked gurus
gurufocus://guru/{guru_id}/picks        - Guru's portfolio
gurufocus://guru/{guru_id}/trades       - Guru's recent trades
gurufocus://stock/{symbol}/gurus        - Gurus holding a stock
```

### Schema Discovery

Schema tools help AI agents understand data structures to write correct JMESPath queries:

```
list_schemas()                          - List all available model schemas with categories
get_schema(model_name)                  - Get JSON schema for a specific model
get_schemas_by_category(category)       - Get schemas by category (e.g., ratios, dividends)
```

Schema resources are also available (but tools are preferred as Claude Desktop doesn't fully support resource templates):

```
gurufocus://schemas                     - List all available model schemas
gurufocus://schemas/{model_name}        - Get JSON schema for a specific model
gurufocus://schemas/category/{category} - Get schemas by category
```

## JMESPath Query Support

Tools that return large datasets support JMESPath queries to filter and transform data inline:

```python
# Get only the last 5 financial periods
get_stock_financials(symbol="AAPL", query="periods[:5]")

# Extract just revenue and profit from each period
get_stock_financials(symbol="AAPL", query="periods[*].{period: period, revenue: revenue, profit: net_income}")

# Get dividend amounts only
get_stock_dividend(symbol="AAPL", query="payments[*].amount")

# Filter insider updates to purchases only
get_insider_updates(query="updates[?type=='P']")
```

JMESPath is the same query language used by AWS CLI. See [jmespath.org](https://jmespath.org/tutorial.html) for more examples.

**Tools with query support:** `get_stock_dividend`, `get_stock_financials`, `get_stock_keyratios`, `get_stock_price_ohlc`, `get_stock_ownership`, `get_stock_indicators`, `get_gurulist`, `get_guru_picks`, `get_insider_updates`

## Example Conversations

### Basic Stock Analysis

```
User: What's the GF Score for Apple?

Claude: [Uses get_gf_score tool]
Apple (AAPL) has a GF Score of 92/100, indicating high quality:
- Financial Strength: 8/10
- Profitability Rank: 10/10
- Growth Rank: 7/10
- Value Rank: 5/10
- Momentum Rank: 8/10
```

### Stock Comparison

```
User: Compare MSFT, GOOGL, and META on valuation metrics

Claude: [Uses compare_stocks tool]
Here's a side-by-side comparison...
```

### Finding Value Opportunities

```
User: Find undervalued tech stocks with high quality scores

Claude: [Uses find_undervalued tool with sector filter]
I found 15 technology stocks trading below their GF Value...
```

### Investment Research

```
User: Create an investment thesis for NVDA

Claude: [Uses investment_thesis prompt + multiple tools]
## Investment Thesis: NVIDIA Corporation

### 1. Company Overview
[Detailed analysis using get_stock_summary]

### 2. Financial Health
[Analysis using get_financials, get_key_ratios]
...
```

## Configuration Options

### Environment Variables

| Variable              | Description              | Default                                  |
| --------------------- | ------------------------ | ---------------------------------------- |
| `GURUFOCUS_API_TOKEN` | Your GuruFocus API token | Required                                 |
| `GURUFOCUS_BASE_URL`  | API base URL             | `https://api.gurufocus.com/public/user/` |
| `MCP_SERVER_NAME`     | Server name for MCP      | `gurufocus-mcp`                          |

### Command Line Options

```bash
gurufocus-mcp [OPTIONS]

Options:
  --transport [stdio|http|sse]  Transport protocol (default: stdio)
  --port PORT                   HTTP server port (default: 8000)
  --host HOST                   HTTP server host (default: 127.0.0.1)
  --help                        Show help message
```

## Error Handling

The server provides helpful error messages for common issues:

### Invalid Symbol
```json
{
  "error": true,
  "error_type": "invalid_symbol",
  "message": "The symbol 'INVALID' was not found or is invalid.",
  "suggestions": [
    "Check that the symbol is spelled correctly",
    "Verify the stock is listed on a supported exchange"
  ]
}
```

### Rate Limiting
```json
{
  "error": true,
  "error_type": "rate_limit",
  "message": "API rate limit exceeded. Try again in 60 seconds.",
  "details": {"retry_after": 60}
}
```

### Authentication
```json
{
  "error": true,
  "error_type": "authentication_error",
  "message": "API authentication failed. Please check your GuruFocus API token."
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest packages/gurufocus-mcp/tests/ -v

# Run specific test file
uv run pytest packages/gurufocus-mcp/tests/test_integration.py -v
```

### Project Structure

```
gurufocus_mcp/
├── __init__.py          # Package exports
├── config.py            # Configuration management
├── server.py            # MCP server setup
├── formatting.py        # TOON/JSON formatters
├── tools/               # Tool handlers (54 tools)
│   ├── stocks.py        # Stock data tools
│   ├── insiders.py      # Insider activity tools
│   ├── gurus.py         # Guru/institutional investor tools
│   ├── politicians.py   # Politician trading tools
│   ├── economic.py      # Economic data tools
│   ├── reference.py     # Reference data tools
│   ├── personal.py      # Account/portfolio tools
│   ├── etfs.py          # ETF tools
│   └── schemas.py       # Schema discovery tools
└── resources/           # Resource handlers
```

## Related Packages

- **gurufocus-api**: Python client library for GuruFocus API
- **fastmcp**: MCP server framework

## Disclaimer

This project is an unofficial tool and is not affiliated with, endorsed by, or sponsored by **GuruFocus.com, LLC** or any of its subsidiaries.

- **Non-Affiliation**: This software is developed independently and does not represent the views or opinions of GuruFocus.
- **Trademarks**: "GuruFocus" and the GuruFocus logo are trademarks of GuruFocus.com, LLC.
- **Data Usage**: Users are responsible for ensuring their use of this tool complies with the GuruFocus [Terms of Use](https://www.gurufocus.com/term-of-use) and any applicable API usage agreements. This tool is provided "as is" and intended for educational and personal use.
- **No Warranty**: The authors of this software make no warranty as to the accuracy, completeness, or reliability of the data retrieved using this tool.
- **No Investment Advice**: The information provided by this tool is for informational and educational purposes only and does not constitute investment advice, financial advice, trading advice, or any other sort of advice. You should not treat any of the tool's content as such.
- **External Methodologies**: References to third-party investment strategies, books, authors, or personalities (e.g., Phil Town, Rule #1, Warren Buffett) are for educational purposes to demonstrate the application of published methodologies. This project is not affiliated with, endorsed by, or sponsored by any referenced individuals or entities. All trademarks belong to their respective owners.

## License

MIT

## Support

- [GuruFocus API Documentation](https://www.gurufocus.com/api.php)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Report Issues](https://github.com/your-org/gurufocus-mcp/issues)
