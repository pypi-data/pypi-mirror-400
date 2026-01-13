# Forkast Python SDK

A Python SDK for interacting with the **Forkast** trading platform

---

## ✨ Features

- 🔐 Gnosis Safe (Proxy Wallet) approval via MultiSend
- 📝 Place / cancel orders (EIP-712 signed)
- 📊 Fetch balances, markets, orders
- 🌐 Network-aware (Testnet / Mainnet)
- 🧪 Integration tests

---

## 🚧 Requirements

- Python >= 3.12
- pip

---

## 📦 Installation

```bash
pip install forkast-py-client
```

---

## 🌀 Running

⚠️ Examples require Python ≥ 3.12 and a virtual environment. You can see the full quickstart example below at [`examples/example.py`](examples/example.py). Run examples with:

```python
python3 examples/example.py
```

---

## 🚀 Quick Start

### 1️⃣ Initialize SDK

```python
import asyncio
from eth_account import Account
from forkast_py_client import ForkastSDK, MarketOutcome, Network, load_abi, create_provider_without_signer

# Initialize SDK
sdk = ForkastSDK(
    network=Network.TESTNET,   # or Network.MAINNET
    api_key="YOUR_API_KEY"
)
```

### 2️⃣ Login using private key

```python
account_service = sdk.get_account_service()

# Login using private key
private_key = "YOUR_PRIVATE_KEY"
login = account_service.login_with_private_key(private_key)
access_token = login.access_token
print("access token: ", access_token)
```

### 3️⃣ Fetch user profile

```python
user = account_service.get_user(access_token)
print("User: ", user)
```

### 4️⃣ Fetch balances

```python
balances_service = sdk.get_balances_service()

balances = balances_service.get_balances(access_token)
print("Balances: ", balances)
```

### 5️⃣ Fetch event data

```python
market_service = sdk.get_market_service()
event_id = 67 # Replace with a valid event id
event_data = market_service.get_event_data(event_id)
print("Event data: ", event_data)
```

### 6️⃣ Choose a market and get its details

```python
market_id = event_data.markets[0].id
outcome_id = event_data.markets[0].outcomes[0].id
outcome_token_id = event_data.markets[0].outcomes[0].token_id
outcome_type = event_data.markets[0].outcomes[0].outcome_type
order_book = market_service.get_order_book(market_id, outcome_id, outcome_type)
print("Market ID: ", market_id)
print("Outcome ID: ", outcome_id)
print("Outcome Token ID: ", outcome_token_id)
print("Outcome Type: ", outcome_type)
print("Orderbook: ", order_book)
```

### 7️⃣ Get token prices

```python
token_prices = market_service.get_token_prices(market_id, 0) # 0 = BUY, 1 = SELL
print("Token prices: ", token_prices)
```

### 8️⃣ Approve if needed
Required once before placing orders.

```python
signer = Account.from_key(private_key)
provider = create_provider_without_signer(sdk._network)
proxy_wallet = "YOUR_PROXY_WALLET_ADDRESS"
gnosis_safe_abi = load_abi("GnosisSafe.abi.json")
multi_send = "MULTI_SEND_CONTRACT_ADDRESS"
chain_id = 421614 # Replace with correct chain id
result = await account_service.approve_max_platform_credits_for_proxy_wallet(
    signer=signer,
    wallet_proxy_address=proxy_wallet,
    buy_amount=10000000,
)
print("approve_max_platform_credits_for_proxy_wallet_success response: ", result)
```

Send transaction if approval is required
```python
if result is not None:
    gnosis_safe = provider.eth.contract(
        address=proxy_wallet,
        abi=gnosis_safe_abi,
    )
    tx = gnosis_safe.functions.execTransaction(
        provider.to_checksum_address(multi_send),
        0,  # value
        bytes.fromhex(result.data_sign["data"][2:]),
        1,  # DELEGATE_CALL
        0,
        0,
        0,
        "0x0000000000000000000000000000000000000000",
        "0x0000000000000000000000000000000000000000",
        bytes.fromhex(result.signature[2:]),
    ).build_transaction(
        {
            "from": signer.address,
            "nonce": provider.eth.get_transaction_count(signer.address),
            "gas": 500_000,
            "chainId": chain_id,
        }
    )
    print("Built tx: ", tx)

    signed_tx = signer.sign_transaction(tx) # The signer address will be the one sending tx, so we need to ensure signer has enough gas
    tx_hash = provider.eth.send_raw_transaction(signed_tx.rawTransaction)
    provider.eth.wait_for_transaction_receipt(tx_hash)
    print("Tx Hash: ", tx_hash.hex())
```
⚠️ The signer address must have enough native gas.

### 9️⃣ Place an order

```python
order_service = sdk.get_order_service()
market_outcome = MarketOutcome(
    id=outcome_id,  # outcome id
    token_id=outcome_token_id,  # outcome token id
    outcome_type=outcome_type,  # 0 = No, 1 = Yes
)
resp = order_service.place_single_order(
    event_id=event_id,
    market_id=market_id,
    token=market_outcome,
    account={
        "wallet": signer.address,
        "private_key": private_key,
        "proxy_wallet": proxy_wallet,
    },
    price=0.6, # the price you want to place your order
    amount=96, # the amount you want to buy/sell
    side=1,  # the side of your order: 0 = BUY, 1 = SELL
    access_token=access_token,
)
print("place_single_order response:", resp)
order_id_placed = resp.order_result["data"]["id"]
print("Order ID placed: ", order_id_placed)
```

### 🔟 Get all orders

```python
resp = order_service.get_all_orders(
    address=proxy_wallet,
    outcome_id=outcome_id,
    access_token=access_token,
    limit=10,
    page=1,
)
print("get_all_orders response:", resp)
```

### 🟡 Cancel order

```python
resp = order_service.cancel_order(
    order_id=order_id_placed,
    access_token=access_token,
)
print("cancel_order response:", resp)
```

