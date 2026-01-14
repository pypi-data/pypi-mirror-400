"""
Limitless Exchange Client
Main client class for trading on Limitless Exchange
"""

from typing import Literal, Optional

import requests
from eth_account import Account
from web3 import Web3

from .approval import (
    # CTF (conditional token) approval for selling
    approve_ctf,
    approve_usdc,
    check_ctf_approval,
    check_usdc_allowance,
    ensure_ctf_approved,
    ensure_usdc_approved,
    get_usdc_balance,
)
from .auth import (
    authenticate,
    get_auth_headers,
    get_signing_message,
)
from .cache import LRUCache
from .constants import (
    API_BASE_URL,
    BASE_CTF_ADDRESS,
    CATEGORY_IDS,
    ORDER_TYPE_GTC,
    SCALING_FACTOR,
    SIDE_BUY,
    SIDE_SELL,
    SIGNATURE_TYPE_EIP712,
    SIGNATURE_TYPE_EOA,
    WalletType,
)
from .orders import (
    calculate_trade_amounts,
    create_order_payload,
    sign_order,
    submit_order,
)
from .orders import (
    cancel_all_orders as _cancel_all_orders,
)
from .orders import (
    cancel_order as _cancel_order,
)
from .orders import (
    get_user_orders as _get_user_orders,
)
from .redemption import (
    EOAPositionRedeemer,
    RedeemablePosition,
    get_redeemable_positions,
)
from .utils import format_private_key

# =============================================================================
# Web3 Instance Cache
# =============================================================================

# Module-level cache for Web3 instances by RPC URL
_web3_instances: dict[str, Web3] = {}


def _get_web3(rpc_url: str) -> Web3:
    """Get or create a cached Web3 instance for the given RPC URL.

    This avoids creating new HTTP connections for every RPC call,
    improving performance for repeated blockchain interactions.

    Args:
        rpc_url: The RPC URL to connect to.

    Returns:
        Web3 instance connected to the RPC URL.
    """
    if rpc_url not in _web3_instances:
        _web3_instances[rpc_url] = Web3(Web3.HTTPProvider(rpc_url))
    return _web3_instances[rpc_url]


