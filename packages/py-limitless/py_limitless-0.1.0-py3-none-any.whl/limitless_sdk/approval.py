"""
Limitless Exchange Approval Helpers
Functions for checking and setting allowances for venue exchanges.

Includes:
- USDC (ERC-20) approval for buying
- Conditional token (ERC-1155) approval for selling
"""

from eth_account import Account
from web3 import Web3

from .constants import (
    BASE_CHAIN_ID,
    ERC20_ABI,
    ERC1155_ABI,
    MAX_UINT256,
    USDC_ADDRESS,
)
from .utils import format_private_key


def get_usdc_contract(w3: Web3) -> "Web3.eth.contract":
    """Get the USDC contract instance.

    Args:
        w3: Web3 instance connected to Base.

    Returns:
        USDC contract instance.
    """
    return w3.eth.contract(
        address=Web3.to_checksum_address(USDC_ADDRESS),
        abi=ERC20_ABI,
    )


def check_usdc_allowance(w3: Web3, owner: str, spender: str) -> int:
    """Check current USDC allowance for a spender.

    Args:
        w3: Web3 instance connected to Base.
        owner: Owner address (the wallet granting approval).
        spender: Spender address (the venue exchange contract).

    Returns:
        Current allowance in raw units (6 decimals).
    """
    usdc = get_usdc_contract(w3)
    return usdc.functions.allowance(
        Web3.to_checksum_address(owner),
        Web3.to_checksum_address(spender),
    ).call()


def approve_usdc(
    w3: Web3,
    private_key: str,
    spender: str,
    amount: int = MAX_UINT256,
    wait_for_receipt: bool = True,
) -> str:
    """Approve USDC spending for a spender address.

    Args:
        w3: Web3 instance connected to Base.
        private_key: Private key of the owner wallet.
        spender: Spender address (the venue exchange contract).
        amount: Amount to approve (default: unlimited).
        wait_for_receipt: Whether to wait for transaction confirmation.

    Returns:
        Transaction hash as hex string.

    Raises:
        Exception: If transaction fails.
    """
    private_key = format_private_key(private_key)
    account = Account.from_key(private_key)
    owner_address = account.address

    usdc = get_usdc_contract(w3)

    # Build transaction
    nonce = w3.eth.get_transaction_count(owner_address)
    gas_price = w3.eth.gas_price

    approve_tx = usdc.functions.approve(
        Web3.to_checksum_address(spender),
        amount,
    ).build_transaction(
        {
            "from": owner_address,
            "nonce": nonce,
            "gas": 100000,  # Approve typically uses ~50k gas
            "gasPrice": gas_price,
            "chainId": BASE_CHAIN_ID,
        }
    )

    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(approve_tx, private_key)
    # Handle both old (rawTransaction) and new (raw_transaction) attribute names
    raw_tx = getattr(signed_tx, "raw_transaction", None) or signed_tx.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw_tx)

    if wait_for_receipt:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status != 1:
            raise Exception(f"USDC approval transaction failed: {tx_hash.hex()}")

    return tx_hash.hex()


def ensure_usdc_approved(
    w3: Web3,
    private_key: str,
    spender: str,
    min_amount: int = 0,
) -> dict:
    """Check USDC allowance and approve if needed.

    Args:
        w3: Web3 instance connected to Base.
        private_key: Private key of the owner wallet.
        spender: Spender address (the venue exchange contract).
        min_amount: Minimum required allowance (0 means any approval is sufficient).

    Returns:
        Dict with:
            - already_approved: bool - True if approval was already sufficient
            - tx_hash: str | None - Transaction hash if approval was needed
            - allowance: int - Current allowance after operation
    """
    private_key = format_private_key(private_key)
    account = Account.from_key(private_key)
    owner_address = account.address

    current_allowance = check_usdc_allowance(w3, owner_address, spender)

    # Check if approval is sufficient
    if min_amount == 0:
        # Any approval is fine, check if unlimited
        if current_allowance >= MAX_UINT256 // 2:
            return {
                "already_approved": True,
                "tx_hash": None,
                "allowance": current_allowance,
            }
    elif current_allowance >= min_amount:
        return {
            "already_approved": True,
            "tx_hash": None,
            "allowance": current_allowance,
        }

    # Need to approve
    tx_hash = approve_usdc(w3, private_key, spender)
    new_allowance = check_usdc_allowance(w3, owner_address, spender)

    return {
        "already_approved": False,
        "tx_hash": tx_hash,
        "allowance": new_allowance,
    }


