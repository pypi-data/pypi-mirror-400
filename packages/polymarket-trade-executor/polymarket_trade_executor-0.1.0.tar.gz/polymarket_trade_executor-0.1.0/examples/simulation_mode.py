"""Simulation mode - test without real API calls."""

import asyncio
from polymarket_trade_executor import SimulateTradeExecutor, OrderSide


async def main():
    # No credentials needed - simulates trades locally
    executor = SimulateTradeExecutor(
        starting_balance=1000.0,  # Start with $1000
        symbol="TEST",
    )
    
    token_id = "fake_token_id"
    
    # Get balance
    balance = await executor.get_balance()
    print(f"💰 Balance: ${balance:.2f}")
    
    # Place orders (simulated)
    result = await executor.place_market_order(
        asset_id=token_id,
        side=OrderSide.BUY,
        amount=100.0,
    )
    print(f"🛒 Bought: {result.size_matched:.2f} tokens @ ${result.price:.4f}")
    
    result = await executor.place_market_order(
        asset_id=token_id,
        side=OrderSide.SELL,
        amount=50.0,
    )
    print(f"💸 Sold: {result.size_matched:.2f} tokens @ ${result.price:.4f}")
    
    # Get trade summary
    summary = executor.get_trade_summary()
    print(f"\n📊 Trade Summary:")
    print(f"   Total orders: {summary['total_orders']}")
    print(f"   Buy orders: {summary['buy_orders']}")
    print(f"   Sell orders: {summary['sell_orders']}")
    print(f"   Total bought: ${summary['total_bought']:.2f}")
    print(f"   Total sold: ${summary['total_sold']:.2f}")
    print(f"   PnL: ${summary['pnl']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())