class Limitless:
    """
    Main client for interacting with Limitless Exchange.

    Provides methods for authentication, trading, and market data.
    Exposes session credentials for custom API requests.
    Supports both EOA (Externally Owned Account) and Smart Wallet modes.

    Example:
        ```python
        from limitless_sdk import Limitless

        # EOA Mode (simple, single key) - default
        client = Limitless(private_key="0x...", wallet_type="eoa")
        client.authenticate()
        client.buy(market_slug="...", token_id="...", price_cents=50, amount=2)

        # Smart Wallet Mode (separate auth and signing keys)
        client = Limitless(
            private_key="0x...",  # auth key
            signing_wallet_pk="0x...",  # signing key
            wallet_type="smart_wallet"
        )
        client.authenticate()
        client.buy(market_slug="...", token_id="...", price_cents=50, amount=2)

        # Make custom requests using exposed credentials
        headers = client.get_headers()
        response = requests.get("https://api.limitless.exchange/custom", headers=headers)
        ```

    Attributes:
        session_cookie: Authentication session cookie (available after authenticate())
        user_data: User account data from authentication
        account: eth_account.Account instance
        wallet_type: "eoa" or "smart_wallet"
    """

    def __init__(
        self,
        private_key: str,
        signing_wallet_pk: Optional[str] = None,
        wallet_type: WalletType = "eoa",
        api_base_url: str = API_BASE_URL,
        referral_code: Optional[str] = None,
    ):
        """
        Initialize the Limitless client.

        Args:
            private_key: Primary private key (used for auth in both modes, and signing in EOA mode)
            signing_wallet_pk: Signing wallet private key (required for smart_wallet mode)
            wallet_type: "eoa" (default) or "smart_wallet"
            api_base_url: Base URL for the API
            referral_code: Optional referral code for authentication

        Raises:
            ValueError: If wallet_type is "smart_wallet" but signing_wallet_pk is not provided
        """
        self.wallet_type = wallet_type
        self._private_key = format_private_key(private_key)
        self.api_base_url = api_base_url
        self.account = Account.from_key(self._private_key)

        # Handle signing key based on wallet type
        if wallet_type == "smart_wallet":
            if signing_wallet_pk is None:
                raise ValueError("signing_wallet_pk is required for smart_wallet mode")
            self._signing_key = format_private_key(signing_wallet_pk)
        else:
            # EOA mode: use the same key for signing
            self._signing_key = self._private_key

        # Set after authentication
        self.session_cookie: Optional[str] = None
        self.user_data: Optional[dict] = None
        self._referral_code = referral_code

        # HTTP session for connection pooling
        self._session = requests.Session()

        # Venue exchange cache (internal use only for get_venue_exchange)
        # LRU cache with max 100 entries to prevent unbounded growth
        self._venue_exchange_cache: LRUCache = LRUCache(maxsize=100)

    @property
    def address(self) -> str:
        """Get the wallet address."""
        return self.account.address

    @property
    def smart_wallet(self) -> Optional[str]:
        """Get the smart wallet address (available after authentication)."""
        if self.user_data:
            return self.user_data.get("smartWallet")
        return None

    @property
    def embedded_account(self) -> Optional[str]:
        """Get the embedded account address (signer, available after authentication)."""
        if self.user_data:
            return self.user_data.get("embeddedAccount")
        return None

    @property
    def user_id(self) -> Optional[str]:
        """Get the user ID (available after authentication)."""
        if self.user_data:
            return self.user_data.get("id")
        return None

    @property
    def fee_rate_bps(self) -> int:
        """Get the user's fee rate in basis points."""
        if self.user_data:
            rank = self.user_data.get("rank", {})
            return rank.get("feeRateBps", 0)
        return 0

    @property
    def maker_address(self) -> Optional[str]:
        """
        Get the maker address for orders.

        For EOA mode: returns the EOA wallet address.
        For smart_wallet mode: returns the smart wallet address.

        Returns:
            Maker address or None if not authenticated (smart_wallet mode)
        """
        if self.wallet_type == "eoa":
            return self.address
        return self.smart_wallet

    @property
    def signer_address(self) -> Optional[str]:
        """
        Get the signer address for orders.

        For EOA mode: returns the EOA wallet address (same as maker).
        For smart_wallet mode: returns the embedded account address.

        Returns:
            Signer address or None if not authenticated (smart_wallet mode)
        """
        if self.wallet_type == "eoa":
            return self.address
        return self.embedded_account

    @property
    def signature_type(self) -> int:
        """
        Get the signature type for orders.

        Returns:
            0 for EOA mode, 2 for smart_wallet mode
        """
        if self.wallet_type == "eoa":
            return SIGNATURE_TYPE_EOA
        return SIGNATURE_TYPE_EIP712

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self.session_cookie is not None

    @property
    def trade_wallet_option(self) -> Optional[str]:
        """
        Get the server-side tradeWalletOption (available after authentication).

        Returns:
            "eoa" or "smartWallet", or None if not authenticated
        """
        if self.user_data:
            return self.user_data.get("tradeWalletOption")
        return None

    def authenticate(self) -> dict:
        """
        Authenticate with the Limitless Exchange API.

        Validates that the configured wallet_type matches the user's tradeWalletOption.
        If they don't match, automatically updates the tradeWalletOption on the server.

        Returns:
            User data dictionary

        Raises:
            Exception: If authentication fails
        """
        signing_message = get_signing_message(self.api_base_url)
        self.session_cookie, self.user_data = authenticate(
            self._private_key,
            signing_message,
            self.api_base_url,
            referral_code=self._referral_code,
        )

        # Validate and sync wallet type with server's tradeWalletOption
        self._sync_trade_wallet_option()

        return self.user_data

    def _get_expected_trade_wallet_option(self) -> str:
        """Map client wallet_type to API tradeWalletOption value."""
        if self.wallet_type == "eoa":
            return "eoa"
        return "smartWallet"

    def _sync_trade_wallet_option(self) -> None:
        """
        Sync the client's wallet_type with the server's tradeWalletOption.

        If they don't match, updates the server to match the client configuration.
        """
        if not self.user_data:
            return

        current_option = self.user_data.get("tradeWalletOption")
        expected_option = self._get_expected_trade_wallet_option()

        if current_option == expected_option:
            return  # Already in sync

        # Update the trade wallet option on the server
        self._update_trade_wallet_option(expected_option)

    def _update_trade_wallet_option(self, trade_wallet_option: str) -> None:
        """
        Update the tradeWalletOption on the server.

        Args:
            trade_wallet_option: "eoa" or "smartWallet"

        Raises:
            Exception: If the update fails
        """
        # Determine the display name based on wallet option
        if trade_wallet_option == "eoa":
            display_name = self.address
        else:
            display_name = self.smart_wallet

        if not display_name:
            raise RuntimeError(
                f"Cannot update to {trade_wallet_option}: required address not available"
            )

        headers = get_auth_headers(self.session_cookie)

        payload = {
            "tradeWalletOption": trade_wallet_option,
            "displayName": display_name,
        }

        response = self._session.put(
            f"{self.api_base_url}/profiles",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to update tradeWalletOption: {response.status_code} - {response.text}"
            )

        # Update local user_data with the new values
        self.user_data["tradeWalletOption"] = trade_wallet_option
        self.user_data["displayName"] = display_name

    def get_headers(self) -> dict:
        """
        Get headers for authenticated API requests.

        Use this for making custom API calls.

        Returns:
            Headers dict with authentication cookie

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.session_cookie:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return get_auth_headers(self.session_cookie)

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., "/orders" or full URL)
            **kwargs: Additional arguments passed to requests

        Returns:
            Response object

        Example:
            ```python
            # Get market data
            response = client.request("GET", "/markets/my-market-slug")
            data = response.json()

            # Custom POST request
            response = client.request("POST", "/some-endpoint", json={"key": "value"})
            ```
        """
        headers = self.get_headers()

        # Merge with any provided headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Build full URL if endpoint doesn't start with http
        if not endpoint.startswith("http"):
            url = f"{self.api_base_url}{endpoint}"
        else:
            url = endpoint

        return self._session.request(method, url, headers=headers, **kwargs)

    def get_venue_exchange(self, market_slug: str) -> str:
        """
        Get the venue exchange address for a market.

        This address is used as the verifyingContract for EIP-712 signing.
        Market data is cached since venue is static per market.

        Args:
            market_slug: Market slug identifier

        Returns:
            Venue exchange address (checksummed)

        Raises:
            ValueError: If market does not have venue data
        """
        # Check cache first (internal use only)
        market_data = self._venue_exchange_cache.get(market_slug)
        if market_data is None:
            # Fetch and cache
            market_data = self.get_market(market_slug)
            self._venue_exchange_cache[market_slug] = market_data

        venue = market_data.get("venue")
        if not venue or not venue.get("exchange"):
            raise ValueError(f"Market {market_slug} does not have venue data")

        return venue["exchange"]

    def get_ctf_address(self, market_slug: str | None = None) -> str:
        """
        Get the CTF (Conditional Token Framework) contract address.

        This is the global ERC-1155 contract that holds all conditional tokens
        (YES/NO position tokens) for all Limitless markets on Base.
        Must be approved before selling positions.

        Args:
            market_slug: Unused - kept for API compatibility. CTF is global.

        Returns:
            CTF contract address (checksummed)
        """
        return BASE_CTF_ADDRESS

    def execute_trade(
        self,
        market_slug: str,
        token_id: str,
        price_cents: int | float,
        amount: float,
        side: Literal["BUY", "SELL"] | int = "BUY",
        token_type: Literal["YES", "NO"] = "YES",
        order_type: str = ORDER_TYPE_GTC,
    ) -> dict:
        """
        Execute a trade on Limitless Exchange.

        Automatically fetches venue exchange address from market data for signing.

        Args:
            market_slug: Market slug identifier
            token_id: Token ID to trade (YES or NO token)
            price_cents: Price in cents (e.g., 65 for 65¢)
            amount: Number of shares
            side: "BUY" or "SELL" (or 0/1)
            token_type: "YES" or "NO" (for logging)
            order_type: "GTC" (Good Till Cancelled) or "FOK" (Fill Or Kill)

        Returns:
            Order result from API

        Raises:
            RuntimeError: If not authenticated
            Exception: If trade execution fails
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        # Get venue exchange address for signing
        venue_exchange = self.get_venue_exchange(market_slug)

        # Convert side string to int
        if isinstance(side, str):
            side_int = SIDE_BUY if side.upper() == "BUY" else SIDE_SELL
        else:
            side_int = side

        # Calculate amounts
        maker_amount, taker_amount = calculate_trade_amounts(
            price_cents, amount, side_int, SCALING_FACTOR, order_type
        )

        # Create order payload with wallet-type-aware addresses and signature type
        order_payload = create_order_payload(
            maker_address=self.maker_address,
            signer_address=self.signer_address,
            token_id=token_id,
            maker_amount=maker_amount,
            taker_amount=taker_amount,
            fee_rate_bps=self.fee_rate_bps,
            side=side_int,
            signature_type=self.signature_type,
        )

        # Sign the order with the venue's exchange address
        signature = sign_order(order_payload, self._signing_key, venue_exchange)

        # Submit to API
        price_dollars = round(price_cents / 100, 3)
        result = submit_order(
            order_payload=order_payload,
            signature=signature,
            owner_id=self.user_id,
            market_slug=market_slug,
            price=price_dollars,
            order_type=order_type,
            session_cookie=self.session_cookie,
            api_base_url=self.api_base_url,
        )

        return result

    def buy(
        self,
        market_slug: str,
        token_id: str,
        price_cents: int | float,
        amount: float,
        token_type: Literal["YES", "NO"] = "YES",
        order_type: str = ORDER_TYPE_GTC,
    ) -> dict:
        """
        Place a buy order.

        Convenience method for execute_trade with side="BUY".

        Args:
            market_slug: Market slug identifier
            token_id: Token ID to buy
            price_cents: Price in cents
            amount: Number of shares
            token_type: "YES" or "NO"
            order_type: "GTC" or "FOK"

        Returns:
            Order result from API
        """
        return self.execute_trade(
            market_slug=market_slug,
            token_id=token_id,
            price_cents=price_cents,
            amount=amount,
            side="BUY",
            token_type=token_type,
            order_type=order_type,
        )

    def sell(
        self,
        market_slug: str,
        token_id: str,
        price_cents: int | float,
        amount: float,
        token_type: Literal["YES", "NO"] = "YES",
        order_type: str = ORDER_TYPE_GTC,
    ) -> dict:
        """
        Place a sell order.

        Convenience method for execute_trade with side="SELL".

        Args:
            market_slug: Market slug identifier
            token_id: Token ID to sell
            price_cents: Price in cents
            amount: Number of shares
            token_type: "YES" or "NO"
            order_type: "GTC" or "FOK"

        Returns:
            Order result from API
        """
        return self.execute_trade(
            market_slug=market_slug,
            token_id=token_id,
            price_cents=price_cents,
            amount=amount,
            side="SELL",
            token_type=token_type,
            order_type=order_type,
        )

    def cancel_order(self, order_id: str) -> dict:
        """
        Cancel an existing order.

        Args:
            order_id: UUID of the order to cancel

        Returns:
            API response

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        return _cancel_order(
            order_id=order_id,
            session_cookie=self.session_cookie,
            api_base_url=self.api_base_url,
        )

    def cancel_all_orders(self, market_slug: str) -> dict:
        """
        Cancel all orders in a specific market.

        Args:
            market_slug: Market slug identifier

        Returns:
            API response

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        return _cancel_all_orders(
            market_slug=market_slug,
            session_cookie=self.session_cookie,
            api_base_url=self.api_base_url,
        )

    def cancel_orders_batch(self, order_ids: list[str]) -> dict:
        """
        Cancel multiple orders in a single batch request.

        NOTE: All orders must be from the same market. Use cancel_all_user_orders()
        for canceling orders across multiple markets.

        Args:
            order_ids: List of order IDs to cancel (must all be from the same market)

        Returns:
            Dict with:
                - message: Success message
                - canceled: List of successfully canceled order IDs
                - failed: List of failed cancellations with reasons

        Raises:
            RuntimeError: If not authenticated
            requests.HTTPError: If the API request fails (e.g., orders from multiple markets)
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        if not order_ids:
            return {"message": "No orders to cancel", "canceled": [], "failed": []}

        response = self.request("POST", "/orders/cancel-batch", json={"orderIds": order_ids})

        # Raise exception on HTTP errors (4xx, 5xx)
        response.raise_for_status()

        return response.json()

    def _get_market_cached(self, market_slug: str) -> dict:
        """Get market data, using cache if available.

        Args:
            market_slug: Market slug to fetch.

        Returns:
            Market data dictionary.
        """
        if market_slug not in self._venue_exchange_cache:
            self._venue_exchange_cache[market_slug] = self.get_market(market_slug)
        return self._venue_exchange_cache[market_slug]

    def get_user_orders_smart(self, market_slugs: list[str] = None) -> list[dict]:
        """
        Get user orders using fast/slow path strategy.

        Combines two query strategies:
        1. Fast per-market queries for specified markets (authoritative)
        2. Portfolio query for comprehensive coverage (only for non-specified markets)

        For any market queried via fast path, those results are authoritative.
        If fast path returns no orders for a specified market, slow path orders
        for that market are ignored (they're likely stale).

        Args:
            market_slugs: Optional list of market slugs to query directly (fast path).
                         If None, only slow path (portfolio) is used.

        Returns:
            Deduplicated list of order dictionaries with market_slug included.
        """
        all_orders = {}  # order_id -> order dict (for deduplication)
        fast_path_markets = set()

        # 1. Fast path: Query specific markets directly (authoritative)
        if market_slugs:
            for market_slug in market_slugs:
                fast_path_markets.add(market_slug)
                try:
                    market_orders = self.get_user_orders(market_slug)

                    for order in market_orders:
                        # Only include live orders
                        if order.get("status", "").upper() == "LIVE":
                            all_orders[order["id"]] = {
                                **order,
                                "market_slug": market_slug,
                            }
                except Exception:
                    # If market query fails, continue (fallback to portfolio)
                    pass

        # 2. Slow path: Portfolio query to catch any orders missed by fast path
        # Always run this to find orders in markets not in the provided list
        portfolio_orders = self._get_orders_from_portfolio()
        for order in portfolio_orders:
            market_slug = order.get("market_slug", "")
            # Skip orders from markets already queried via fast path
            if market_slug in fast_path_markets:
                continue
            # Add orders from markets not covered by fast path
            if order["id"] not in all_orders:
                all_orders[order["id"]] = order

        return list(all_orders.values())

    def _get_orders_from_portfolio(self) -> list[dict]:
        """Extract orders from portfolio positions (slow path)."""
        portfolio = self.get_portfolio_positions()
        clob_positions = portfolio.get("clob", [])

        orders = []
        for position in clob_positions:
            market = position.get("market", {})
            market_slug = market.get("slug", "")

            orders_data = position.get("orders", {})
            live_orders = orders_data.get("liveOrders", [])

            for order in live_orders:
                # Normalize order format to match get_user_orders
                normalized_order = {
                    "id": order.get("id", ""),
                    "market_slug": market_slug,
                    "side": order.get("side", "buy").lower(),
                    "token": order.get("token", ""),
                    "price": order.get("price", ""),
                    "originalSize": order.get("originalSize", ""),
                    "filledSize": order.get("filledSize", ""),
                    "status": order.get("status", ""),
                }
                orders.append(normalized_order)

        return orders

    def cancel_all_user_orders(self, market_slugs: list[str] = None) -> dict:
        """
        Cancel all user orders using smart fast/slow path logic with batch cancellation.

        Groups orders by market and cancels each market's orders in a separate batch
        request (API requires all orders in a batch to be from the same market).

        Args:
            market_slugs: Optional list of market slugs to prioritize (fast path).
                         If provided, these markets are queried directly first.

        Returns:
            Dict with summary of canceled and failed orders:
                - markets_processed: Number of markets that had orders
                - total_canceled: List of successfully canceled order IDs
                - total_failed: List of failed cancellations with reasons
                - market_results: Per-market breakdown

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        # Get most up-to-date orders using fast/slow path logic
        all_orders = self.get_user_orders_smart(market_slugs)

        if not all_orders:
            return {
                "markets_processed": 0,
                "total_canceled": [],
                "total_failed": [],
                "market_results": [],
            }

        # Group orders by market (API requires all orders in batch to be from same market)
        orders_by_market: dict[str, list[dict]] = {}
        for order in all_orders:
            market_slug = order.get("market_slug", "")
            if market_slug not in orders_by_market:
                orders_by_market[market_slug] = []
            orders_by_market[market_slug].append(order)

        # Cancel orders market by market
        total_canceled: list[str] = []
        total_failed: list[dict] = []
        market_results: list[dict] = []

        for market_slug, orders in orders_by_market.items():
            order_ids = [order["id"] for order in orders]
            market_canceled: list[str] = []
            market_failed: list[dict] = []

            try:
                batch_result = self.cancel_orders_batch(order_ids)

                # Extract canceled/failed from API result
                canceled = batch_result.get("canceled", [])
                failed = batch_result.get("failed", [])

                # If API doesn't provide lists, assume success (request didn't raise)
                if not canceled and not failed:
                    canceled = order_ids

                market_canceled = canceled
                market_failed = failed

            except Exception as e:
                # Batch request failed - mark all orders as failed
                for order_id in order_ids:
                    market_failed.append(
                        {
                            "orderId": order_id,
                            "reason": "BATCH_ERROR",
                            "message": str(e),
                        }
                    )

            total_canceled.extend(market_canceled)
            total_failed.extend(market_failed)
            market_results.append(
                {
                    "market_slug": market_slug,
                    "orders_count": len(orders),
                    "result": {
                        "canceled": market_canceled,
                        "failed": market_failed,
                    },
                }
            )

        return {
            "markets_processed": len(orders_by_market),
            "total_canceled": total_canceled,
            "total_failed": total_failed,
            "market_results": market_results,
        }

    def get_user_orders(self, market_slug: str) -> list:
        """
        Get user's orders for a specific market.

        Args:
            market_slug: Market slug identifier

        Returns:
            List of user's orders

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        return _get_user_orders(
            market_slug=market_slug,
            session_cookie=self.session_cookie,
            api_base_url=self.api_base_url,
        )

    def get_portfolio_positions(self) -> dict:
        """
        Get user's portfolio positions.

        Returns:
            Portfolio positions data

        Raises:
            RuntimeError: If not authenticated
        """
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        response = self.request("GET", "/portfolio/positions")
        return response.json()

    # Market Data Methods (no authentication required)

    def get_market(self, market_slug: str) -> dict:
        """
        Get market details by slug.

        Args:
            market_slug: Market slug identifier

        Returns:
            Market data dictionary
        """
        response = self._session.get(f"{self.api_base_url}/markets/{market_slug}")
        response.raise_for_status()
        return response.json()

    def get_orderbook(self, market_slug: str) -> dict:
        """
        Get orderbook data for a market.

        Args:
            market_slug: Market slug identifier

        Returns:
            Orderbook data dictionary
        """
        response = self._session.get(f"{self.api_base_url}/markets/{market_slug}/orderbook")
        response.raise_for_status()
        return response.json()

    def get_active_markets(
        self,
        category_id: int,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "newest",
    ) -> dict:
        """
        Get active markets in a category.

        Args:
            category_id: Category ID (see CATEGORY_IDS constant)
            page: Page number
            limit: Results per page
            sort_by: Sort order

        Returns:
            Dictionary with "data" list of markets
        """
        response = self._session.get(
            f"{self.api_base_url}/markets/active/{category_id}",
            params={
                "page": str(page),
                "limit": str(limit),
                "sortBy": sort_by,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_categories(self) -> dict:
        """
        Get market categories with counts.

        Returns:
            Categories data
        """
        response = self._session.get(f"{self.api_base_url}/markets/categories/count")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_category_name(category_id: int) -> str:
        """
        Get human-readable category name.

        Args:
            category_id: Category ID

        Returns:
            Category name or "Unknown"
        """
        return CATEGORY_IDS.get(category_id, "Unknown")

    # USDC Approval Methods (for EOA mode)

    def check_usdc_allowance_for_market(
        self,
        market_slug: str,
        rpc_url: str = "https://mainnet.base.org",
    ) -> int:
        """
        Check USDC allowance for a market's venue exchange.

        Args:
            market_slug: Market slug identifier
            rpc_url: Base RPC URL

        Returns:
            Current allowance in raw units (6 decimals)
        """
        venue_exchange = self.get_venue_exchange(market_slug)
        w3 = _get_web3(rpc_url)
        return check_usdc_allowance(w3, self.address, venue_exchange)

    def approve_usdc_for_market(
        self,
        market_slug: str,
        rpc_url: str = "https://mainnet.base.org",
        amount: Optional[int] = None,
    ) -> str:
        """
        Approve USDC spending for a market's venue exchange.

        Args:
            market_slug: Market slug identifier
            rpc_url: Base RPC URL
            amount: Amount to approve (default: unlimited)

        Returns:
            Transaction hash
        """
        venue_exchange = self.get_venue_exchange(market_slug)
        w3 = _get_web3(rpc_url)

        if amount is not None:
            return approve_usdc(w3, self._private_key, venue_exchange, amount)
        return approve_usdc(w3, self._private_key, venue_exchange)

    def ensure_usdc_approved_for_market(
        self,
        market_slug: str,
        rpc_url: str = "https://mainnet.base.org",
        min_amount: int = 0,
    ) -> dict:
        """
        Check and approve USDC for a market if needed.

        Args:
            market_slug: Market slug identifier
            rpc_url: Base RPC URL
            min_amount: Minimum required allowance (0 for any)

        Returns:
            Dict with:
                - already_approved: bool
                - tx_hash: str | None
                - allowance: int
        """
        venue_exchange = self.get_venue_exchange(market_slug)
        w3 = _get_web3(rpc_url)
        return ensure_usdc_approved(w3, self._private_key, venue_exchange, min_amount)

    def get_usdc_balance(self, rpc_url: str = "https://mainnet.base.org") -> int:
        """
        Get USDC balance for this wallet.

        Args:
            rpc_url: Base RPC URL

        Returns:
            USDC balance in raw units (6 decimals)
        """
        w3 = _get_web3(rpc_url)
        return get_usdc_balance(w3, self.address)

    # CTF (Conditional Token) Approval Methods (for selling)

    def check_ctf_approval_for_market(
        self,
        market_slug: str,
        rpc_url: str = "https://mainnet.base.org",
    ) -> bool:
        """
        Check if CTF tokens are approved for a market's venue exchange.

        This approval is required before selling positions.

        Args:
            market_slug: Market slug identifier
            rpc_url: Base RPC URL

        Returns:
            True if approved, False otherwise
        """
        ctf_address = self.get_ctf_address(market_slug)
        venue_exchange = self.get_venue_exchange(market_slug)
        w3 = _get_web3(rpc_url)
        return check_ctf_approval(w3, ctf_address, self.address, venue_exchange)

    def approve_ctf_for_market(
        self,
        market_slug: str,
        rpc_url: str = "https://mainnet.base.org",
        approved: bool = True,
    ) -> str:
        """
        Approve CTF token transfers for a market's venue exchange.

        This is required before selling positions.

        Args:
            market_slug: Market slug identifier
            rpc_url: Base RPC URL
            approved: Whether to approve (True) or revoke (False)

        Returns:
            Transaction hash
        """
        ctf_address = self.get_ctf_address(market_slug)
        venue_exchange = self.get_venue_exchange(market_slug)
        w3 = _get_web3(rpc_url)
        return approve_ctf(w3, self._private_key, ctf_address, venue_exchange, approved)

    def ensure_ctf_approved_for_market(
        self,
        market_slug: str,
        rpc_url: str = "https://mainnet.base.org",
    ) -> dict:
        """
        Check and approve CTF for a market if needed.

        This approval is required before selling positions.

        Args:
            market_slug: Market slug identifier
            rpc_url: Base RPC URL

        Returns:
            Dict with:
                - already_approved: bool
                - tx_hash: str | None
        """
        ctf_address = self.get_ctf_address(market_slug)
        venue_exchange = self.get_venue_exchange(market_slug)
        w3 = _get_web3(rpc_url)
        return ensure_ctf_approved(w3, self._private_key, ctf_address, venue_exchange)

    # Position Redemption Methods (for EOA wallets)

    def get_redeemable_positions(self) -> list[RedeemablePosition]:
        """
        Get all redeemable positions from resolved markets.

        Returns positions where the user holds winning tokens that can be
        redeemed for USDC.

        Returns:
            List of RedeemablePosition objects

        Example:
            ```python
            redeemable = client.get_redeemable_positions()
            for pos in redeemable:
                print(f"{pos.market_title}: ${pos.balance} {pos.winning_token}")
            ```
        """
        portfolio = self.get_portfolio_positions()
        return get_redeemable_positions(portfolio)

    def redeem_position(
        self,
        condition_id: str,
        rpc_url: str = "https://mainnet.base.org",
        wait_for_receipt: bool = True,
    ) -> dict:
        """
        Redeem a resolved position for USDC.

        Calls the CTF contract to redeem winning tokens.
        Requires ETH for gas.

        Args:
            condition_id: Condition ID of the resolved market (32 bytes hex)
            rpc_url: Base RPC URL
            wait_for_receipt: Whether to wait for transaction confirmation

        Returns:
            Dict with:
                - tx_hash: Transaction hash
                - receipt: Transaction receipt (if wait_for_receipt=True)
                - success: Whether the transaction was successful

        Raises:
            ValueError: If condition_id is invalid
            Exception: If transaction fails

        Example:
            ```python
            result = client.redeem_position("0x8fee844847e80120f263...")
            print(f"Redeemed: {result['tx_hash']}")
            ```
        """
        redeemer = EOAPositionRedeemer(
            private_key=self._private_key,
            rpc_url=rpc_url,
        )

        tx_hash = redeemer.redeem_position(condition_id)

        result = {
            "tx_hash": tx_hash,
            "receipt": None,
            "success": False,
        }

        if wait_for_receipt:
            receipt = redeemer.wait_for_receipt(tx_hash)
            result["receipt"] = receipt
            result["success"] = receipt.get("status") == 1

        return result

    def redeem_all_positions(
        self,
        rpc_url: str = "https://mainnet.base.org",
    ) -> list[dict]:
        """
        Redeem all redeemable positions sequentially.

        Each position is redeemed in a separate transaction. The method waits
        for each transaction to be confirmed before starting the next one.

        Args:
            rpc_url: Base RPC URL

        Returns:
            List of result dicts, each with:
                - condition_id: The condition ID
                - market_title: Market title
                - balance: Amount redeemed
                - tx_hash: Transaction hash
                - success: Whether the transaction was successful
                - error: Error message if failed

        Example:
            ```python
            results = client.redeem_all_positions()
            for r in results:
                if r['success']:
                    print(f"Redeemed ${r['balance']} from {r['market_title']}")
            ```
        """
        redeemable = self.get_redeemable_positions()

        if not redeemable:
            return []

        redeemer = EOAPositionRedeemer(
            private_key=self._private_key,
            rpc_url=rpc_url,
        )

        # Redeem one-by-one, waiting for each to confirm before the next
        results = []
        for pos in redeemable:
            result = {
                "condition_id": pos.condition_id,
                "market_title": pos.market_title,
                "balance": pos.balance,
                "tx_hash": None,
                "success": False,
                "error": None,
            }

            try:
                tx_hash = redeemer.redeem_position(pos.condition_id)
                result["tx_hash"] = tx_hash

                # Wait for confirmation before proceeding to next
                receipt = redeemer.wait_for_receipt(tx_hash)
                result["success"] = receipt.get("status") == 1

            except Exception as e:
                result["error"] = str(e)

            results.append(result)

        return results

    def estimate_redemption_gas(
        self,
        condition_id: str,
        rpc_url: str = "https://mainnet.base.org",
    ) -> dict:
        """
        Estimate gas for redeeming a position.

        Args:
            condition_id: Condition ID of the resolved market
            rpc_url: Base RPC URL

        Returns:
            Dict with:
                - gas_units: Estimated gas units
                - gas_price_gwei: Current gas price in gwei
                - estimated_cost_eth: Estimated cost in ETH
                - eth_balance: Current ETH balance
                - has_sufficient_gas: Whether user has enough ETH
        """
        redeemer = EOAPositionRedeemer(
            private_key=self._private_key,
            rpc_url=rpc_url,
        )

        gas_units = redeemer.estimate_gas(condition_id)
        base_fee = redeemer.w3.eth.get_block("latest")["baseFeePerGas"]
        gas_price_gwei = base_fee / 1e9
        estimated_cost_eth = (gas_units * base_fee) / 1e18
        eth_balance = redeemer.get_eth_balance()

        return {
            "gas_units": gas_units,
            "gas_price_gwei": float(gas_price_gwei),
            "estimated_cost_eth": float(estimated_cost_eth),
            "eth_balance": float(eth_balance),
            "has_sufficient_gas": eth_balance >= estimated_cost_eth * 1.2,  # 20% buffer
        }
