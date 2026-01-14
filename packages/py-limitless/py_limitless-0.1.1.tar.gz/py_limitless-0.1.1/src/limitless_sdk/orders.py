"""
Limitless Exchange Order Management
Order creation, EIP-712 signing, and API submission
"""

import time
from typing import Literal

import requests
from eth_account import Account

# Import with version compatibility
try:
    from eth_account.messages import encode_typed_data
except ImportError:
    from eth_account.messages import encode_structured_data as encode_typed_data

from .auth import get_auth_headers
from .constants import (
    API_BASE_URL,
    BASE_CHAIN_ID,
    CLOB_ADDRESS,
    NEGRISK_ADDRESS,
    ORDER_TYPES,
    SIDE_BUY,
    SIGNATURE_TYPE_EIP712,
)
from .utils import format_private_key


def get_eip712_domain(venue_exchange_address: str) -> dict:
    """
    Get the EIP-712 domain for order signing.

    Args:
        venue_exchange_address: The venue's exchange contract address from market data.

    Returns:
        EIP-712 domain object
    """
    return {
        "name": "Limitless CTF Exchange",
        "version": "1",
        "chainId": BASE_CHAIN_ID,
        "verifyingContract": venue_exchange_address,
    }


def get_eip712_domain_legacy(market_type: Literal["CLOB", "NEGRISK"] = "CLOB") -> dict:
    """
    DEPRECATED: Use get_eip712_domain(venue_exchange_address) instead.

    Get the EIP-712 domain for order signing using legacy hardcoded addresses.

    Args:
        market_type: 'CLOB' or 'NEGRISK'

    Returns:
        EIP-712 domain object
    """
    contract_address = CLOB_ADDRESS if market_type == "CLOB" else NEGRISK_ADDRESS
    return {
        "name": "Limitless CTF Exchange",
        "version": "1",
        "chainId": BASE_CHAIN_ID,
        "verifyingContract": contract_address,
    }


def create_order_payload(
    maker_address: str,
    signer_address: str,
    token_id: str,
    maker_amount: int,
    taker_amount: int,
    fee_rate_bps: int,
    side: int = SIDE_BUY,
    expiration: int = 0,
    nonce: int = 0,
    signature_type: int = SIGNATURE_TYPE_EIP712,
) -> dict:
    """
    Create the base order payload without signature.

    Args:
        maker_address: The maker's wallet address (smart wallet)
        signer_address: The signer's address (embedded account)
        token_id: The token ID to trade (YES or NO token)
        maker_amount: Amount the maker is offering (scaled by 1e6)
        taker_amount: Amount the maker wants in return (scaled by 1e6)
        fee_rate_bps: Fee rate in basis points
        side: 0 for BUY, 1 for SELL
        expiration: Order expiration timestamp (0 for no expiration)
        nonce: Order nonce
        signature_type: Signature type (2 for EIP-712)

    Returns:
        Order payload ready for signing
    """
    salt = int(time.time() * 1000) + (24 * 60 * 60 * 1000)  # Current time + 24h in ms

    return {
        "salt": salt,
        "maker": maker_address,
        "signer": signer_address,
        "taker": "0x0000000000000000000000000000000000000000",  # Open to any taker
        "tokenId": str(token_id),  # Keep as string for API
        "makerAmount": maker_amount,
        "takerAmount": taker_amount,
        "expiration": str(expiration),
        "nonce": nonce,
        "feeRateBps": fee_rate_bps,
        "side": side,
        "signatureType": signature_type,
    }


def sign_order(
    order_payload: dict,
    private_key: str,
    venue_exchange_address: str,
) -> str:
    """
    Sign an order payload using EIP-712.

    Args:
        order_payload: The order data to sign
        private_key: Private key for signing
        venue_exchange_address: The venue's exchange contract address from market data.

    Returns:
        Hex-encoded signature
    """
    private_key = format_private_key(private_key)
    account = Account.from_key(private_key)

    domain_data = get_eip712_domain(venue_exchange_address)

    # Convert string fields to int for signing
    message_data = {
        "salt": order_payload["salt"],
        "maker": order_payload["maker"],
        "signer": order_payload["signer"],
        "taker": order_payload["taker"],
        "tokenId": int(order_payload["tokenId"]),
        "makerAmount": order_payload["makerAmount"],
        "takerAmount": order_payload["takerAmount"],
        "expiration": int(order_payload["expiration"]) if order_payload["expiration"] else 0,
        "nonce": order_payload["nonce"],
        "feeRateBps": order_payload["feeRateBps"],
        "side": order_payload["side"],
        "signatureType": order_payload["signatureType"],
    }

    # Sign using EIP-712
    encoded_message = encode_typed_data(domain_data, ORDER_TYPES, message_data)
    signed_message = account.sign_message(encoded_message)

    return signed_message.signature.hex()


