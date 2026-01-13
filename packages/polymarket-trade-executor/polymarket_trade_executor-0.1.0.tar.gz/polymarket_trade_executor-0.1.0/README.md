# Polymarket Trade Executor

Trade execution library for Polymarket CLOB API.

## Installation

```bash
pip install polymarket-trade-executor
```

For merge/split/redeem (gasless transactions):

```bash
pip install polymarket-trade-executor[relayer]
```

## Quick Start

```python
import asyncio
from polymarket_trade_executor import TradeExecutor, OrderSide

async def main():
    executor = TradeExecutor(
        host="https://clob.polymarket.com",
        private_key="0x...",
        funder="0x...",  # optional
        # For merge/split/redeem (optional)
        builder_api_key="xxx",
        builder_secret="xxx",
        builder_passphrase="xxx",
    )
    
    # Get balance
    balance = await executor.get_balance()
    print(f"Balance: ${balance:.2f}")
    
    # Place market order
    result = await executor.place_market_order(
        asset_id="token_id_here",
        side=OrderSide.BUY,
        amount=10.0,
    )
    
    if result:
        print(f"Order: {result.order_id} - {result.size_matched} tokens @ ${result.price}")

asyncio.run(main())
```

## Features

| Feature | Requires Builder API |
|---------|---------------------|
| `place_order` / `place_market_order` | ❌ |
| `post_orders` (batch) | ❌ |
| `get_balance` / `get_token_balance` | ❌ |
| `buy_market` / `sell_all` (with retry) | ❌ |
| `split_positions` | ✅ |
| `merge_positions` / `merge_all` | ✅ |
| `redeem_positions` | ✅ |

## Simulation Mode

```python
from polymarket_trade_executor import SimulateTradeExecutor

executor = SimulateTradeExecutor(starting_balance=1000.0)
# Same API as TradeExecutor, no real API calls
```

## License

MIT

