"""Trade execution for Polymarket CLOB API.

This module can be used as a standalone library.
No external project-specific dependencies required.
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict
from functools import partial
from dataclasses import dataclass


# ============================================================================
# Models (self-contained, no external dependency)
# ============================================================================

class OrderSide(Enum):
    """Order side."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order status."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


@dataclass
class OrderResult:
    """Order result."""
    order_id: str
    status: str              # LIVE, MATCHED, CANCELLED, etc.
    side: str                # BUY, SELL
    price: float
    original_size: float
    size_matched: float
    order_type: str          # GTC, FOK, FAK, GTD
    asset_id: str = ""
    market: str = ""
    outcome: str = ""        # Up, Down
    
    @property
    def is_filled(self) -> bool:
        return self.status == "MATCHED"
    
    @property
    def fill_ratio(self) -> float:
        """Fill ratio (0.0 - 1.0)."""
        if self.original_size == 0:
            return 0.0
        return self.size_matched / self.original_size
    
    @classmethod
    def from_api_response(cls, data: dict) -> "OrderResult":
        """Parse from API response."""
        return cls(
            order_id=data.get("id", ""),
            status=data.get("status", ""),
            side=data.get("side", ""),
            price=float(data.get("price", 0)),
            original_size=float(data.get("original_size", 0)),
            size_matched=float(data.get("size_matched", 0)),
            order_type=data.get("order_type", ""),
            asset_id=data.get("asset_id", ""),
            market=data.get("market", ""),
            outcome=data.get("outcome", ""),
        )


@dataclass
class SellAllResult:
    """Result of sell_all operation."""
    total_size: float           # Total size to sell
    total_matched: float        # Total sold
    remaining: float            # Remaining unsold
    avg_price: float            # Weighted average price
    is_complete: bool           # True if sold all
    retry_count: int            # Number of retries


@dataclass
class MergeAllResult:
    """Result of merge_all operation."""
    merge_amount: float         # Amount merged
    yes_remaining: float        # YES remaining
    no_remaining: float         # NO remaining
    tx_hash: Optional[str]      # Transaction hash if successful


@dataclass
class RedeemResult:
    """Result of redeem operation."""
    amount_redeemed: float      # Tokens redeemed
    usdc_received: float        # USDC received (= amount if winning)
    tx_hash: Optional[str]      # Transaction hash if successful


@dataclass
class BuyMarketResult:
    """Result of buy_market operation."""
    amount_spent: float         # $ spent
    total_matched: float        # Total tokens bought
    remaining: float            # Remaining unspent
    avg_price: float            # Weighted average price
    is_complete: bool           # True if bought all
    retry_count: int            # Number of retries


@dataclass
class BatchOrderArgs:
    """Args for a batch order."""
    asset_id: str               # Token ID
    side: OrderSide             # BUY or SELL
    price: float                # Limit price
    size: float                 # Size
    order_type: str = "GTC"     # GTC, FOK, FAK, GTD


@dataclass 
class BatchOrdersResult:
    """Result of post_orders (batch) operation."""
    success_count: int          # Successful orders
    failed_count: int           # Failed orders
    orders: list[OrderResult]   # List of order results


# py-clob-client imports
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    OrderArgs,
    MarketOrderArgs,
    OrderType,
    PostOrdersArgs,
    BalanceAllowanceParams,
    AssetType,
    OpenOrderParams,
)
from py_clob_client.order_builder.constants import BUY, SELL
from py_clob_client.config import get_contract_config

from eth_abi import encode
from eth_utils import keccak


