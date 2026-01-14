"""
Limitless Exchange Position Redemption

Supports two modes:
- EOA: Direct on-chain redemption (user pays gas)
- Smart Wallet: EIP-4337 Account Abstraction with gasless transactions
"""

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import requests
from eth_abi import encode
from eth_account import Account
from eth_utils import keccak
from web3 import Web3

# Import with version compatibility
try:
    from eth_account.messages import encode_typed_data
except ImportError:
    from eth_account.messages import encode_structured_data as encode_typed_data

from .constants import (
    BASE_CHAIN_ID,
    BASE_CTF_ADDRESS,
    CTF_ABI,
    ENTRY_POINT_ABI,
    ENTRY_POINT_V06,
    GAS_TOKEN,
    SAFE_4337_MODULE_V06,
    SAFE_OP_TYPES,
    USDC_ADDRESS,
    USDC_DECIMALS,
)
from .utils import format_private_key

# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class RedeemablePosition:
    """A position that can be redeemed from a resolved market."""

    condition_id: str
    market_slug: str
    market_title: str
    winning_token: str  # "YES" or "NO"
    balance: Decimal  # Number of winning tokens (USDC value)


# =============================================================================
# Helper Functions
# =============================================================================


def get_redeemable_positions(portfolio_data: dict) -> list[RedeemablePosition]:
    """
    Extract redeemable positions from portfolio API response.

    Args:
        portfolio_data: Response from client.get_portfolio_positions()

    Returns:
        List of RedeemablePosition objects for resolved markets with winning tokens

    Example:
        ```python
        portfolio = client.get_portfolio_positions()
        redeemable = get_redeemable_positions(portfolio)
        for pos in redeemable:
            print(f"{pos.market_title}: {pos.balance} {pos.winning_token}")
        ```
    """
    redeemable = []

    for market_data in portfolio_data.get("clob", []):
        market = market_data.get("market", {})

        # Only process resolved markets
        if market.get("status") != "RESOLVED":
            continue

        condition_id = market.get("conditionId")
        winning_index = market.get("winningOutcomeIndex")

        if condition_id is None or winning_index is None:
            continue

        # Determine winning token type (0 = YES, 1 = NO)
        winning_token = "YES" if winning_index == 0 else "NO"
        token_key = winning_token.lower()

        # Check if user has winning tokens
        tokens_balance = market_data.get("tokensBalance", {})
        raw_balance = int(tokens_balance.get(token_key, 0) or 0)

        if raw_balance <= 0:
            continue

        # Scale balance from raw units (6 decimals for USDC)
        balance = Decimal(str(raw_balance)) / Decimal(str(10**USDC_DECIMALS))

        redeemable.append(
            RedeemablePosition(
                condition_id=condition_id,
                market_slug=market.get("slug", ""),
                market_title=market.get("title", ""),
                winning_token=winning_token,
                balance=balance,
            )
        )

    return redeemable


# =============================================================================
# EOA Position Redeemer
# =============================================================================


