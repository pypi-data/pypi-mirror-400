"""
Limitless Exchange Utilities
Common helper functions
"""

from importlib.metadata import version, PackageNotFoundError


def string_to_hex(text: str) -> str:
    """Convert string to hex representation with 0x prefix."""
    return "0x" + text.encode("utf-8").hex()


def assert_eth_account_version(required: str = "0.10.0") -> None:
    """
    Assert that eth-account version matches the required version.
    
    Args:
        required: Required version string (default: "0.10.0")
        
    Raises:
        RuntimeError: If eth-account is not installed or version mismatches
    """
    try:
        installed = version("eth-account")
    except PackageNotFoundError:
        raise RuntimeError("eth-account is not installed")

    if installed != required:
        raise RuntimeError(
            f"eth-account version mismatch: {installed} (expected {required})"
        )


def scale_amount(amount: float, decimals: int = 6) -> int:
    """
    Scale a decimal amount to integer representation.
    
    Args:
        amount: Decimal amount (e.g., 10.5 for 10.5 USDC)
        decimals: Number of decimals (default: 6 for USDC)
        
    Returns:
        Scaled integer amount
    """
    return round(amount * (10 ** decimals))


def unscale_amount(amount: int, decimals: int = 6) -> float:
    """
    Unscale an integer amount to decimal representation.
    
    Args:
        amount: Scaled integer amount
        decimals: Number of decimals (default: 6 for USDC)
        
    Returns:
        Decimal amount
    """
    return amount / (10 ** decimals)


def cents_to_dollars(cents: int | float) -> float:
    """Convert price in cents to dollars."""
    return cents / 100


def dollars_to_cents(dollars: float) -> int:
    """Convert price in dollars to cents."""
    return round(dollars * 100)


def format_address(address: str) -> str:
    """
    Ensure address has 0x prefix.
    
    Args:
        address: Ethereum address with or without 0x prefix
        
    Returns:
        Address with 0x prefix
    """
    if not address.startswith("0x"):
        return "0x" + address
    return address


def format_private_key(private_key: str) -> str:
    """
    Ensure private key has 0x prefix.
    
    Args:
        private_key: Private key with or without 0x prefix
        
    Returns:
        Private key with 0x prefix
    """
    return format_address(private_key)


def strip_0x(hex_string: str) -> str:
    """Remove 0x prefix from hex string if present."""
    if hex_string.startswith("0x"):
        return hex_string[2:]
    return hex_string

