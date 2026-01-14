# py-limitless

A Python SDK for trading on [Limitless Exchange](https://limitless.exchange) — a prediction market on Base.

## Features

- **Authentication** — Sign in with your Ethereum wallet (EOA or Smart Wallet)
- **Trading** — Place buy/sell orders (GTC and FOK), cancel orders, view orderbook
- **Real-time data** — WebSocket subscriptions for price updates and orderbook changes
- **Portfolio management** — View positions, open orders, and P&L
- **Position redemption** — Claim winnings from resolved markets
- **Token approvals** — Approve USDC and conditional tokens for trading

## Installation

```bash
pip install py-limitless
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add py-limitless
```

## Quick Start

### EOA Mode (Simple)

Use your Ethereum wallet's private key directly:

```python
from limitless_sdk import Limitless

# Initialize client
client = Limitless(private_key="0x...")
client.authenticate()

# Place a buy order: 10 shares of YES at 65¢
result = client.buy(
    market_slug="btc-above-100k-by-jan",
    token_id="123456789...",  # YES token ID from market data
    price_cents=65,
    amount=10
)

print(f"Order placed: {result['order']['id']}")
```

### Smart Wallet Mode

For accounts using Limitless's embedded smart wallet:

```python
from limitless_sdk import Limitless

client = Limitless(
    private_key="0x...",        # Auth key (your EOA)
    signing_wallet_pk="0x...",  # Signing key (embedded account)
    wallet_type="smart_wallet"
)
client.authenticate()

# Trading works the same way
client.buy(market_slug="...", token_id="...", price_cents=50, amount=5)
```

## Core Concepts

### Market Data

Every market has a `slug` (URL identifier) and two tokens: YES and NO. Get market details:

```python
market = client.get_market("btc-above-100k-by-jan")

yes_token_id = market["tokens"]["yes"]
no_token_id = market["tokens"]["no"]
prices = market["prices"]  # [yes_price, no_price]
```

### Order Types

- **GTC (Good Till Cancelled)** — Limit order that stays open until filled or cancelled
- **FOK (Fill Or Kill)** — Market order that fills immediately or fails

```python
# Limit order at specific price
client.buy(market_slug="...", token_id="...", price_cents=65, amount=10, order_type="GTC")

# Market order - fills at best available price
client.buy(market_slug="...", token_id="...", price_cents=70, amount=10, order_type="FOK")
```

### Token Approvals

Before trading, you need to approve the exchange to spend your tokens:

```python
# For buying: approve USDC
client.ensure_usdc_approved_for_market("btc-above-100k-by-jan")

# For selling: approve conditional tokens (YES/NO positions)
client.ensure_ctf_approved_for_market("btc-above-100k-by-jan")
```

## API Reference

### Limitless Client

The main client for interacting with Limitless Exchange.

#### Constructor

```python
Limitless(
    private_key: str,                    # Your wallet's private key
    signing_wallet_pk: str = None,       # Signing key (smart_wallet mode only)
    wallet_type: str = "eoa",            # "eoa" or "smart_wallet"
    api_base_url: str = "https://api.limitless.exchange",
    referral_code: str = None            # Optional referral code
)
```

#### Authentication

```python
client.authenticate()  # Returns user data dict
client.is_authenticated  # bool
client.address  # Your wallet address
client.smart_wallet  # Smart wallet address (after auth)
```

#### Trading

```python
# Place orders
client.buy(market_slug, token_id, price_cents, amount, order_type="GTC")
client.sell(market_slug, token_id, price_cents, amount, order_type="GTC")

# Cancel orders
client.cancel_order(order_id)
client.cancel_all_orders(market_slug)
client.cancel_all_user_orders()  # Cancel across all markets

# View orders
client.get_user_orders(market_slug)
```

#### Market Data

```python
client.get_market(market_slug)           # Market details
client.get_orderbook(market_slug)        # Current orderbook
client.get_active_markets(category_id)   # Browse markets by category
client.get_categories()                  # List all categories
```

#### Portfolio

```python
client.get_portfolio_positions()         # All positions
client.get_usdc_balance()                # USDC balance
```

#### Position Redemption

Claim winnings from resolved markets:

```python
# Get redeemable positions
redeemable = client.get_redeemable_positions()
for pos in redeemable:
    print(f"{pos.market_title}: ${pos.balance}")

# Redeem a single position
result = client.redeem_position(condition_id="0x...")

# Redeem all winning positions
results = client.redeem_all_positions()
```

#### Token Approvals

```python
# USDC (for buying)
client.check_usdc_allowance_for_market(market_slug)
client.approve_usdc_for_market(market_slug)
client.ensure_usdc_approved_for_market(market_slug)

# CTF/Conditional Tokens (for selling)
client.check_ctf_approval_for_market(market_slug)
client.approve_ctf_for_market(market_slug)
client.ensure_ctf_approved_for_market(market_slug)
```

### WebSocket Client

Real-time market data via Socket.IO:

```python
import asyncio
from limitless_sdk import LimitlessWebSocket

async def main():
    ws = LimitlessWebSocket(auth_private_key="0x...")
    await ws.connect()

    # Register event handlers
    ws.on("price", lambda data: print(f"Price update: {data}"))
    ws.on("orderbook", lambda data: print(f"Orderbook: {data}"))

    # Subscribe to markets
    await ws.subscribe_markets(market_slugs=["btc-above-100k-by-jan"])

    # Keep connection alive
    await ws.wait()

asyncio.run(main())
```

#### Events

- `price` — Price updates for subscribed markets
- `orderbook` — Orderbook changes (CLOB markets)
- `positions` — Position updates (requires authentication)
- `system` — System messages
- `exception` — Error messages

### Constants

```python
from limitless_sdk import (
    # Trade sides
    SIDE_BUY,           # 0
    SIDE_SELL,          # 1

    # Order types
    ORDER_TYPE_GTC,     # "GTC"
    ORDER_TYPE_FOK,     # "FOK"

    # Market categories
    CATEGORY_IDS,       # {2: "Crypto", 5: "Other", ...}

    # Contract addresses (Base chain)
    USDC_ADDRESS,
    BASE_CTF_ADDRESS,
)
```

### Utility Functions

```python
from limitless_sdk import (
    scale_amount,       # Convert to 6-decimal USDC units
    unscale_amount,     # Convert from 6-decimal units
    cents_to_dollars,   # 65 → 0.65
    dollars_to_cents,   # 0.65 → 65
)
```

## Configuration

### Environment Variables

```bash
# Your wallet's private key
PRIVATE_KEY=0x...

# Optional: Custom RPC URL (defaults to https://mainnet.base.org)
BASE_RPC_URL=https://your-rpc-url.com
```

### Custom RPC

Pass a custom RPC URL for blockchain operations:

```python
client.get_usdc_balance(rpc_url="https://your-rpc.com")
client.approve_usdc_for_market(market_slug, rpc_url="https://your-rpc.com")
client.redeem_position(condition_id, rpc_url="https://your-rpc.com")
```

## Examples

### Market Making Bot

```python
from limitless_sdk import Limitless

client = Limitless(private_key="0x...")
client.authenticate()

market_slug = "btc-above-100k-by-jan"
market = client.get_market(market_slug)

# Ensure approvals
client.ensure_usdc_approved_for_market(market_slug)
client.ensure_ctf_approved_for_market(market_slug)

# Place bid and ask
yes_token = market["tokens"]["yes"]
client.buy(market_slug, yes_token, price_cents=48, amount=100)   # Bid
client.sell(market_slug, yes_token, price_cents=52, amount=100)  # Ask
```

### Portfolio Monitor

```python
from limitless_sdk import Limitless

client = Limitless(private_key="0x...")
client.authenticate()

portfolio = client.get_portfolio_positions()

for position in portfolio.get("clob", []):
    market = position["market"]
    print(f"{market['title']}")
    print(f"  Value: ${position.get('value', 0):.2f}")
    print(f"  P&L: ${position.get('pnl', 0):.2f}")
```

### Claim All Winnings

```python
from limitless_sdk import Limitless

client = Limitless(private_key="0x...")
client.authenticate()

redeemable = client.get_redeemable_positions()
if redeemable:
    print(f"Found {len(redeemable)} positions to redeem")
    results = client.redeem_all_positions()

    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"{status} {r['market_title']}: ${r['balance']}")
```

## Requirements

- Python 3.10+
- An Ethereum wallet with Base ETH for gas (redemptions only)
- USDC on Base for trading

## Links

- [Limitless Exchange](https://limitless.exchange)
- [API Documentation](https://api.limitless.exchange/api-v1)
- [GitHub Repository](https://github.com/ego-errante/limitless-sdk)

## License

MIT
