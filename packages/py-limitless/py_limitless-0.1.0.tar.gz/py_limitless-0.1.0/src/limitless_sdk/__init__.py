"""
Limitless Exchange Python SDK
A comprehensive library for trading on Limitless Exchange.

Supports both EOA (Externally Owned Account) and Smart Wallet signature modes.

Example:
    ```python
    from limitless_sdk import Limitless, LimitlessWebSocket

    # EOA Mode (simple, single key) - default
    client = Limitless(private_key="0x...", wallet_type="eoa")
    client.authenticate()
    client.buy(market_slug="my-market", token_id="123...", price_cents=65, amount=10)

    # Smart Wallet Mode (separate auth and signing keys)
    client = Limitless(
        private_key="0x...",  # auth key
        signing_wallet_pk="0x...",  # signing key
        wallet_type="smart_wallet"
    )
    client.authenticate()
    client.buy(market_slug="my-market", token_id="123...", price_cents=65, amount=10)

    # WebSocket subscriptions
    async def main():
        ws = LimitlessWebSocket(private_key="0x...")
        await ws.connect()
        ws.on("orderbook", lambda data: print(data))
        await ws.subscribe_markets(market_slugs=["my-market"])
        await ws.wait()
    ```
"""

# USDC Approval utilities (for EOA mode - buying)
# CTF (Conditional Token) Approval utilities (for EOA mode - selling)
from .approval import (
    approve_ctf,
    approve_usdc,
    check_ctf_approval,
    check_usdc_allowance,
    ensure_ctf_approved,
    ensure_usdc_approved,
    get_usdc_balance,
)

# Auth utilities (for custom integrations)
from .auth import (
    authenticate,
    get_auth_headers,
    get_signing_message,
    get_smart_wallet,
    sign_message,
)

# Cache utilities
from .cache import LRUCache
from .client import Limitless

# Constants
from .constants import (
    API_BASE_URL,
    BASE_CHAIN_ID,
    # CTF (Conditional Token Framework) contract
    BASE_CTF_ADDRESS,
    CATEGORY_IDS,
    CLOB_ADDRESS,
    # CTF ABI (for position redemption)
    CTF_ABI,
    # EIP-4337 constants
    ENTRY_POINT_V06,
    ENTRY_POINT_V07,
    ERC20_ABI,
    # ERC-1155 constants (for conditional token approval)
    ERC1155_ABI,
    MARKET_TYPE_CLOB,
    MARKET_TYPE_NEGRISK,
    MAX_UINT256,
    NEGRISK_ADDRESS,
    ORDER_TYPE_FOK,
    ORDER_TYPE_GTC,
    ORDER_TYPES,
    SAFE_4337_MODULE_V06,
    SAFE_4337_MODULE_V07,
    SCALING_FACTOR,
    SIDE_BUY,
    SIDE_SELL,
    SIGNATURE_TYPE_EIP712,
    # Signature types
    SIGNATURE_TYPE_EOA,
    # USDC constants
    USDC_ADDRESS,
    USDC_DECIMALS,
    WEBSOCKET_URL,
    # Wallet type
    WalletType,
)

# Order utilities (for advanced usage)
from .orders import (
    calculate_trade_amounts,
    cancel_order,
    create_order_payload,
    get_eip712_domain,
    get_eip712_domain_legacy,
    get_user_orders,
    sign_order,
    submit_order,
)
# Position Redemption (for claiming resolved positions)
from .redemption import (
    EOAPositionRedeemer,
    PositionRedeemer,
    RedeemablePosition,
    get_redeemable_positions,
)

# Utility functions
from .utils import (
    assert_eth_account_version,
    cents_to_dollars,
    dollars_to_cents,
    format_address,
    format_private_key,
    scale_amount,
    string_to_hex,
    strip_0x,
    unscale_amount,
)
from .websocket import LimitlessWebSocket

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "Limitless",
    "LimitlessWebSocket",
    "PositionRedeemer",
    "EOAPositionRedeemer",
    "RedeemablePosition",
    "LRUCache",
    # Auth
    "authenticate",
    "get_signing_message",
    "sign_message",
    "get_auth_headers",
    "get_smart_wallet",
    # Orders
    "create_order_payload",
    "sign_order",
    "submit_order",
    "cancel_order",
    "get_user_orders",
    "calculate_trade_amounts",
    "get_eip712_domain",
    "get_eip712_domain_legacy",
    # USDC Approval (buying)
    "check_usdc_allowance",
    "approve_usdc",
    "ensure_usdc_approved",
    "get_usdc_balance",
    # CTF Approval (selling)
    "check_ctf_approval",
    "approve_ctf",
    "ensure_ctf_approved",
    # Position Redemption
    "get_redeemable_positions",
    # Constants
    "API_BASE_URL",
    "BASE_CTF_ADDRESS",
    "WEBSOCKET_URL",
    "CLOB_ADDRESS",
    "NEGRISK_ADDRESS",
    "BASE_CHAIN_ID",
    "ORDER_TYPES",
    "CATEGORY_IDS",
    "SIDE_BUY",
    "SIDE_SELL",
    "ORDER_TYPE_GTC",
    "ORDER_TYPE_FOK",
    "MARKET_TYPE_CLOB",
    "MARKET_TYPE_NEGRISK",
    "SCALING_FACTOR",
    "USDC_DECIMALS",
    "SIGNATURE_TYPE_EOA",
    "SIGNATURE_TYPE_EIP712",
    "WalletType",
    "ENTRY_POINT_V06",
    "ENTRY_POINT_V07",
    "SAFE_4337_MODULE_V06",
    "SAFE_4337_MODULE_V07",
    "USDC_ADDRESS",
    "MAX_UINT256",
    "ERC20_ABI",
    "ERC1155_ABI",
    "CTF_ABI",
    # Utils
    "string_to_hex",
    "scale_amount",
    "unscale_amount",
    "cents_to_dollars",
    "dollars_to_cents",
    "format_address",
    "format_private_key",
    "strip_0x",
    "assert_eth_account_version",
]
