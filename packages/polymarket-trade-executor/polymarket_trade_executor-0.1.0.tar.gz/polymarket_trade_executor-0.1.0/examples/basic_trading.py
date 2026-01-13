"""Basic trading example with Polymarket Trade Executor."""

import asyncio
import os
from polymarket_trade_executor import TradeExecutor, OrderSide
import dotenv

dotenv.load_dotenv()

async def main():
    # Initialize executor
    executor = TradeExecutor(
        host="https://clob.polymarket.com",
        private_key=os.getenv("POLY_PRIVATE_KEY"),
        funder=os.getenv("POLY_FUNDER_ADDRESS"),  # Optional
        # Builder API credentials (optional - for merge/split/redeem)
        builder_api_key=os.getenv("BUILDER_API_KEY"),
        builder_secret=os.getenv("BUILDER_SECRET"),
        builder_passphrase=os.getenv("BUILDER_PASSPHRASE"),
    )
    
    # Get USDC balance
    balance = await executor.get_balance()
    print(f"💰 Balance: ${balance:.2f} USDC")
    
    # Token ID from Polymarket market
    # token_id = "your_token_id_here"
    
    # # Pre-cache market info (optional but recommended)
    # executor.prefetch_market_cache([token_id])
    
    # Get token balance
    # token_balance = await executor.get_token_balance(token_id)
    # print(f"🎯 Token balance: {token_balance:.2f}")
    
    # ========================================
    # Place market order (BUY $10 worth)
    # ========================================
    # result = await executor.place_market_order(
    #     asset_id=token_id,
    #     side=OrderSide.BUY,
    #     amount=10.0,  # $10 USD
    # )
    
    # if result:
    #     print(f"✅ Buy order: {result.size_matched:.2f} tokens @ ${result.price:.4f}")
    # else:
    #     print("❌ Buy order failed")
    
    # # ========================================
    # # Place limit order
    # # ========================================
    # result = await executor.place_order(
    #     asset_id=token_id,
    #     side=OrderSide.BUY,
    #     price=0.50,   # Limit price
    #     size=10.0,    # 10 tokens
    #     order_type="GTC",  # Good Till Cancelled
    # )
    
    if result:
        print(f"✅ Limit order: {result.order_id} [{result.status}]")


if __name__ == "__main__":
    asyncio.run(main())