def submit_order(
    order_payload: dict,
    signature: str,
    owner_id: str,
    market_slug: str,
    price: float,
    order_type: str,
    session_cookie: str,
    api_base_url: str = API_BASE_URL,
) -> dict:
    """
    Submit an order to the API.

    Args:
        order_payload: Order payload with order parameters
        signature: EIP-712 signature
        owner_id: User's owner ID
        market_slug: Market slug identifier
        price: Price in decimal format
        order_type: "GTC" or "FOK"
        session_cookie: Authentication session cookie
        api_base_url: Base URL for the API

    Returns:
        API response with order details. Structure::

            {
                "order": {
                    "id": "uuid",           # Order UUID
                    "createdAt": "...",     # ISO timestamp
                    "makerAmount": 1400000, # Raw maker amount (6 decimals)
                    "takerAmount": 2000000, # Raw taker amount (6 decimals)
                    "price": 0.7,           # Price as decimal
                    "side": 0,              # 0=BUY, 1=SELL
                    "tokenId": "...",       # Position token ID
                    "marketId": 12345,      # Market ID
                    "ownerId": 123,         # Owner ID
                    "status": "LIVE",       # Order status
                    "market": {...},        # Full market details
                    "owner": {...}          # Owner details
                }
            }

    Raises:
        Exception: If order submission fails
    """
    headers = get_auth_headers(session_cookie)

    final_payload = {
        "order": {
            **order_payload,
            "signature": signature,
        },
        "ownerId": owner_id,
        "orderType": order_type,
        "marketSlug": market_slug,
    }

    # Only add price for non-FOK orders
    if order_type != "FOK":
        final_payload["order"]["price"] = price

    response = requests.post(
        f"{api_base_url}/orders", headers=headers, json=final_payload, timeout=35
    )

    if response.status_code != 201:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    return response.json()


def cancel_order(
    order_id: str,
    session_cookie: str,
    api_base_url: str = API_BASE_URL,
) -> dict:
    """
    Cancel an existing order.

    Args:
        order_id: UUID of the order to cancel
        session_cookie: Authentication session cookie
        api_base_url: Base URL for the API

    Returns:
        API response

    Raises:
        Exception: If cancellation fails
    """
    headers = get_auth_headers(session_cookie)
    headers.pop("Content-Type")  # Remove Content-Type header to prevent API validation error

    response = requests.delete(
        f"{api_base_url}/orders/{order_id}",
        headers=headers,
    )

    if response.status_code not in (200, 204):
        raise Exception(f"Cancel failed {response.status_code}: {response.text}")

    return response.json() if response.text else {}


def get_user_orders(
    market_slug: str,
    session_cookie: str,
    api_base_url: str = API_BASE_URL,
) -> list:
    """
    Get user's orders for a specific market.

    Args:
        market_slug: Market slug identifier
        session_cookie: Authentication session cookie
        api_base_url: Base URL for the API

    Returns:
        List of user's orders

    Raises:
        Exception: If request fails
    """
    headers = get_auth_headers(session_cookie)

    response = requests.get(
        f"{api_base_url}/markets/{market_slug}/user-orders",
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get orders: {response.status_code} - {response.text}")

    return response.json()


def cancel_all_orders(
    market_slug: str,
    session_cookie: str,
    api_base_url: str = API_BASE_URL,
) -> dict:
    """
    Cancel all orders in a specific market.

    Args:
        market_slug: Market slug identifier
        session_cookie: Authentication session cookie
        api_base_url: Base URL for the API

    Returns:
        API response

    Raises:
        Exception: If cancellation fails
    """
    headers = get_auth_headers(session_cookie)
    headers.pop("Content-Type")  # Remove Content-Type header to prevent API validation error

    response = requests.delete(
        f"{api_base_url}/orders/all/{market_slug}",
        headers=headers,
    )

    if response.status_code not in (200, 204):
        raise Exception(f"Cancel all failed {response.status_code}: {response.text}")

    return response.json() if response.text else {}


def cancel_orders_batch(
    order_ids: list[str],
    session_cookie: str,
    api_base_url: str = API_BASE_URL,
) -> dict:
    """
    Cancel multiple orders in a single batch operation.

    Args:
        order_ids: List of order IDs to cancel
        session_cookie: Authentication session cookie
        api_base_url: Base URL for the API

    Returns:
        API response with 'message', 'canceled', and 'failed' keys

    Raises:
        Exception: If batch cancellation fails
    """
    headers = get_auth_headers(session_cookie)

    response = requests.post(
        f"{api_base_url}/orders/cancel-batch",
        headers=headers,
        json={"orderIds": order_ids},
    )

    if response.status_code not in (200, 207):
        raise Exception(f"Cancel batch failed {response.status_code}: {response.text}")

    return response.json()


def calculate_trade_amounts(
    price_cents: int | float,
    amount: float,
    side: int = SIDE_BUY,
    scaling_factor: int = 1_000_000,
    order_type: str = "GTC",
) -> tuple[int, int]:
    """
    Calculate maker and taker amounts for a trade.

    Args:
        price_cents: Price in cents (e.g., 65 for 65¢). For FOK orders, this should
            be the current market price + slippage tolerance to ensure fill.
        amount: Number of shares
        side: 0 for BUY, 1 for SELL
        scaling_factor: Scaling factor (default 1e6 for USDC)
        order_type: "GTC" or "FOK"

    Returns:
        Tuple of (maker_amount, taker_amount)

    Note:
        For FOK (Fill or Kill) orders, takerAmount is set to 1 per Limitless API
        semantics. This signals "market order" behavior where makerAmount determines
        the maximum USDC to spend and the exchange fills as much as possible at the
        best available prices. The price_cents parameter is critical for FOK orders
        as it determines the makerAmount budget.
    """
    price_dollars = price_cents / 100
    total_cost = price_dollars * amount

    maker_amount = round(total_cost * scaling_factor)
    taker_amount = round(amount * scaling_factor)

    if side == 1:  # SELL
        maker_amount, taker_amount = taker_amount, maker_amount

    if order_type == "FOK":
        # FOK market order semantics per Limitless API docs:
        # takerAmount=1 signals "fill as much as possible with given makerAmount"
        # The makerAmount controls how much USDC is spent
        taker_amount = 1

    return maker_amount, taker_amount