def get_usdc_balance(w3: Web3, address: str) -> int:
    """Get USDC balance for an address.

    Args:
        w3: Web3 instance connected to Base.
        address: Wallet address.

    Returns:
        USDC balance in raw units (6 decimals).
    """
    usdc = get_usdc_contract(w3)
    return usdc.functions.balanceOf(
        Web3.to_checksum_address(address),
    ).call()


# =============================================================================
# Conditional Token (ERC-1155) Approval Functions
# Used when selling positions - must approve venue exchange to transfer tokens
# =============================================================================


def get_ctf_contract(w3: Web3, ctf_address: str) -> "Web3.eth.contract":
    """Get the Conditional Token Framework (ERC-1155) contract instance.

    Args:
        w3: Web3 instance connected to Base.
        ctf_address: Address of the CTF contract.

    Returns:
        CTF contract instance.
    """
    return w3.eth.contract(
        address=Web3.to_checksum_address(ctf_address),
        abi=ERC1155_ABI,
    )


def check_ctf_approval(w3: Web3, ctf_address: str, owner: str, operator: str) -> bool:
    """Check if an operator is approved to transfer all tokens for an owner.

    Args:
        w3: Web3 instance connected to Base.
        ctf_address: Address of the CTF contract.
        owner: Owner address (the wallet granting approval).
        operator: Operator address (the venue exchange contract).

    Returns:
        True if approved, False otherwise.
    """
    ctf = get_ctf_contract(w3, ctf_address)
    return ctf.functions.isApprovedForAll(
        Web3.to_checksum_address(owner),
        Web3.to_checksum_address(operator),
    ).call()


def approve_ctf(
    w3: Web3,
    private_key: str,
    ctf_address: str,
    operator: str,
    approved: bool = True,
    wait_for_receipt: bool = True,
) -> str:
    """Approve an operator to transfer all conditional tokens.

    This is required before selling positions. Uses ERC-1155 setApprovalForAll.

    Args:
        w3: Web3 instance connected to Base.
        private_key: Private key of the owner wallet.
        ctf_address: Address of the CTF contract.
        operator: Operator address (the venue exchange contract).
        approved: Whether to approve (True) or revoke (False).
        wait_for_receipt: Whether to wait for transaction confirmation.

    Returns:
        Transaction hash as hex string.

    Raises:
        Exception: If transaction fails.
    """
    private_key = format_private_key(private_key)
    account = Account.from_key(private_key)
    owner_address = account.address

    ctf = get_ctf_contract(w3, ctf_address)

    # Build transaction
    nonce = w3.eth.get_transaction_count(owner_address)
    gas_price = w3.eth.gas_price

    approve_tx = ctf.functions.setApprovalForAll(
        Web3.to_checksum_address(operator),
        approved,
    ).build_transaction(
        {
            "from": owner_address,
            "nonce": nonce,
            "gas": 100000,  # setApprovalForAll typically uses ~50k gas
            "gasPrice": gas_price,
            "chainId": BASE_CHAIN_ID,
        }
    )

    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(approve_tx, private_key)
    # Handle both old (rawTransaction) and new (raw_transaction) attribute names
    raw_tx = getattr(signed_tx, "raw_transaction", None) or signed_tx.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw_tx)

    if wait_for_receipt:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status != 1:
            raise Exception(f"CTF approval transaction failed: {tx_hash.hex()}")

    return tx_hash.hex()


def ensure_ctf_approved(
    w3: Web3,
    private_key: str,
    ctf_address: str,
    operator: str,
) -> dict:
    """Check CTF approval and approve if needed.

    Args:
        w3: Web3 instance connected to Base.
        private_key: Private key of the owner wallet.
        ctf_address: Address of the CTF contract.
        operator: Operator address (the venue exchange contract).

    Returns:
        Dict with:
            - already_approved: bool - True if approval was already granted
            - tx_hash: str | None - Transaction hash if approval was needed
    """
    private_key = format_private_key(private_key)
    account = Account.from_key(private_key)
    owner_address = account.address

    is_approved = check_ctf_approval(w3, ctf_address, owner_address, operator)

    if is_approved:
        return {
            "already_approved": True,
            "tx_hash": None,
        }

    # Need to approve
    tx_hash = approve_ctf(w3, private_key, ctf_address, operator)

    return {
        "already_approved": False,
        "tx_hash": tx_hash,
    }
