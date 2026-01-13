"""Buy/Sell with retry logic - ensures full fill."""

import asyncio
import os
from polymarket_trade_executor import TradeExecutor, OrderSide


async def main():
    executor = TradeExecutor(
        host="https://clob.polymarket.com",
        private_key=os.getenv("POLY_PRIVATE_KEY"),
        funder=os.getenv("POLY_FUNDER_ADDRESS"),
    )
    
    token_id = "your_token_id_here"
    executor.prefetch_market_cache([token_id])
    
    # ========================================
    # Buy $50 worth with retry (FAK orders)
    # Will keep retrying until fully filled
    # ========================================
    result = await executor.buy_market(
        asset_id=token_id,
        amount=50.0,        # $50 USD
        max_retries=10,     # Max 10 retries
        min_amount=1.0,     # Stop if remaining < $1
    )
    
    print(f"🛒 Buy result:")
    print(f"   Spent: ${result.amount_spent:.2f}")
    print(f"   Tokens: {result.total_matched:.2f}")
    print(f"   Avg price: ${result.avg_price:.4f}")
    print(f"   Complete: {result.is_complete}")
    print(f"   Retries: {result.retry_count}")
    
    # ========================================
    # Sell all tokens with retry
    # ========================================
    token_balance = await executor.get_token_balance(token_id)
    
    if token_balance > 0:
        result = await executor.sell_all(
            asset_id=token_id,
            size=token_balance,
            max_retries=10,
            min_size=0.01,  # Stop if remaining < 0.01 tokens
        )
        
        print(f"💸 Sell result:")
        print(f"   Sold: {result.total_matched:.2f}/{result.total_size:.2f}")
        print(f"   Avg price: ${result.avg_price:.4f}")
        print(f"   Complete: {result.is_complete}")


if __name__ == "__main__":
    asyncio.run(main())

