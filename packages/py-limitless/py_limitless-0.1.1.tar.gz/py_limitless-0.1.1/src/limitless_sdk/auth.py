"""
Limitless Exchange Authentication
Authentication utilities for API access
"""

import requests
from eth_account import Account
from eth_account.messages import encode_defunct

from .constants import API_BASE_URL
from .utils import format_private_key, string_to_hex


def get_signing_message(api_base_url: str = API_BASE_URL) -> str:
    """
    Fetch the signing message from the API.

    Args:
        api_base_url: Base URL for the API

    Returns:
        The signing message to be signed

    Raises:
        Exception: If the request fails
    """
    response = requests.get(f"{api_base_url}/auth/signing-message")
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to get signing message: {response.status_code}")


def sign_message(private_key: str, message: str) -> str:
    """
    Sign a message using a private key.

    Args:
        private_key: Private key for signing
        message: Message to sign

    Returns:
        Hex-encoded signature with 0x prefix
    """
    private_key = format_private_key(private_key)
    account = Account.from_key(private_key)

    message_hash = encode_defunct(text=message)
    signed_message = account.sign_message(message_hash)

    sig_hex = signed_message.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex

    return sig_hex


def authenticate(
    private_key: str,
    signing_message: str | None = None,
    api_base_url: str = API_BASE_URL,
    referral_code: str | None = None,
) -> tuple[str, dict]:
    """
    Authenticate with the Limitless Exchange API.

    Args:
        private_key: Your wallet's private key
        signing_message: Optional pre-fetched signing message
        api_base_url: Base URL for the API
        referral_code: Optional referral code

    Returns:
        Tuple of (session_cookie, user_data)

    Raises:
        Exception: If authentication fails
    """
    private_key = format_private_key(private_key)
    account = Account.from_key(private_key)
    ethereum_address = account.address

    # Get signing message if not provided
    if signing_message is None:
        signing_message = get_signing_message(api_base_url)

    hex_message = string_to_hex(signing_message)

    # Sign the message
    signature = sign_message(private_key, signing_message)

    headers = {
        "x-account": ethereum_address,
        "x-signing-message": hex_message,
        "x-signature": signature,
        "Content-Type": "application/json",
    }

    payload = {"client": "eoa"}
    if referral_code:
        payload["r"] = referral_code

    response = requests.post(f"{api_base_url}/auth/login", headers=headers, json=payload)

    if response.status_code == 200:
        session_cookie = response.cookies.get("limitless_session")
        return session_cookie, response.json()
    else:
        raise Exception(f"Authentication failed: {response.status_code} - {response.text}")


def get_auth_headers(session_cookie: str) -> dict:
    """
    Get headers for authenticated API requests.

    Args:
        session_cookie: Session cookie from authentication

    Returns:
        Headers dict ready for requests
    """
    return {
        "cookie": f"limitless_session={session_cookie}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def get_smart_wallet(private_key: str, api_base_url: str = API_BASE_URL) -> str | None:
    """
    Get the smart wallet address associated with a private key.

    Args:
        private_key: Private key for authentication
        api_base_url: Base URL for the API

    Returns:
        Smart wallet address or None if not found
    """
    try:
        _, user_data = authenticate(private_key, api_base_url=api_base_url)
        return user_data.get("smartWallet")
    except Exception as e:
        print(f"Could not fetch smart wallet: {e}")
        return None
