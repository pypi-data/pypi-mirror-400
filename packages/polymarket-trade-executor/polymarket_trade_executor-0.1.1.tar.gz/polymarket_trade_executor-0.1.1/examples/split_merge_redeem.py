"""Split, Merge, Redeem positions - requires Builder API credentials."""

import asyncio
import os
from polymarket_trade_executor import TradeExecutor


async def main():
    # Builder API credentials required for gasless transactions
    executor = TradeExecutor(
        host="https://clob.polymarket.com",
        private_key=os.getenv("POLY_PRIVATE_KEY"),
        funder=os.getenv("POLY_FUNDER_ADDRESS"),
        # Required for split/merge/redeem
        builder_api_key=os.getenv("BUILDER_API_KEY"),
        builder_secret=os.getenv("BUILDER_SECRET"),
        builder_passphrase=os.getenv("BUILDER_PASSPHRASE"),
    )
    
    # Market condition ID (bytes32) - get from Polymarket API
    condition_id = "0x..."
    yes_token_id = "..."
    no_token_id = "..."
    
    # ========================================
    # Split: USDC → YES + NO tokens
    # ========================================
    tx_hash = await executor.split_positions(
        condition_id=condition_id,
        amount=10.0,  # $10 USDC → 10 YES + 10 NO
        neg_risk=False,
    )
    
    if tx_hash:
        print(f"✅ Split successful! Tx: {tx_hash}")
    else:
        print("❌ Split failed")
    
    # ========================================
    # Merge: YES + NO → USDC
    # ========================================
    tx_hash = await executor.merge_positions(
        condition_id=condition_id,
        amount=10.0,  # 10 YES + 10 NO → $10 USDC
        neg_risk=False,
    )
    
    if tx_hash:
        print(f"✅ Merge successful! Tx: {tx_hash}")
    
    # ========================================
    # Merge All: auto-detect and merge all pairs
    # ========================================
    result = await executor.merge_all(
        condition_id=condition_id,
        yes_token_id=yes_token_id,
        no_token_id=no_token_id,
        neg_risk=False,
    )
    
    print(f"📊 Merge all result:")
    print(f"   Merged: {result.merge_amount:.2f}")
    print(f"   YES remaining: {result.yes_remaining:.2f}")
    print(f"   NO remaining: {result.no_remaining:.2f}")
    
    # ========================================
    # Redeem: After market resolved
    # ========================================
    result = await executor.redeem_positions(
        condition_id=condition_id,
        index_sets=[1, 2],  # [1]=YES, [2]=NO, [1,2]=both
        neg_risk=False,
    )
    
    if result:
        print(f"✅ Redeem successful! Tx: {result.tx_hash}")
    else:
        print("❌ Redeem failed (market may not be resolved yet)")


if __name__ == "__main__":
    asyncio.run(main())

