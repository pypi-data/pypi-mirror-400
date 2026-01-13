"""Polymarket Trade Executor - Trade execution library for Polymarket CLOB API.

This library provides a clean interface to:
- Place limit/market orders
- Batch orders
- Split/Merge positions (gasless via Relayer)
- Redeem winning positions
- Manage balances

Example:
    from polymarket_trade_executor import TradeExecutor, OrderSide

    executor = TradeExecutor(
        host="https://clob.polymarket.com",
        private_key="0x...",
        funder="0x...",  # optional
    )

    # Get balance
    balance = await executor.get_balance()

    # Place market order
    result = await executor.place_market_order(
        asset_id="token_id_here",
        side=OrderSide.BUY,
        amount=10.0,
    )
"""

from .executor import (
    # Enums
    OrderSide,
    OrderStatus,
    # Result dataclasses
    OrderResult,
    SellAllResult,
    MergeAllResult,
    RedeemResult,
    BuyMarketResult,
    BatchOrderArgs,
    BatchOrdersResult,
    # Executors
    BaseTradeExecutor,
    SimulateTradeExecutor,
    TradeExecutor,
)

__version__ = "0.1.0"
__all__ = [
    # Enums
    "OrderSide",
    "OrderStatus",
    # Result dataclasses
    "OrderResult",
    "SellAllResult",
    "MergeAllResult",
    "RedeemResult",
    "BuyMarketResult",
    "BatchOrderArgs",
    "BatchOrdersResult",
    # Executors
    "BaseTradeExecutor",
    "SimulateTradeExecutor",
    "TradeExecutor",
]

