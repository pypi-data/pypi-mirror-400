from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

# Max value of uint256 for token approval
MAX_UINT256 = 2**256 - 1
# Max amount of PC to buy
MAX_BUY_AMOUNT = 10_000_000


# Network types for the SDK
class Network(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"


# RPC URLs for different networks
RPC_URLS = {
    Network.MAINNET: "https://arb1.arbitrum.io/rpc",
    Network.TESTNET: "https://api.zan.top/arb-sepolia",
}

# API endpoints for the SDK
ENDPOINTS = {
    Network.MAINNET: {
        "PLACE_ORDER": "https://mgapi.forkast.gg/api/v1/order/place/v2",
        "EVENT": "https://mgapi.forkast.gg/api/v1/markets/get-by-slug",
        "LOGIN": "https://mgapi.forkast.gg/api/v1/auth",
        "CLAIM_CREDIT": "https://mgapi.forkast.gg/api/v1/credit/claim",
        "BALANCE": "https://mgapi.forkast.gg/api/v1/balance",
        "USER_PROFILE": "https://mgapi.forkast.gg/api/v1/user/profile",
        "ORDERBOOK": "https://mgapi.forkast.gg/api/v1/orderbook",
        "TOKEN_PRICE": "https://mgapi.forkast.gg/api/v1/token-price",
        "GET_ORDER": "https://mgapi.forkast.gg/api/v1/order",
        "CANCEL_ORDER": "https://mgapi.forkast.gg/api/v1/order/cancel-order",
        "ADD_ORDER": "https://mgapi.forkast.gg/api/v1/order/place/v2",
    },
    Network.TESTNET: {
        "PLACE_ORDER": "https://api.sit.forkast.gg/api/v1/order/place/v2",
        "EVENT": "https://api.sit.forkast.gg/api/v1/markets/get-by-slug",
        "LOGIN": "https://api.sit.forkast.gg/api/v1/auth",
        "CLAIM_CREDIT": "https://api.sit.forkast.gg/api/v1/credit/claim",
        "BALANCE": "https://api.sit.forkast.gg/api/v1/balance",
        "USER_PROFILE": "https://api.sit.forkast.gg/api/v1/user/profile",
        "ORDERBOOK": "https://api.sit.forkast.gg/api/v1/orderbook",
        "TOKEN_PRICE": "https://api.sit.forkast.gg/api/v1/token-price",
        "GET_ORDER": "https://api.sit.forkast.gg/api/v1/order",
        "CANCEL_ORDER": "https://api.sit.forkast.gg/api/v1/order/cancel-order",
        "ADD_ORDER": "https://api.sit.forkast.gg/api/v1/order/place/v2",
    },
}

# Token addresses for different networks
TOKEN_ADDRESSES = {
    Network.MAINNET: {
        "PC_TOKEN": "0x4AC7b973fb4f10D94eda5Efa92fFABD6aDDFb65c",
        "GNOSIS_SAFE_PROXY_FACTORY": "0x5c8789b886ADa0fF89Defebe27AAF954984350BF",
        "CTF_EXCHANGE": "0x2D7aa09fe8a9Af205aD6E0Fef1441834c4250cdc",
        "CONDITIONAL_TOKENS": "0x49598aae06f8ed6D82Cb9DFa503e731221fBf7E6",
        "MULTI_SEND": "0x0D2Bea44d8E9AE2ac6b9419431dea3e48aBF00BD",
    },
    Network.TESTNET: {
        "PC_TOKEN": "0x9C94076DE90c387940DB2eB2264A95d8E51daB03",
        "GNOSIS_SAFE_PROXY_FACTORY": "0x75328f565Cd68C42FEE9350D7045791273cdC20F",
        "CTF_EXCHANGE": "0x0a9F05f3d1192128E35cdB599Bd318C3c1E888A4",
        "CONDITIONAL_TOKENS": "0xa9501A8cbD50127F0aE4F413f25257ea58dfa751",
        "MULTI_SEND": "0xd80d6e760eaa49E5C0C85f55005eE0D270D10dE4",
    },
}

# Configuration for active proxy
PREPARE_ACTIVE_PROXY = {
    Network.MAINNET: {
        "PUBLIC_MESSAGE_SIGN": "Welcome to Forkast!",
        "GNOSIS_SAFE_PROXY_FACTORY": TOKEN_ADDRESSES[Network.MAINNET][
            "GNOSIS_SAFE_PROXY_FACTORY"
        ],
        "CHAIN_ID": 42161,
    },
    Network.TESTNET: {
        "PUBLIC_MESSAGE_SIGN": "Welcome to Forkast!",
        "GNOSIS_SAFE_PROXY_FACTORY": TOKEN_ADDRESSES[Network.TESTNET][
            "GNOSIS_SAFE_PROXY_FACTORY"
        ],
        "CHAIN_ID": 421614,
    },
}

# Configuration for token approval
PREPARE_APPROVE_TOKEN = {
    Network.MAINNET: {
        "PC_TOKEN": TOKEN_ADDRESSES[Network.MAINNET]["PC_TOKEN"],
        "CTF_EXCHANGE": TOKEN_ADDRESSES[Network.MAINNET]["CTF_EXCHANGE"],
        "CONDITIONAL_TOKENS": TOKEN_ADDRESSES[Network.MAINNET]["CONDITIONAL_TOKENS"],
        "MULTI_SEND": TOKEN_ADDRESSES[Network.MAINNET]["MULTI_SEND"],
    },
    Network.TESTNET: {
        "PC_TOKEN": TOKEN_ADDRESSES[Network.TESTNET]["PC_TOKEN"],
        "CTF_EXCHANGE": TOKEN_ADDRESSES[Network.TESTNET]["CTF_EXCHANGE"],
        "CONDITIONAL_TOKENS": TOKEN_ADDRESSES[Network.TESTNET]["CONDITIONAL_TOKENS"],
        "MULTI_SEND": TOKEN_ADDRESSES[Network.TESTNET]["MULTI_SEND"],
    },
}


# Sample order data
@dataclass(frozen=True)
class PlaceOrderSample:
    SIGNER_ADDRESS: str = (
        "0xc4D0EDDd8Dd741271419A0044d624646DF5D8B03"  # Sample user public wallet
    )
    MAKER_ADDRESS: str = (
        "0x5BDEd57E52d2a47F55c1cB7829558f99A541ec7f"  # Sample user proxy wallet address
    )

    PROTOCOL_NAME: str = "CTF Exchange"
    PROTOCOL_VERSION: str = "1"

    AMOUNT: int = 1
    PRICE: Decimal = Decimal("0.5")

    MARKET_ID: int = 7
    OUTCOME_ID: int = 10

    TOKEN_ID: int = int(
        "16857067677315976042371946575915213868828523458552027724604404849007529922229"
    )

    SIDE: int = 0  # 0: Buy, 1: Sell
    OUTCOME_TYPE: int = 0  # 0: No, 1: Yes
    TYPE: int = 1  # 1: Limit, 2: Market


# Order structure for EIP-712 signing
ORDER_STRUCTURE = [
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

# Trading modes
TRADING_MODE = {
    "RANDOM": "RANDOM",
    "IN_ORDER": "IN_ORDER",
}

# Order sides
SIDE = {"BUY": 0, "SELL": 1}
