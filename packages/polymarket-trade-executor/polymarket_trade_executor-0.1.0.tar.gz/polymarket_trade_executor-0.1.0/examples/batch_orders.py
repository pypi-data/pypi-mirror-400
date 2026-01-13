"""Batch orders example - place multiple orders in one request."""

import asyncio
import os
from polymarket_trade_executor import TradeExecutor, OrderSide, BatchOrderArgs


async def main():
    executor = TradeExecutor(
        host="https://clob.polymarket.com",
        private_key=os.getenv("POLY_PRIVATE_KEY"),
        funder=os.getenv("POLY_FUNDER_ADDRESS"),
    )
    
    token_id = "your_token_id_here"
    executor.prefetch_market_cache([token_id])
    
    # ========================================
    # Place multiple orders at once
    # ========================================
    orders = [
        BatchOrderArgs(
            asset_id=token_id,
            side=OrderSide.BUY,
            price=0.48,
            size=5.0,
            order_type="GTC",
        ),
        BatchOrderArgs(
            asset_id=token_id,
            side=OrderSide.BUY,
            price=0.49,
            size=5.0,
            order_type="GTC",
        ),
        BatchOrderArgs(
            asset_id=token_id,
            side=OrderSide.BUY,
            price=0.50,
            size=5.0,
            order_type="FAK",  # Fill And Kill
        ),
    ]
    
    result = await executor.post_orders(orders)
    
    print(f"📦 Batch result: {result.success_count}/{len(orders)} successful")
    
    for order in result.orders:
        print(f"   - {order.order_id}: {order.size_matched:.2f} @ ${order.price:.4f}")


if __name__ == "__main__":
    asyncio.run(main())

