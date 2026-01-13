import logging
import requests
from forkast_py_client.config import Network, ENDPOINTS
from forkast_py_client.mappers import BalancesMapper
from forkast_py_client.types import BalanceResponse, OutcomeBalanceResponse
from forkast_py_client.services.base import BaseService

logger = logging.getLogger(__name__)

"""
Balance service for fetching balance information
"""


class BalancesService(BaseService):
    def __init__(
        self,
        network: Network = Network.TESTNET,
        api_key: str = "",
    ) -> None:
        super().__init__(network=network, api_key=api_key)

    def get_balances(self, access_token: str) -> BalanceResponse:
        """
        Retrieves the balances of the authenticated user.

        :param access_token: User access token for authentication
        :return: Parsed balance response
        :raises RuntimeError: If the API request fails or an unexpected error occurs
        """
        endpoint = ENDPOINTS[self.network]["BALANCE"]

        try:
            data = self._get(
                endpoint,
                headers=self._headers(access_token=access_token),
            )

            if not data:
                return BalanceResponse(
                    id="",
                    created_at="",
                    updated_at="",
                    deleted_at=None,
                    user_id=0,
                    balance_usdc="0",
                    lock_balance_usdc="0",
                    balance_usdt="0",
                    lock_balance_usdt="0",
                    balance_cgpc="0",
                    lock_balance_cgpc="0",
                    wallet_proxy_address="",
                    wallet_address="",
                )

            return BalancesMapper.map_balance(data)

        except requests.HTTPError as e:
            logger.exception("Failed to fetch balances")
            raise RuntimeError("Failed to fetch balances") from e

        except Exception as e:
            logger.exception("Unexpected error in get_balances")
            raise RuntimeError("Unexpected error while fetching balances") from e

    def get_outcome_balances(
        self, token_id: str, access_token: str
    ) -> OutcomeBalanceResponse:
        """
        Retrieves the outcome balances of the authenticated user.

        :param access_token: User access token for authentication
        :return: Parsed outcome balances response
        :raises RuntimeError: If the API request fails or an unexpected error occurs
        """
        endpoint = ENDPOINTS[self.network]["BALANCE"]
        url = f"{endpoint}/{token_id}/outcomes"

        try:
            data = self._get(
                url,
                headers=self._headers(access_token=access_token),
            )

            if not data:
                return OutcomeBalanceResponse(
                    id="",
                    created_at="",
                    updated_at="",
                    deleted_at=None,
                    user_id=0,
                    outcome_id=0,
                    token_id="0",
                    balance="0",
                    locked_balance="0",
                )

            return BalancesMapper.map_outcome_balance(data)

        except requests.HTTPError as e:
            logger.exception("Failed to fetch outcome balances")
            raise RuntimeError("Failed to fetch outcome balances") from e

        except Exception as e:
            logger.exception("Unexpected error in get_outcome_balances")
            raise RuntimeError(
                "Unexpected error while fetching outcome balances"
            ) from e