class EOAPositionRedeemer:
    """
    Handles direct on-chain position redemption for EOA wallets.

    Unlike the smart wallet redeemer, this requires the user to pay gas
    in ETH for the transaction.

    Example:
        ```python
        redeemer = EOAPositionRedeemer(
            private_key="0x...",
            rpc_url="https://mainnet.base.org"
        )
        tx_hash = redeemer.redeem_position(condition_id="0x...")
        receipt = redeemer.wait_for_receipt(tx_hash)
        ```
    """

    def __init__(
        self,
        private_key: str,
        rpc_url: str = "https://mainnet.base.org",
        ctf_address: str = BASE_CTF_ADDRESS,
        collateral_token: str = USDC_ADDRESS,
        chain_id: int = BASE_CHAIN_ID,
    ):
        """
        Initialize the EOA position redeemer.

        Args:
            private_key: EOA private key for signing transactions
            rpc_url: Base chain RPC URL
            ctf_address: Conditional Token Framework contract address
            collateral_token: Collateral token address (USDC)
            chain_id: Chain ID (8453 for Base)
        """
        self.private_key = format_private_key(private_key)
        self.ctf_address = Web3.to_checksum_address(ctf_address)
        self.collateral_token = Web3.to_checksum_address(collateral_token)
        self.chain_id = chain_id

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address

        self.ctf_contract = self.w3.eth.contract(address=self.ctf_address, abi=CTF_ABI)

        # Track last used nonce to detect RPC sync delays
        self._last_used_nonce: int | None = None

    def _get_next_nonce(self, max_retries: int = 10, delay_ms: int = 200) -> int:
        """
        Get the next nonce, waiting for RPC to sync if needed.

        If the fetched nonce equals the last used nonce, the RPC hasn't
        synced yet. Wait and retry until we get a fresh nonce.
        """
        import time

        for attempt in range(max_retries):
            nonce = self.w3.eth.get_transaction_count(self.address, "pending")

            # First call or nonce has incremented - good to go
            if self._last_used_nonce is None or nonce > self._last_used_nonce:
                return nonce

            # Nonce hasn't incremented yet, RPC is stale - wait and retry
            time.sleep(delay_ms / 1000)

        # After max retries, force increment to avoid infinite loop
        return self._last_used_nonce + 1

    def redeem_position(
        self,
        condition_id: str,
        gas_limit: int = 150000,
        max_priority_fee_gwei: float = 0.01,
    ) -> str:
        """
        Redeem a resolved position by calling CTF.redeemPositions().

        Args:
            condition_id: Condition ID of the resolved market (32 bytes hex)
            gas_limit: Gas limit for the transaction
            max_priority_fee_gwei: Max priority fee in gwei

        Returns:
            Transaction hash

        Raises:
            ValueError: If condition_id is invalid
            Exception: If transaction fails
        """
        # Validate and format condition_id
        cid = condition_id.lower().replace("0x", "")
        if len(cid) != 64:
            raise ValueError("Condition ID must be 32 bytes (64 hex chars)")
        condition_id_bytes = bytes.fromhex(cid)

        # Parent collection ID is all zeros for root conditions
        parent_collection_id = bytes(32)

        # Index sets: 1 = YES (2^0), 2 = NO (2^1) - redeem both
        index_sets = [1, 2]

        # Fetch nonce, waiting for RPC to sync if needed
        nonce = self._get_next_nonce()

        # Get gas prices
        base_fee = self.w3.eth.get_block("latest")["baseFeePerGas"]
        max_priority_fee = self.w3.to_wei(max_priority_fee_gwei, "gwei")
        max_fee = base_fee * 2 + max_priority_fee

        tx = self.ctf_contract.functions.redeemPositions(
            self.collateral_token,
            parent_collection_id,
            condition_id_bytes,
            index_sets,
        ).build_transaction(
            {
                "from": self.address,
                "nonce": nonce,
                "gas": gas_limit,
                "maxFeePerGas": max_fee,
                "maxPriorityFeePerGas": max_priority_fee,
                "chainId": self.chain_id,
            }
        )

        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)

        # Handle both old (rawTransaction) and new (raw_transaction) attribute names
        raw_tx = getattr(signed_tx, "raw_transaction", None) or signed_tx.rawTransaction
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)

        # Track nonce after successful send (caller should wait_for_receipt before next call)
        self._last_used_nonce = nonce

        return tx_hash.hex()

    def wait_for_receipt(self, tx_hash: str, timeout: int = 120) -> dict:
        """
        Wait for transaction receipt.

        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds

        Returns:
            Transaction receipt

        Raises:
            TimeoutError: If transaction not mined within timeout
        """
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return dict(receipt)

    def estimate_gas(self, condition_id: str) -> int:
        """
        Estimate gas for redemption transaction.

        Args:
            condition_id: Condition ID of the resolved market

        Returns:
            Estimated gas units
        """
        cid = condition_id.lower().replace("0x", "")
        condition_id_bytes = bytes.fromhex(cid)
        parent_collection_id = bytes(32)
        index_sets = [1, 2]

        return self.ctf_contract.functions.redeemPositions(
            self.collateral_token,
            parent_collection_id,
            condition_id_bytes,
            index_sets,
        ).estimate_gas({"from": self.address})

    def get_eth_balance(self) -> Decimal:
        """Get ETH balance for gas estimation display."""
        balance_wei = self.w3.eth.get_balance(self.address)
        return Decimal(str(balance_wei)) / Decimal("1e18")


# Dummy signature for gas estimation
DUMMY_SIGNATURE = (
    "0x000000000000000000000000fffffffffffffffffffffffffffffff0"
    "000000000000000000000000000000007aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1c"
)


