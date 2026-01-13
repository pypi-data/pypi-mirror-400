"""
Forkast Python SDK
==================

Public entrypoint for the Forkast SDK.
"""

# --------------------
# Services
# --------------------
from forkast_py_client.services.market import MarketService
from forkast_py_client.services.account import AccountService
from forkast_py_client.services.balances import BalancesService
from forkast_py_client.services.order import OrderService

# --------------------
# Types
# --------------------
from forkast_py_client.types import (
    WalletDetails,
    LoginResponse,
    TokenApprovalResponse,
    UserProfile,
    BalanceResponse,
    OutcomeBalanceResponse,
    Event,
    Market,
    MarketOutcome,
    MarketPosition,
    MarketsResponse,
    MarketStatus,
    OutcomeType,
    OrderBook,
    TokenPrices,
)

# --------------------
# Config / constants
# --------------------
from forkast_py_client.config import Network, ENDPOINTS

# --------------------
# Utils
# --------------------
from forkast_py_client.utils import load_abi, create_provider_without_signer


# --------------------
# Main SDK facade
# --------------------
class ForkastSDK:
    """
    Main entrypoint for the Forkast SDK.

    Provides access to all Forkast services with shared
    network and API key configuration.
    """

    def __init__(
        self,
        network: Network = Network.TESTNET,
        api_key: str = "",
    ) -> None:
        self._network = network
        self._api_key = api_key

    def get_market_service(self) -> MarketService:
        """
        Get MarketService instance.
        """
        return MarketService(self._network, self._api_key)

    def get_account_service(self) -> AccountService:
        """
        Get AccountService instance.
        """
        return AccountService(self._network, self._api_key)

    def get_balances_service(self) -> BalancesService:
        """
        Get BalancesService instance.
        """
        return BalancesService(self._network, self._api_key)

    def get_order_service(self) -> OrderService:
        """
        Get OrderService instance.
        """
        return OrderService(self._network, self._api_key)


__all__ = [
    # SDK
    "ForkastSDK",
    # Services
    "MarketService",
    "AccountService",
    "BalancesService",
    "OrderService",
    # Types
    "WalletDetails",
    "LoginResponse",
    "TokenApprovalResponse",
    "UserProfile",
    "BalanceResponse",
    "OutcomeBalanceResponse",
    "Event",
    "Market",
    "MarketOutcome",
    "MarketPosition",
    "MarketsResponse",
    "MarketStatus",
    "OutcomeType",
    "OrderBook",
    "TokenPrices",
    # Config
    "Network",
    "ENDPOINTS",
    # Utils
    "load_abi",
    "create_provider_without_signer",
]