class BaseTradeExecutor(ABC):
    """Abstract base class for Trade Executor."""
    
    def __init__(self, api_base_url: str = "", symbol: str = ""):
        self.api_base_url = api_base_url
        self.symbol = symbol
        logger_name = f"polymarket_trade_executor.{symbol}" if symbol else "polymarket_trade_executor"
        self.logger = logging.getLogger(logger_name)
    
    @abstractmethod
    async def place_order(
        self, 
        asset_id: str, 
        side: OrderSide, 
        price: float, 
        size: float,
        order_type: str = "FOK",
    ) -> Optional[OrderResult]:
        """Place a limit order.
        
        Args:
            order_type: GTC, FOK, GTD, FAK
        Returns:
            OrderResult with details, or None if failed.
        """
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Get order status."""
        pass
    
    @abstractmethod
    async def get_order_detail(self, order_id: str) -> dict:
        """Get order details."""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        pass
    
    @abstractmethod
    async def get_balance(self) -> float:
        """Get USDC balance."""
        pass
    
    @abstractmethod
    async def get_token_balance(self, token_id: str) -> float:
        """Get balance of a specific token (YES/NO)."""
        pass
    
    @abstractmethod
    async def place_market_order(
        self,
        asset_id: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.FAK,
    ) -> Optional[OrderResult]:
        """Place a market order.
        
        Args:
            amount: BUY = $ to spend, SELL = shares to sell
            order_type: Order type (FAK, FOK, GTC). Default FAK
        Returns:
            OrderResult with details, or None if failed.
        """
        pass
    
    @abstractmethod
    async def merge_positions(
        self,
        condition_id: str,
        amount: float,
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Merge YES + NO positions to receive USDC.
        
        Args:
            condition_id: Market condition ID (bytes32)
            amount: Number of tokens to merge
            neg_risk: True if NegRisk market
            
        Returns:
            Transaction hash if successful, None if failed.
        """
        pass
    
    @abstractmethod
    async def split_positions(
        self,
        condition_id: str,
        amount: float,
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Split USDC into YES + NO tokens.
        
        Args:
            condition_id: Market condition ID (bytes32)
            amount: USDC amount to split (will receive amount YES + amount NO)
            neg_risk: True if NegRisk market
            
        Returns:
            Transaction hash if successful, None if failed.
        """
        pass
    
    def prefetch_market_cache(self, token_ids: list[str]) -> None:
        """Pre-cache tick_size, neg_risk, fee_rate for token_ids.
        
        Call this when you get new markets to cache ahead of time,
        avoiding API calls when creating orders.
        
        Default: no-op (SimulateTradeExecutor).
        """
        pass
    
    @abstractmethod
    async def sell_all(
        self,
        asset_id: str,
        size: float,
        max_retries: int = 10,
        min_size: float = 0.01,
    ) -> SellAllResult:
        """Sell entire position with retry logic.
        
        Args:
            asset_id: Token ID to sell
            size: Amount to sell
            max_retries: Max retry count
            min_size: Don't sell if remaining is too small
            
        Returns:
            SellAllResult with details.
        """
        pass
    
    @abstractmethod
    async def buy_market(
        self,
        asset_id: str,
        amount: float,
        max_retries: int = 5,
        min_amount: float = 1.0,
    ) -> BuyMarketResult:
        """Buy market order with retry logic (FAK).
        
        Args:
            asset_id: Token ID to buy
            amount: $ to spend
            max_retries: Max retry count
            min_amount: Don't buy if remaining is too small
            
        Returns:
            BuyMarketResult with details.
        """
        pass
    
    @abstractmethod
    async def merge_all(
        self,
        condition_id: str,
        yes_token_id: str,
        no_token_id: str,
        neg_risk: bool = False,
    ) -> MergeAllResult:
        """Auto get balance and merge all possible pairs.
        
        Args:
            condition_id: Market condition ID
            yes_token_id: YES token ID
            no_token_id: NO token ID
            neg_risk: True if NegRisk market
            
        Returns:
            MergeAllResult with (merge_amount, yes_remaining, no_remaining, tx_hash)
        """
        pass
    
    @abstractmethod
    async def redeem_positions(
        self,
        condition_id: str,
        index_sets: list[int],
        neg_risk: bool = False,
    ) -> Optional[RedeemResult]:
        """Redeem winning positions after market resolved.
        
        Use after market is resolved to convert winning tokens to USDC.
        No amount needed - will redeem entire balance.
        
        Args:
            condition_id: Market condition ID (bytes32)
            index_sets: Outcome indices to redeem. 
                       [1] = YES only, [2] = NO only, [1, 2] = both
            neg_risk: True if NegRisk market
            
        Returns:
            RedeemResult if successful, None if failed.
        """
        pass
    
    @abstractmethod
    async def post_orders(
        self,
        orders: list[BatchOrderArgs],
    ) -> BatchOrdersResult:
        """Place multiple orders at once (batch).
        
        Args:
            orders: List of BatchOrderArgs with order info
            
        Returns:
            BatchOrdersResult with results for each order.
        """
        pass


class SimulateTradeExecutor(BaseTradeExecutor):
    """Simulate trades - no real API calls."""
    
    def __init__(self, api_base_url: str = "", starting_balance: float = 1000.0, symbol: str = ""):
        super().__init__(api_base_url, symbol)
        self._order_counter = 0
        self._orders: Dict[str, dict] = {}
        self._starting_balance = starting_balance
        self._balance = starting_balance
    
    async def place_order(
        self, 
        asset_id: str, 
        side: OrderSide, 
        price: float, 
        size: float,
        order_type: str = "FOK",
    ) -> Optional[OrderResult]:
        """Simulate order placement."""
        self._order_counter += 1
        order_id = f"SIM-{self._order_counter:06d}"
        
        cost = price * size
        
        # Store order
        self._orders[order_id] = {
            "order_id": order_id,
            "asset_id": asset_id,
            "side": side.value.upper(),
            "price": price,
            "size": size,
            "cost": cost,
            "status": "MATCHED",
            "timestamp": time.time()
        }
        
        self.logger.info(f"[SIM] Order {order_id}: {side.value.upper()} {size:.0f} @ ${price:.3f} = ${cost:.2f}")
        
        await asyncio.sleep(0.1)  # Simulate delay
        
        return OrderResult(
            order_id=order_id,
            status="MATCHED",
            side=side.value.upper(),
            price=price,
            original_size=size,
            size_matched=size,
            order_type=order_type,
            asset_id=asset_id,
        )
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Get order status."""
        order = self._orders.get(order_id)
        if not order:
            return OrderStatus.FAILED
        status = order["status"]
        if isinstance(status, OrderStatus):
            return status
        # Map string status
        status_map = {
            "MATCHED": OrderStatus.FILLED,
            "LIVE": OrderStatus.PENDING,
            "CANCELLED": OrderStatus.CANCELLED,
        }
        return status_map.get(status, OrderStatus.FAILED)
    
    async def get_order_detail(self, order_id: str) -> dict:
        """Get order details."""
        order = self._orders.get(order_id)
        if not order:
            return None
        return {
            "id": order["order_id"],
            "status": "MATCHED" if order["status"] == "MATCHED" or order["status"] == OrderStatus.FILLED else str(order["status"]),
            "side": order["side"],
            "price": order["price"],
            "original_size": order["size"],
            "size_matched": order["size"],
            "order_type": "GTC",
            "asset_id": order["asset_id"],
        }
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order."""
        if order_id in self._orders:
            self._orders[order_id]["status"] = OrderStatus.CANCELLED
            self.logger.info(f"[SIM] Order {order_id} cancelled")
            return True
        return False
    
    async def get_balance(self) -> float:
        """Get account balance."""
        return self._balance
    
    async def get_token_balance(self, token_id: str) -> float:
        """Simulate token balance - return large value."""
        return 1000.0
    
    async def place_market_order(
        self,
        asset_id: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.FAK,
    ) -> Optional[OrderResult]:
        """Simulate market order - fill immediately at simulated price."""
        simulated_price = 0.50
        
        if side == OrderSide.BUY:
            size = amount / simulated_price
        else:
            size = amount
        
        order_type_str = order_type.value if hasattr(order_type, 'value') else str(order_type)
        return await self.place_order(asset_id, side, simulated_price, size, order_type_str)
    
    def get_trade_summary(self) -> dict:
        """Get summary of executed trades."""
        orders = list(self._orders.values())
        buys = [o for o in orders if o["side"] == "BUY"]
        sells = [o for o in orders if o["side"] == "SELL"]
        
        return {
            "total_orders": len(orders),
            "buy_orders": len(buys),
            "sell_orders": len(sells),
            "total_bought": sum(o["cost"] for o in buys),
            "total_sold": sum(o["cost"] for o in sells),
            "current_balance": self._balance,
            "starting_balance": self._starting_balance,
            "pnl": self._balance - self._starting_balance
        }
    
    async def merge_positions(
        self,
        condition_id: str,
        amount: float,
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Simulate merge positions."""
        self.logger.info(f"[SIM] Merge positions: {amount:.2f} tokens for condition {condition_id[:20]}...")
        await asyncio.sleep(0.2)
        
        self._balance += amount
        
        tx_hash = f"0xSIM_MERGE_{int(time.time())}"
        self.logger.info(f"[SIM] Merge successful! Received ${amount:.2f} USDC. Tx: {tx_hash}")
        return tx_hash
    
    async def split_positions(
        self,
        condition_id: str,
        amount: float,
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Simulate split positions."""
        self.logger.info(f"[SIM] Split positions: ${amount:.2f} USDC for condition {condition_id[:20]}...")
        await asyncio.sleep(0.2)
        
        if self._balance < amount:
            self.logger.error(f"[SIM] Insufficient balance: ${self._balance:.2f} < ${amount:.2f}")
            return None
        
        self._balance -= amount
        
        tx_hash = f"0xSIM_SPLIT_{int(time.time())}"
        self.logger.info(f"[SIM] Split successful! Received {amount:.2f} YES + {amount:.2f} NO tokens. Tx: {tx_hash}")
        return tx_hash
    
    async def sell_all(
        self,
        asset_id: str,
        size: float,
        max_retries: int = 10,
        min_size: float = 0.01,
    ) -> SellAllResult:
        """Simulate sell all - sell everything immediately."""
        simulated_price = 0.50
        
        await self.place_market_order(asset_id, OrderSide.SELL, size)
        
        self.logger.info(f"[SIM] Sell all: {size:.2f} @ ${simulated_price:.4f}")
        
        return SellAllResult(
            total_size=size,
            total_matched=size,
            remaining=0,
            avg_price=simulated_price,
            is_complete=True,
            retry_count=1,
        )
    
    async def buy_market(
        self,
        asset_id: str,
        amount: float,
        max_retries: int = 5,
        min_amount: float = 1.0,
    ) -> BuyMarketResult:
        """Simulate buy market - buy everything immediately."""
        simulated_price = 0.50
        size = amount / simulated_price
        
        await self.place_market_order(asset_id, OrderSide.BUY, amount)
        
        self.logger.info(f"[SIM] Buy market: ${amount:.2f} -> {size:.2f} tokens @ ${simulated_price:.4f}")
        
        return BuyMarketResult(
            amount_spent=amount,
            total_matched=size,
            remaining=0,
            avg_price=simulated_price,
            is_complete=True,
            retry_count=1,
        )
    
    async def merge_all(
        self,
        condition_id: str,
        yes_token_id: str,
        no_token_id: str,
        neg_risk: bool = False,
    ) -> MergeAllResult:
        """Simulate merge all."""
        yes_balance = await self.get_token_balance(yes_token_id)
        no_balance = await self.get_token_balance(no_token_id)
        merge_amount = min(yes_balance, no_balance)
        
        tx_hash = None
        if merge_amount > 0:
            tx_hash = await self.merge_positions(condition_id, merge_amount, neg_risk)
        
        return MergeAllResult(
            merge_amount=merge_amount if tx_hash else 0,
            yes_remaining=yes_balance - merge_amount if tx_hash else yes_balance,
            no_remaining=no_balance - merge_amount if tx_hash else no_balance,
            tx_hash=tx_hash,
        )
    
    async def redeem_positions(
        self,
        condition_id: str,
        index_sets: list[int],
        neg_risk: bool = False,
    ) -> Optional[RedeemResult]:
        """Simulate redeem positions."""
        simulated_amount = 100.0
        
        self.logger.info(f"[SIM] Redeem positions: index_sets={index_sets} for condition {condition_id[:20]}...")
        await asyncio.sleep(0.2)
        
        self._balance += simulated_amount
        
        tx_hash = f"0xSIM_REDEEM_{int(time.time())}"
        self.logger.info(f"[SIM] Redeem successful! Received ${simulated_amount:.2f} USDC. Tx: {tx_hash}")
        
        return RedeemResult(
            amount_redeemed=simulated_amount,
            usdc_received=simulated_amount,
            tx_hash=tx_hash,
        )
    
    async def post_orders(
        self,
        orders: list[BatchOrderArgs],
    ) -> BatchOrdersResult:
        """Simulate batch orders."""
        results = []
        success_count = 0
        
        for order_args in orders:
            result = await self.place_order(
                asset_id=order_args.asset_id,
                side=order_args.side,
                price=order_args.price,
                size=order_args.size,
                order_type=order_args.order_type,
            )
            if result:
                results.append(result)
                success_count += 1
        
        self.logger.info(f"[SIM] Batch orders: {success_count}/{len(orders)} successful")
        
        return BatchOrdersResult(
            success_count=success_count,
            failed_count=len(orders) - success_count,
            orders=results,
        )


class TradeExecutor(BaseTradeExecutor):
    """Real trade executor - calls Polymarket CLOB API."""
    
    CHAIN_ID = 137  # Polygon mainnet
    RELAYER_URL = "https://relayer-v2.polymarket.com"
    
    def __init__(
        self, 
        host: str,
        private_key: str,
        funder: str = None,
        signature_type: int = 2,  # 0=EOA, 1=Email/Magic, 2=Browser proxy
        symbol: str = "",
        # Builder API credentials (optional - for merge/split/redeem)
        builder_api_key: str = None,
        builder_secret: str = None,
        builder_passphrase: str = None,
        # Logger injection (optional)
        logger=None,
    ):
        super().__init__(host, symbol)
        
        # Override logger if injected
        if logger:
            self.logger = logger
        
        # Store builder credentials for Relayer
        self.builder_api_key = builder_api_key
        self.builder_secret = builder_secret
        self.builder_passphrase = builder_passphrase
        
        # Store private_key for Relayer
        self.private_key = private_key
        
        # Store funder for logging
        self.funder_address = funder
        
        # Validate and log funder
        if not funder:
            self.logger.warning("⚠️  No funder address provided. Trading will use private key wallet only.")
        else:
            self.logger.info(f"✅ Funder address configured: {funder}")
        
        # CLOB Client for trading
        self.client = ClobClient(
            host=host,
            chain_id=self.CHAIN_ID,
            key=private_key,
            signature_type=signature_type,
            funder=funder or None,
        )
        
        # Derive/create API credentials
        creds = self.client.create_or_derive_api_creds()
        if creds:
            self.client.set_api_creds(creds)
            trading_address = self.client.get_address()
            self.logger.info(f"✅ ClobClient initialized")
            self.logger.info(f"   Trading address: {trading_address}")
            if funder:
                self.logger.info(f"   Funder address: {funder}")
            else:
                self.logger.warning(f"   Funder address: None (using trading address for funding)")
        else:
            raise RuntimeError("Failed to create/derive API credentials")
        
        # Relayer Client for gasless transactions (split/merge)
        self.relay_client = self._init_relay_client()
    
    def _init_relay_client(self):
        """Initialize RelayClient for gasless transactions."""
        if not self.builder_api_key or not self.builder_secret:
            self.logger.warning("⚠️ Builder API credentials not configured. Split/Merge/Redeem will not work.")
            return None
        
        try:
            from py_builder_relayer_client.client import RelayClient
            from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds
            
            builder_config = BuilderConfig(
                local_builder_creds=BuilderApiKeyCreds(
                    key=self.builder_api_key,
                    secret=self.builder_secret,
                    passphrase=self.builder_passphrase or "",
                )
            )
            
            relay_client = RelayClient(
                relayer_url=self.RELAYER_URL,
                chain_id=self.CHAIN_ID,
                private_key=self.private_key,
                builder_config=builder_config,
            )
            
            self.logger.info(f"✅ RelayClient initialized for {relay_client.get_expected_safe()}")
            return relay_client
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to initialize RelayClient: {e}")
            return None
    
    def _run_sync(self, func, *args, **kwargs):
        """Wrap sync function to run in thread pool."""
        return asyncio.get_event_loop().run_in_executor(
            None, partial(func, *args, **kwargs)
        )
    
    async def _fetch_order_with_retry(self, order_id: str, max_wait: float = 10) -> Optional[dict]:
        """Fetch order details with retry until success or timeout.
        
        Args:
            order_id: Order ID to fetch
            max_wait: Max wait time (seconds)
            
        Returns:
            Order detail dict or None if timeout
        """
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                order_detail = await self._run_sync(self.client.get_order, order_id)
                if order_detail:
                    return order_detail
            except Exception as e:
                self.logger.warning(f"Retrying get_order ({order_id}): {e}")
            await asyncio.sleep(1)
        
        self.logger.error(f"Failed to fetch order detail after {max_wait}s: {order_id}")
        return None
    
    def prefetch_market_cache(self, token_ids: list[str]) -> None:
        """Pre-cache tick_size, neg_risk, fee_rate for token_ids.
        
        Calls API to cache market info, avoiding API calls when creating orders.
        """
        for token_id in token_ids:
            try:
                tick_size = self.client.get_tick_size(token_id)
                neg_risk = self.client.get_neg_risk(token_id)
                fee_rate = self.client.get_fee_rate_bps(token_id)
                self.logger.debug(f"Cached market info for {token_id[:16]}...: tick_size={tick_size}, neg_risk={neg_risk}, fee_rate={fee_rate}")
            except Exception as e:
                self.logger.warning(f"Failed to prefetch cache for {token_id}: {e}")
    
    async def place_order(
        self, 
        asset_id: str, 
        side: OrderSide, 
        price: float, 
        size: float,
        order_type: OrderType = OrderType.FOK,
    ) -> Optional[OrderResult]:
        """Place order via CLOB API.
        
        Args:
            order_type: GTC (Good Till Cancelled), FOK (Fill or Kill), 
                       GTD (Good Till Date), FAK (Fill and Kill)
        Returns:
            OrderResult with details, or None if failed.
        """
        try:
            clob_side = BUY if side == OrderSide.BUY else SELL
            
            order_args = OrderArgs(
                token_id=asset_id,
                price=price,
                size=size,
                side=clob_side,
            )
            
            # Create and sign order
            signed_order = await self._run_sync(self.client.create_order, order_args)
            
            # Post order with specified type
            response = await self._run_sync(
                self.client.post_order, signed_order, order_type
            )
            
            order_id = response.get("orderID") or response.get("id")
            if not order_id:
                self.logger.error(f"Order response missing ID: {response}")
                return None
            
            # Fetch order details with retry
            order_detail = await self._fetch_order_with_retry(order_id)
            if not order_detail:
                return None
                
            result = OrderResult.from_api_response(order_detail)
            
            self.logger.info(
                f"Order placed: {result.order_id} - {result.side} {result.size_matched:.2f}/{result.original_size:.2f} @ ${result.price:.4f} [{result.status}]"
            )
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return None
    
    async def place_market_order(
        self,
        asset_id: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.FAK,
    ) -> Optional[OrderResult]:
        """Place market order via CLOB API.
        
        Args:
            amount: BUY = $ to spend, SELL = shares to sell
            order_type: Order type (FAK, FOK, GTC). Default FAK (Fill and Kill)
        Returns:
            OrderResult with details, or None if failed.
        """
        try:
            clob_side = BUY if side == OrderSide.BUY else SELL
            
            order_args = MarketOrderArgs(
                token_id=asset_id,
                amount=amount,
                side=clob_side,
                price=0,  # 0 = auto calculate from orderbook
                order_type=order_type,
            )
            
            # Create and sign market order
            signed_order = await self._run_sync(self.client.create_market_order, order_args)
            
            # Post order
            response = await self._run_sync(
                self.client.post_order, signed_order, order_type
            )
            
            order_id = response.get("orderID") or response.get("id")
            if not order_id:
                self.logger.error(f"Market order response missing ID: {response}")
                return None
            
            # Fetch order details with retry
            order_detail = await self._fetch_order_with_retry(order_id)
            if not order_detail:
                return None
                
            result = OrderResult.from_api_response(order_detail)
            
            self.logger.info(
                f"Market order placed: {result.order_id} - {result.side} {result.size_matched:.2f}/{result.original_size:.2f} @ ${result.price:.4f} [{result.status}]"
            )
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to place market order: {e}")
            return None
    
    async def get_order_detail(self, order_id: str) -> dict:
        """Get order details from API with mapped status."""
        try:
            order = await self._run_sync(self.client.get_order, order_id)
            
            # Map raw status to OrderStatus enum
            status_map = {
                "LIVE": OrderStatus.PENDING,
                "OPEN": OrderStatus.PENDING,
                "MATCHED": OrderStatus.FILLED,
                "FILLED": OrderStatus.PENDING,
                "CANCELLED": OrderStatus.CANCELLED,
                "CANCELED": OrderStatus.CANCELLED,
            }
            raw_status = order.get("status", "").upper()
            order["mapped_status"] = status_map.get(raw_status, OrderStatus.FAILED)
            
            return order
        except Exception as e:
            self.logger.error(f"Failed to get order detail: {e}")
            return None

    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Get order status from API."""
        order = await self.get_order_detail(order_id)
        if order is None:
            return OrderStatus.FAILED
        return order["mapped_status"]
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order via API."""
        try:
            result = await self._run_sync(self.client.cancel, order_id)
            success = result.get("canceled") or result.get("success", False)
            if success:
                self.logger.info(f"Order cancelled: {order_id}")
            return bool(success)
        except Exception as e:
            self.logger.error(f"Failed to cancel order: {e}")
            return False
    
    async def get_balance(self) -> float:
        """Get USDC balance from API.
        
        Note: Balance is from trading address (private key wallet),
        not from funder address.
        """
        try:
            trading_address = self.client.get_address()
            
            params = BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
            result = await self._run_sync(self.client.get_balance_allowance, params)
            
            if not result:
                self.logger.warning("get_balance_allowance returned None")
                return 0.0
            
            self.logger.debug(f"Balance API response: {result}")
            
            balance_raw = result.get("balance", 0)
            balance = float(balance_raw)
            
            # Convert from 6 decimals (USDC uses 6 decimals)
            balance_usd = balance / 1_000_000
            
            target_address = self.funder_address if self.funder_address else trading_address
            self.logger.info(
                f"Balance: ${balance_usd:.2f} USDC "
                f"(raw: {balance}, address: {target_address} {'[Funder]' if self.funder_address else '[Signer]'})"
            )
            
            return balance_usd
            
        except Exception as e:
            self.logger.error(f"Failed to get balance: {e}", exc_info=True)
            return 0.0
    
    async def get_token_balance(self, token_id: str) -> float:
        """Get token (YES/NO) balance from API."""
        params = BalanceAllowanceParams(
            asset_type=AssetType.CONDITIONAL,
            token_id=token_id
        )
        result = await self._run_sync(self.client.get_balance_allowance, params)
        
        balance = float(result.get("balance", 0))
        # Convert from 6 decimals
        return balance / 1_000_000
    
    async def get_open_orders(self, asset_id: str = None) -> list:
        """Get list of open orders."""
        try:
            params = OpenOrderParams(asset_id=asset_id) if asset_id else OpenOrderParams()
            orders = await self._run_sync(self.client.get_orders, params)
            return orders
        except Exception as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return []
    
    async def cancel_all_orders(self) -> bool:
        """Cancel all orders."""
        try:
            await self._run_sync(self.client.cancel_all)
            self.logger.info("All orders cancelled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel all orders: {e}")
            return False
    
    async def post_orders(
        self,
        orders: list[BatchOrderArgs],
    ) -> BatchOrdersResult:
        """Place multiple orders at once (batch) via CLOB API.
        
        Uses client.post_orders to send all orders in 1 request.
        More efficient than calling place_order multiple times.
        """
        try:
            post_orders_list = []
            order_type_map = {
                "GTC": OrderType.GTC,
                "FOK": OrderType.FOK,
                "FAK": OrderType.FAK,
                "GTD": OrderType.GTD,
            }
            
            for order_args in orders:
                clob_side = BUY if order_args.side == OrderSide.BUY else SELL
                
                # Create and sign order
                signed_order = await self._run_sync(
                    self.client.create_order,
                    OrderArgs(
                        token_id=order_args.asset_id,
                        price=order_args.price,
                        size=order_args.size,
                        side=clob_side,
                    )
                )
                
                order_type = order_type_map.get(order_args.order_type, OrderType.GTC)
                
                post_orders_list.append(PostOrdersArgs(
                    order=signed_order,
                    orderType=order_type,
                ))
            
            # Send batch request
            response = await self._run_sync(self.client.post_orders, post_orders_list)
            
            self.logger.debug(f"Batch orders raw response: {response}")
            
            # Parse response
            results = []
            success_count = 0
            
            if isinstance(response, list):
                for i, item in enumerate(response):
                    order_id = item.get("orderID") or item.get("id")
                    error_msg = item.get("error") or item.get("errorMsg") or item.get("message")
                    
                    if error_msg:
                        self.logger.warning(f"Order {i+1} failed: {error_msg}")
                    
                    if order_id:
                        order_detail = await self._fetch_order_with_retry(order_id, max_wait=5)
                        if order_detail:
                            result = OrderResult.from_api_response(order_detail)
                            results.append(result)
                            success_count += 1
                    elif not error_msg:
                        self.logger.warning(f"Order {i+1} failed with unknown error: {item}")
            
            self.logger.info(f"Batch orders: {success_count}/{len(orders)} successful")
            
            return BatchOrdersResult(
                success_count=success_count,
                failed_count=len(orders) - success_count,
                orders=results,
            )
            
        except Exception as e:
            self.logger.error(f"Failed to post batch orders: {e}")
            return BatchOrdersResult(
                success_count=0,
                failed_count=len(orders),
                orders=[],
            )
    
    async def merge_positions(
        self,
        condition_id: str,
        amount: float,
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Merge YES + NO positions to receive USDC via Relayer (gasless).
        
        Args:
            condition_id: Market condition ID (bytes32)
            amount: Number of tokens to merge (must have both YES and NO)
            neg_risk: True if NegRisk market
            
        Returns:
            Transaction hash if successful, None if failed.
        """
        return await self._execute_ctf_operation(
            operation="merge",
            condition_id=condition_id,
            amount=amount,
            neg_risk=neg_risk,
        )
    
    async def split_positions(
        self,
        condition_id: str,
        amount: float,
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Split USDC into YES + NO tokens via Relayer (gasless).
        
        Args:
            condition_id: Market condition ID (bytes32)
            amount: USDC amount to split (will receive amount YES + amount NO)
            neg_risk: True if NegRisk market
            
        Returns:
            Transaction hash if successful, None if failed.
        """
        return await self._execute_ctf_operation(
            operation="split",
            condition_id=condition_id,
            amount=amount,
            neg_risk=neg_risk,
        )
    
    async def redeem_positions(
        self,
        condition_id: str,
        index_sets: list[int],
        neg_risk: bool = False,
    ) -> Optional[RedeemResult]:
        """Redeem winning positions after market resolved via Relayer (gasless).
        
        Args:
            condition_id: Market condition ID (bytes32)
            index_sets: Outcome indices to redeem.
                       [1] = YES only, [2] = NO only, [1, 2] = both
            neg_risk: True if NegRisk market
            
        Returns:
            RedeemResult if successful, None if failed.
        """
        tx_hash = await self._execute_ctf_redeem(
            condition_id=condition_id,
            index_sets=index_sets,
            neg_risk=neg_risk,
        )
        
        if tx_hash:
            # Note: Unknown exact amount - CTF redeems entire balance
            # Caller should track balance before/after
            return RedeemResult(
                amount_redeemed=0,  # Unknown - caller should track
                usdc_received=0,    # Unknown - caller should track
                tx_hash=tx_hash,
            )
        return None
    
    async def _execute_ctf_operation(
        self,
        operation: str,  # "merge" or "split"
        condition_id: str,
        amount: float,
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Execute CTF operation (merge/split) via Relayer.
        
        Ref: https://docs.polymarket.com/developers/builders/relayer-client
        """
        try:
            from py_builder_relayer_client.models import SafeTransaction, OperationType
            
            if not self.relay_client:
                self.logger.error("RelayClient not initialized. Check Builder API credentials.")
                return None
            
            # Contract addresses
            contract_config = get_contract_config(self.CHAIN_ID, neg_risk)
            ctf_address = contract_config.conditional_tokens
            collateral_address = contract_config.collateral
            
            # parentCollectionId = bytes32(0) for binary markets
            parent_collection_id = "0x" + "00" * 32
            
            # Partition for binary outcome: [1, 2] = [YES, NO]
            partition = [1, 2]
            
            # Amount in token decimals (1e6 - USDC/CTF decimals)
            amount_wei = int(amount * 1e6)
            
            # Condition ID - ensure 0x prefix
            if not condition_id.startswith("0x"):
                condition_id = "0x" + condition_id
            
            # Encode function call
            tx_data = self._encode_ctf_function(
                function_name="mergePositions" if operation == "merge" else "splitPosition",
                collateral_token=collateral_address,
                parent_collection_id=parent_collection_id,
                condition_id=condition_id,
                partition=partition,
                amount=amount_wei,
            )
            
            # Build SafeTransaction
            tx = SafeTransaction(
                to=ctf_address,
                operation=OperationType.Call,
                data=tx_data,
                value="0"
            )
            
            # Execute via relayer
            op_name = "Merge" if operation == "merge" else "Split"
            self.logger.info(f"{op_name}ing {amount:.2f} via Relayer...")
            
            response = await self._run_sync(
                self.relay_client.execute, 
                [tx], 
                f"{op_name} positions"
            )
            
            if not response or not response.transaction_id:
                self.logger.error(f"{op_name} transaction failed - no response from relayer")
                return None
            
            self.logger.info(f"{op_name} tx submitted: {response.transaction_id}")
            
            # Wait for confirmation
            result = await self._run_sync(response.wait)
            
            if result and result.get("state") in ["STATE_MINED", "STATE_CONFIRMED"]:
                tx_hash = result.get("transactionHash", response.transaction_hash)
                self.logger.info(f"{op_name} positions successful! Tx: {tx_hash}")
                return tx_hash
            else:
                self.logger.error(f"{op_name} positions failed! State: {result.get('state') if result else 'unknown'}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to {operation} positions: {e}")
            return None
    
    def _encode_ctf_function(
        self,
        function_name: str,
        collateral_token: str,
        parent_collection_id: str,
        condition_id: str,
        partition: list,
        amount: int
    ) -> str:
        """Encode CTF function call data (mergePositions/splitPosition)."""
        from eth_abi import encode
        from eth_utils import to_checksum_address
        
        # Function selector: keccak256("<function_name>(address,bytes32,bytes32,uint256[],uint256)")[:4]
        function_sig = f"{function_name}(address,bytes32,bytes32,uint256[],uint256)"
        function_selector = keccak(text=function_sig)[:4]
        
        # Convert addresses
        collateral_token = to_checksum_address(collateral_token)
        
        # Convert bytes32 strings to bytes
        parent_bytes = bytes.fromhex(parent_collection_id[2:]) if parent_collection_id.startswith("0x") else bytes.fromhex(parent_collection_id)
        condition_bytes = bytes.fromhex(condition_id[2:]) if condition_id.startswith("0x") else bytes.fromhex(condition_id)
        
        # Encode parameters
        encoded_params = encode(
            ["address", "bytes32", "bytes32", "uint256[]", "uint256"],
            [collateral_token, parent_bytes, condition_bytes, partition, amount]
        )
        
        return "0x" + (function_selector + encoded_params).hex()
    
    async def _execute_ctf_redeem(
        self,
        condition_id: str,
        index_sets: list[int],
        neg_risk: bool = False,
    ) -> Optional[str]:
        """Execute CTF redeemPositions via Relayer.
        
        Redeem has different signature than merge/split - no amount needed.
        Function: redeemPositions(address collateralToken, bytes32 parentCollectionId, 
                                   bytes32 conditionId, uint256[] indexSets)
        """
        try:
            from py_builder_relayer_client.models import SafeTransaction, OperationType
            
            if not self.relay_client:
                self.logger.error("RelayClient not initialized. Check Builder API credentials.")
                return None
            
            # Contract addresses
            contract_config = get_contract_config(self.CHAIN_ID, neg_risk)
            ctf_address = contract_config.conditional_tokens
            collateral_address = contract_config.collateral
            
            # parentCollectionId = bytes32(0) for binary markets
            parent_collection_id = "0x" + "00" * 32
            
            # Condition ID - ensure 0x prefix
            if not condition_id.startswith("0x"):
                condition_id = "0x" + condition_id
            
            # Encode redeemPositions function call
            tx_data = self._encode_redeem_function(
                collateral_token=collateral_address,
                parent_collection_id=parent_collection_id,
                condition_id=condition_id,
                index_sets=index_sets,
            )
            
            # Build SafeTransaction
            tx = SafeTransaction(
                to=ctf_address,
                operation=OperationType.Call,
                data=tx_data,
                value="0"
            )
            
            self.logger.info(f"Redeeming positions (index_sets={index_sets}) via Relayer...")
            
            response = await self._run_sync(
                self.relay_client.execute,
                [tx],
                "Redeem positions"
            )
            
            if not response or not response.transaction_id:
                self.logger.error("Redeem transaction failed - no response from relayer")
                return None
            
            self.logger.info(f"Redeem tx submitted: {response.transaction_id}")
            
            # Wait for confirmation
            result = await self._run_sync(response.wait)
            
            if result and result.get("state") in ["STATE_MINED", "STATE_CONFIRMED"]:
                tx_hash = result.get("transactionHash", response.transaction_hash)
                self.logger.info(f"Redeem positions successful! Tx: {tx_hash}")
                return tx_hash
            else:
                self.logger.error(f"Redeem positions failed! State: {result.get('state') if result else 'unknown'}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to redeem positions: {e}")
            return None
    
    def _encode_redeem_function(
        self,
        collateral_token: str,
        parent_collection_id: str,
        condition_id: str,
        index_sets: list[int],
    ) -> str:
        """Encode redeemPositions function call data.
        
        Function: redeemPositions(address, bytes32, bytes32, uint256[])
        """
        from eth_abi import encode
        from eth_utils import to_checksum_address
        
        # Function selector
        function_sig = "redeemPositions(address,bytes32,bytes32,uint256[])"
        function_selector = keccak(text=function_sig)[:4]
        
        # Convert addresses
        collateral_token = to_checksum_address(collateral_token)
        
        # Convert bytes32 strings to bytes
        parent_bytes = bytes.fromhex(parent_collection_id[2:]) if parent_collection_id.startswith("0x") else bytes.fromhex(parent_collection_id)
        condition_bytes = bytes.fromhex(condition_id[2:]) if condition_id.startswith("0x") else bytes.fromhex(condition_id)
        
        # Encode parameters
        encoded_params = encode(
            ["address", "bytes32", "bytes32", "uint256[]"],
            [collateral_token, parent_bytes, condition_bytes, index_sets]
        )
        
        return "0x" + (function_selector + encoded_params).hex()
    
    async def sell_all(
        self,
        asset_id: str,
        size: float,
        max_retries: int = 10,
        min_size: float = 0.01,
    ) -> SellAllResult:
        """Sell entire position with retry logic.
        
        Loop to sell everything, retry if not fully filled.
        """
        remaining_size = size
        total_matched = 0.0
        total_value = 0.0  # For weighted average price
        retry_count = 0
        
        while remaining_size > min_size and retry_count < max_retries:
            result = await self.place_market_order(
                asset_id=asset_id,
                side=OrderSide.SELL,
                amount=remaining_size,
            )
            
            if result and result.size_matched > 0:
                total_matched += result.size_matched
                total_value += result.size_matched * result.price
                remaining_size -= result.size_matched
                
                self.logger.info(
                    f"Sell progress: sold {result.size_matched:.2f}, "
                    f"total: {total_matched:.2f}/{size:.2f}, "
                    f"remaining: {remaining_size:.2f}"
                )
                
                if remaining_size <= min_size:
                    break
                    
                await asyncio.sleep(1.0)
            else:
                self.logger.warning(f"Sell: no fill on retry {retry_count + 1}")
                await asyncio.sleep(2.0)
            
            retry_count += 1
        
        # Calculate weighted average price
        avg_price = total_value / total_matched if total_matched > 0 else 0.0
        is_complete = remaining_size <= min_size
        
        if not is_complete:
            self.logger.error(
                f"Sell incomplete: sold {total_matched:.2f}/{size:.2f}, "
                f"remaining: {remaining_size:.2f} after {retry_count} retries"
            )
        
        return SellAllResult(
            total_size=size,
            total_matched=total_matched,
            remaining=remaining_size,
            avg_price=avg_price,
            is_complete=is_complete,
            retry_count=retry_count,
        )
    
    async def buy_market(
        self,
        asset_id: str,
        amount: float,
        max_retries: int = 10,
        min_amount: float = 1.0,
    ) -> BuyMarketResult:
        """Buy market order with retry logic (FAK).
        
        Loop to buy entire amount, retry if not fully filled.
        Trusts result.size_matched, falls back to balance polling when size_matched=0.
        """
        remaining_amount = amount
        total_matched = 0.0
        total_spent = 0.0
        retry_count = 0
        
        # Get initial balance to track
        initial_balance = await self.get_token_balance(asset_id)
        balance_before = initial_balance
        
        while remaining_amount > min_amount and retry_count < max_retries:
            
            result = await self.place_market_order(
                asset_id=asset_id,
                side=OrderSide.BUY,
                amount=remaining_amount,
                order_type=OrderType.FAK,  # Fill And Kill - increases fill rate
            )
            
            if result:
                # Case 1: result.size_matched > 0 → trust order response
                if result.size_matched > 0:
                    actual_size = result.size_matched
                    spent = actual_size * result.price
                    total_matched += actual_size
                    total_spent += spent
                    remaining_amount -= spent
                    
                    self.logger.info(
                        f"Buy progress: bought {actual_size:.2f} tokens @ ${result.price:.4f}, "
                        f"spent ${spent:.2f}, remaining ${remaining_amount:.2f}"
                    )
                    
                    # Update balance_before for next iteration (estimate)
                    balance_before += actual_size
                    
                    if remaining_amount <= min_amount:
                        break
                else:
                    # Case 2: size_matched = 0 → poll balance to double-check
                    # (API may return wrong, balance sync may be slow)
                    balance_after = balance_before
                    for _ in range(60):  # Max 12s (60 * 200ms)
                        await asyncio.sleep(0.2)
                        balance_after = await self.get_token_balance(asset_id)
                        if balance_after > balance_before:
                            break
                    
                    balance_change = balance_after - balance_before
                    
                    if balance_change > 0:
                        # Balance increased despite size_matched=0 → API response was wrong
                        spent = balance_change * result.price
                        total_matched += balance_change
                        total_spent += spent
                        remaining_amount -= spent
                        balance_before = balance_after
                        
                        self.logger.info(
                            f"Buy progress (from balance): bought {balance_change:.2f} tokens @ ${result.price:.4f}, "
                            f"spent ${spent:.2f}, remaining ${remaining_amount:.2f}"
                        )
                        
                        if remaining_amount <= min_amount:
                            break
                    else:
                        self.logger.warning(f"Buy: no fill on retry {retry_count + 1} (size_matched=0, balance unchanged)")
                        await asyncio.sleep(2.0)
            else:
                self.logger.warning(f"Buy: order failed on retry {retry_count + 1}")
                await asyncio.sleep(2.0)
            
            retry_count += 1
        
        # Final double check with actual balance change
        final_balance = await self.get_token_balance(asset_id)
        actual_total_matched = final_balance - initial_balance
        
        # If large discrepancy (> 1 token), log warning and use balance
        if abs(actual_total_matched - total_matched) > 1.0:
            self.logger.warning(
                f"Balance discrepancy: tracked={total_matched:.2f}, actual={actual_total_matched:.2f}"
            )
            # Use larger value to ensure we don't miss fills
            total_matched = max(total_matched, actual_total_matched)
        
        # Calculate weighted average price
        avg_price = total_spent / total_matched if total_matched > 0 else 0.0
        is_complete = remaining_amount <= min_amount
        
        if not is_complete:
            self.logger.error(
                f"Buy incomplete: spent ${total_spent:.2f}/{amount:.2f}, "
                f"remaining: ${remaining_amount:.2f} after {retry_count} retries"
            )
        
        return BuyMarketResult(
            amount_spent=total_spent,
            total_matched=total_matched,
            remaining=remaining_amount,
            avg_price=avg_price,
            is_complete=is_complete,
            retry_count=retry_count,
        )
    
    async def merge_all(
        self,
        condition_id: str,
        yes_token_id: str,
        no_token_id: str,
        neg_risk: bool = False,
    ) -> MergeAllResult:
        """Auto get balance and merge all possible pairs.
        
        Returns: MergeAllResult with (merge_amount, yes_remaining, no_remaining, tx_hash)
        """
        yes_balance = await self.get_token_balance(yes_token_id)
        no_balance = await self.get_token_balance(no_token_id)
        merge_amount = min(yes_balance, no_balance)
        
        self.logger.info(f"Token balances: YES={yes_balance:.2f}, NO={no_balance:.2f}")
        
        if merge_amount <= 0:
            self.logger.warning("No tokens to merge")
            return MergeAllResult(
                merge_amount=0,
                yes_remaining=yes_balance,
                no_remaining=no_balance,
                tx_hash=None,
            )
        
        self.logger.info(f"Merging {merge_amount:.2f} positions to receive USDC...")
        
        tx_hash = await self.merge_positions(
            condition_id=condition_id,
            amount=merge_amount,
            neg_risk=neg_risk,
        )
        
        if tx_hash:
            usdc_received = merge_amount
            self.logger.info(f"✅ Merge successful! Received ${usdc_received:.2f} USDC. Tx: {tx_hash}")
            return MergeAllResult(
                merge_amount=merge_amount,
                yes_remaining=yes_balance - merge_amount,
                no_remaining=no_balance - merge_amount,
                tx_hash=tx_hash,
            )
        else:
            self.logger.warning("⚠️ Merge failed! Positions still held.")
            return MergeAllResult(
                merge_amount=0,
                yes_remaining=yes_balance,
                no_remaining=no_balance,
                tx_hash=None,
            )