class PositionRedeemer:
    """
    Handles EIP-4337 UserOperation flow for redeeming positions.

    Supports claiming resolved market positions via Pimlico paymaster,
    enabling gasless transactions.

    Example:
        ```python
        redeemer = PositionRedeemer(
            private_key="0x...",
            smart_wallet="0x...",
            pimlico_api_key="pim_..."
        )
        result = redeemer.redeem_position(condition_id="0x...")
        ```
    """

    def __init__(
        self,
        private_key: str,
        smart_wallet: str,
        pimlico_api_key: str,
        rpc_url: str = "https://base-mainnet.infura.io/v3/9aadf67222e842aba70a6238829e66cc",
        entry_point: str = ENTRY_POINT_V06,
        safe_module: str = SAFE_4337_MODULE_V06,
        chain_id: int = BASE_CHAIN_ID,
    ):
        """
        Initialize the position redeemer.

        Args:
            private_key: Private key for signing UserOperations
            smart_wallet: Smart wallet address (sender)
            pimlico_api_key: Pimlico API key for bundler/paymaster
            rpc_url: Base chain RPC URL
            entry_point: EntryPoint contract address
            safe_module: Safe 4337 module address
            chain_id: Chain ID (8453 for Base)
        """
        self.private_key = format_private_key(private_key)
        self.smart_wallet = smart_wallet
        self.pimlico_api_key = pimlico_api_key
        self.entry_point = entry_point
        self.safe_module = safe_module
        self.chain_id = chain_id

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.bundler_url = f"https://api.pimlico.io/v2/{chain_id}/rpc?apikey={pimlico_api_key}"

        self.entry_point_contract = self.w3.eth.contract(address=entry_point, abi=ENTRY_POINT_ABI)

    def _rpc_call(self, method: str, params: list, id_: int = 1) -> dict:
        """Make a JSON-RPC call to the bundler."""
        payload = {
            "jsonrpc": "2.0",
            "id": id_,
            "method": method,
            "params": params,
        }
        resp = requests.post(self.bundler_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"RPC error in {method}: {data['error']}")
        return data["result"]

    def _get_nonce(self) -> str:
        """Get current nonce for the smart wallet."""
        nonce_key = int(time.time() * 1000)
        nonce_int = self.entry_point_contract.functions.getNonce(
            self.smart_wallet, nonce_key
        ).call()
        return hex(nonce_int)

    def _make_call_data(self, condition_id: str) -> str:
        """
        Build callData for redeeming a position.

        Args:
            condition_id: Condition ID of the resolved market (32 bytes hex)

        Returns:
            Encoded callData for the redemption transaction
        """
        cid = condition_id.lower().replace("0x", "")
        if len(cid) != 64:
            raise ValueError("Condition ID must be 32 bytes (64 hex chars)")

        # Static parts of the callData template
        prefix = (
            "0x541d63c8000000000000000000000000c9c98965297bc527861c898329ee280632b76e18"
            "0000000000000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000080"
            "0000000000000000000000000000000000000000000000000000000000000000"
            "00000000000000000000000000000000000000000000000000000000000000e4"
            "01b7037c000000000000000000000000833589fcd6edb6e08f4c7c32d4f71b54bda02913"
            "0000000000000000000000000000000000000000000000000000000000000000"
        )

        suffix = (
            "0000000000000000000000000000000000000000000000000000000000000080"
            "0000000000000000000000000000000000000000000000000000000000000002"
            "0000000000000000000000000000000000000000000000000000000000000001"
            "0000000000000000000000000000000000000000000000000000000000000002"
            "0000000000000000000000000000000000000000000000000000000000000000"
        )

        return prefix + cid + suffix

    def _build_user_op(
        self,
        condition_id: str,
        max_fee_per_gas: str,
        max_priority_fee_per_gas: str,
    ) -> dict:
        """Build base UserOperation."""
        return {
            "callData": self._make_call_data(condition_id),
            "callGasLimit": "0x0",
            "initCode": "0x",
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "nonce": self._get_nonce(),
            "paymasterAndData": "0x",
            "preVerificationGas": "0x0",
            "sender": self.smart_wallet,
            "signature": DUMMY_SIGNATURE,
            "verificationGasLimit": "0x0",
        }

    def _sign_user_op(self, user_op: dict) -> str:
        """
        Generate EIP-712 signature for Safe 4337 account.

        Format: validAfter(6) + validUntil(6) + r(32) + s(32) + v(1)
        """
        valid_after = 0
        valid_until = 0

        # EIP-712 domain for Safe module
        domain = {"chainId": self.chain_id, "verifyingContract": self.safe_module}

        # Message to sign
        message = {
            "safe": user_op["sender"],
            "nonce": int(user_op["nonce"], 16),
            "initCode": bytes.fromhex(user_op["initCode"][2:])
            if user_op["initCode"] != "0x"
            else b"",
            "callData": bytes.fromhex(user_op["callData"][2:]),
            "callGasLimit": int(user_op["callGasLimit"], 16),
            "verificationGasLimit": int(user_op["verificationGasLimit"], 16),
            "preVerificationGas": int(user_op["preVerificationGas"], 16),
            "maxFeePerGas": int(user_op["maxFeePerGas"], 16),
            "maxPriorityFeePerGas": int(user_op["maxPriorityFeePerGas"], 16),
            "paymasterAndData": bytes.fromhex(user_op["paymasterAndData"][2:])
            if user_op["paymasterAndData"] != "0x"
            else b"",
            "validAfter": valid_after,
            "validUntil": valid_until,
            "entryPoint": self.entry_point,
        }

        # Create EIP-712 structured data
        structured_data = {
            "types": SAFE_OP_TYPES,
            "primaryType": "SafeOp",
            "domain": domain,
            "message": message,
        }

        # Sign
        account = Account.from_key(self.private_key)
        signable_message = encode_typed_data(full_message=structured_data)
        signature = account.sign_message(signable_message)

        # Pack: validAfter(6) + validUntil(6) + r(32) + s(32) + v(1)
        packed_sig = (
            valid_after.to_bytes(6, "big")
            + valid_until.to_bytes(6, "big")
            + signature.r.to_bytes(32, "big")
            + signature.s.to_bytes(32, "big")
            + signature.v.to_bytes(1, "big")
        )

        return "0x" + packed_sig.hex()

    def redeem_position(
        self,
        condition_id: str,
        gas_token: str = GAS_TOKEN,
    ) -> str:
        """
        Redeem a resolved position using EIP-4337 UserOperation.

        Args:
            condition_id: Condition ID of the resolved market
            gas_token: Gas token for paymaster (default: native token)

        Returns:
            UserOperation hash

        Raises:
            RuntimeError: If any step in the flow fails
        """
        # 1. Get gas prices
        gas_prices = self._rpc_call("pimlico_getUserOperationGasPrice", [])
        fast = gas_prices["fast"]
        max_fee = fast["maxFeePerGas"]
        max_priority = fast["maxPriorityFeePerGas"]

        # 2. Build base UserOp
        user_op = self._build_user_op(condition_id, max_fee, max_priority)

        # 3. Get paymaster stub data
        stub_result = self._rpc_call(
            "pm_getPaymasterStubData", [user_op, self.entry_point, gas_token, None]
        )
        user_op["paymasterAndData"] = stub_result["paymasterAndData"]

        # 4. Estimate gas
        gas_estimate = self._rpc_call("eth_estimateUserOperationGas", [user_op, self.entry_point])
        user_op["callGasLimit"] = gas_estimate["callGasLimit"]
        user_op["verificationGasLimit"] = gas_estimate["verificationGasLimit"]
        user_op["preVerificationGas"] = gas_estimate["preVerificationGas"]

        # 5. Get final paymaster data
        paymaster_result = self._rpc_call(
            "pm_getPaymasterData", [user_op, self.entry_point, gas_token, None]
        )
        user_op["paymasterAndData"] = paymaster_result["paymasterAndData"]

        # 6. Sign the UserOp
        user_op["signature"] = self._sign_user_op(user_op)

        # 7. Send UserOperation
        result = self._rpc_call("eth_sendUserOperation", [user_op, self.entry_point])

        return result

    def get_user_op_receipt(self, user_op_hash: str) -> Optional[dict]:
        """
        Get receipt for a UserOperation.

        Args:
            user_op_hash: UserOperation hash from redeem_position

        Returns:
            Receipt dict or None if not found/pending
        """
        try:
            return self._rpc_call("eth_getUserOperationReceipt", [user_op_hash])
        except RuntimeError:
            return None
