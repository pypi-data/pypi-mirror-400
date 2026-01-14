"""
Limitless Exchange Constants
Contract addresses, EIP-712 type definitions, and configuration
"""

from typing import Literal

# Wallet Types
WalletType = Literal["eoa", "smart_wallet"]

# API Configuration
API_BASE_URL = "https://api.limitless.exchange"
WEBSOCKET_URL = "wss://ws.limitless.exchange"

# Contract Addresses (Base Chain)
# DEPRECATED: These are legacy addresses. Use market.venue.exchange instead.
# Markets now have per-market venue exchange addresses returned from the API.
CLOB_ADDRESS = "0xa4409D988CA2218d956BeEFD3874100F444f0DC3"  # Deprecated
NEGRISK_ADDRESS = "0x5a38afc17F7E97ad8d6C547ddb837E40B4aEDfC6"  # Deprecated

# USDC Token (Base Chain)
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Gnosis Conditional Token Framework (Base Chain)
# Global ERC-1155 contract that holds all conditional tokens (YES/NO positions)
BASE_CTF_ADDRESS = "0xC9c98965297Bc527861c898329Ee280632B76e18"

# Multicall3 (same address on all EVM chains)
# Used to batch multiple contract calls into a single transaction
MULTICALL3_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

# Max uint256 for unlimited approval
MAX_UINT256 = 2**256 - 1

# EIP-4337 Account Abstraction
ENTRY_POINT_V06 = "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"
ENTRY_POINT_V07 = "0x0000000071727De22E5E9d8BAf0edAc6f37da032"
SAFE_4337_MODULE_V06 = "0xa581c4A4DB7175302464fF3C06380BC3270b4037"
SAFE_4337_MODULE_V07 = "0x75cf11467937ce3F2f357CE24ffc3DBF8fD5c226"
SAFE_4337_MODULE_V07_ERC7579 = "0x7579EE8307284F293B1927136486880611F20002"

# Paymaster
PAYMASTER_ADDRESS = "0x6666666666667849c56f2850848ce1c4da65c68b"
GAS_TOKEN = "0x2105"

# Chain Configuration
BASE_CHAIN_ID = 8453

# EIP-712 Type Definitions for Order Signing
ORDER_TYPES = {
    "Order": [
        {"name": "salt", "type": "uint256"},
        {"name": "maker", "type": "address"},
        {"name": "signer", "type": "address"},
        {"name": "taker", "type": "address"},
        {"name": "tokenId", "type": "uint256"},
        {"name": "makerAmount", "type": "uint256"},
        {"name": "takerAmount", "type": "uint256"},
        {"name": "expiration", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "feeRateBps", "type": "uint256"},
        {"name": "side", "type": "uint8"},
        {"name": "signatureType", "type": "uint8"},
    ]
}

# EIP-712 Types for Safe 4337 Operations
SAFE_OP_TYPES = {
    "EIP712Domain": [
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ],
    "SafeOp": [
        {"name": "safe", "type": "address"},
        {"name": "nonce", "type": "uint256"},
        {"name": "initCode", "type": "bytes"},
        {"name": "callData", "type": "bytes"},
        {"name": "callGasLimit", "type": "uint256"},
        {"name": "verificationGasLimit", "type": "uint256"},
        {"name": "preVerificationGas", "type": "uint256"},
        {"name": "maxFeePerGas", "type": "uint256"},
        {"name": "maxPriorityFeePerGas", "type": "uint256"},
        {"name": "paymasterAndData", "type": "bytes"},
        {"name": "validAfter", "type": "uint48"},
        {"name": "validUntil", "type": "uint48"},
        {"name": "entryPoint", "type": "address"},
    ],
}

# Market Category Mappings
CATEGORY_IDS = {
    2: "Crypto",
    5: "Other",
    19: "Company News",
    23: "Economy",
    29: "Hourly",
    30: "Daily",
    31: "Weekly",
    39: "中文预测专区",
    42: "Korean Market",
}

# Trade Sides
SIDE_BUY = 0
SIDE_SELL = 1

# Order Types
ORDER_TYPE_GTC = "GTC"  # Good Till Cancelled
ORDER_TYPE_FOK = "FOK"  # Fill Or Kill

# Market Types
MARKET_TYPE_CLOB = "CLOB"
MARKET_TYPE_NEGRISK = "NEGRISK"

# Signature Types
SIGNATURE_TYPE_EOA = 0
SIGNATURE_TYPE_EIP712 = 2

# Scaling
USDC_DECIMALS = 6
SCALING_FACTOR = 10**USDC_DECIMALS  # 1e6 for USDC

# Entry Point ABI (minimal for nonce retrieval)
ENTRY_POINT_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "uint192", "name": "key", "type": "uint192"},
        ],
        "name": "getNonce",
        "outputs": [
            {"internalType": "uint256", "name": "nonce", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

# ERC20 ABI (minimal for allowance and approve)
ERC20_ABI = [
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# ERC1155 ABI (minimal for setApprovalForAll and isApprovedForAll)
# Used for conditional token (CTF) approval when selling positions
ERC1155_ABI = [
    {
        "inputs": [
            {"name": "operator", "type": "address"},
            {"name": "approved", "type": "bool"},
        ],
        "name": "setApprovalForAll",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "account", "type": "address"},
            {"name": "operator", "type": "address"},
        ],
        "name": "isApprovedForAll",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "account", "type": "address"},
            {"name": "id", "type": "uint256"},
        ],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Conditional Token Framework (CTF) ABI - for position redemption
# Gnosis CTF contract on Base: 0xC9c98965297Bc527861c898329Ee280632B76e18
CTF_ABI = [
    # redeemPositions - claim winnings from resolved markets
    {
        "inputs": [
            {"name": "collateralToken", "type": "address"},
            {"name": "parentCollectionId", "type": "bytes32"},
            {"name": "conditionId", "type": "bytes32"},
            {"name": "indexSets", "type": "uint256[]"},
        ],
        "name": "redeemPositions",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    # balanceOf - check position balance
    {
        "inputs": [
            {"name": "account", "type": "address"},
            {"name": "id", "type": "uint256"},
        ],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Multicall3 ABI - for batching multiple contract calls
# https://github.com/mds1/multicall
MULTICALL3_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "target", "type": "address"},
                    {"name": "allowFailure", "type": "bool"},
                    {"name": "callData", "type": "bytes"},
                ],
                "name": "calls",
                "type": "tuple[]",
            }
        ],
        "name": "aggregate3",
        "outputs": [
            {
                "components": [
                    {"name": "success", "type": "bool"},
                    {"name": "returnData", "type": "bytes"},
                ],
                "name": "returnData",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "payable",
        "type": "function",
    },
]
