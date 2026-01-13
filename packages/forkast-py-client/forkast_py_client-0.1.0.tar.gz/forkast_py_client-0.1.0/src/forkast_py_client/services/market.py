import logging
import requests
from forkast_py_client.config import ENDPOINTS, Network
from forkast_py_client.mappers import MarketMapper
from forkast_py_client.types import Event, OrderBook, TokenPrices
from forkast_py_client.services.base import BaseService

logger = logging.getLogger(__name__)

"""
Market service for fetching market event, order book and token prices
"""


class MarketService(BaseService):
    def __init__(
        self,
        network: Network = Network.TESTNET,
        api_key: str = "",
    ) -> None:
        super().__init__(network=network, api_key=api_key)

    def get_event_data(
        self,
        event_id: str,
        access_token: str | None = None,
    ) -> Event:
        """
        Fetches event details by event ID.

        :param event_id: Unique identifier of the event
        :param access_token: Optional bearer access token for authentication
        :return: Parsed event data
        :raises ValueError: If the response format is invalid
        :raises RuntimeError: If the API request fails or response format is invalid
        """
        endpoint = ENDPOINTS[self.network]["EVENT"]
        url = f"{endpoint}/{event_id}"

        try:
            data = self._get(
                url,
                headers=self._headers(access_token=access_token),
            )

            if "data" not in data:
                raise ValueError("Invalid response format: missing data property")

            return MarketMapper.map_event(data["data"])

        except requests.HTTPError as e:
            logger.exception("Failed to fetch event data (event_id=%s)", event_id)
            raise RuntimeError("Failed to fetch event data") from e

        except Exception as e:
            logger.exception(
                "Unexpected error in get_event_data (event_id=%s)", event_id
            )
            raise RuntimeError("Unexpected error while getting event data") from e

    def get_order_book(
        self,
        market_id: int,
        outcome_id: int,
        outcome_type: int,
        access_token: str | None = None,
    ) -> OrderBook:
        """
        Fetches the order book for a specific market outcome.

        :param market_id: Market identifier
        :param outcome_id: Outcome identifier within the market
        :param outcome_type: Outcome type
        :param access_token: Optional bearer access token for authentication
        :return: Parsed order book data
        :raises RuntimeError: If the API request fails
        """
        endpoint = ENDPOINTS[self.network]["ORDERBOOK"]
        url = (
            f"{endpoint}?marketId={market_id}"
            f"&outcomeId={outcome_id}"
            f"&outcomeType={outcome_type}"
        )

        try:
            data = self._get(
                url,
                headers=self._headers(access_token=access_token),
            )

            return MarketMapper.map_order_book(data)

        except requests.HTTPError as e:
            logger.exception(
                "Failed to fetch order book "
                "(market_id=%s, outcome_id=%s, outcome_type=%s)",
                market_id,
                outcome_id,
                outcome_type,
            )
            raise RuntimeError("Failed to fetch order book") from e

        except Exception as e:
            logger.exception(
                "Unexpected error in get_order_book (market_id=%s, outcome_id=%s, outcome_type=%s)",
                market_id,
                outcome_id,
                outcome_type,
            )
            raise RuntimeError("Unexpected error while getting orderbook data") from e

    def get_token_prices(
        self,
        market_id: int,
        side: int = 0,
        access_token: str | None = None,
    ) -> TokenPrices:
        """
        Fetches token price information for a market.

        :param market_id: Market identifier
        :param side: Trade side (0 = buy, 1 = sell)
        :param access_token: Optional bearer access token for authentication
        :return: Parsed token price data
        :raises RuntimeError: If the API request fails or response format is invalid
        """
        endpoint = ENDPOINTS[self.network]["TOKEN_PRICE"]
        url = f"{endpoint}?marketId={market_id}&side={side}"

        try:
            data = self._get(
                url,
                headers=self._headers(access_token=access_token),
            )

            if "data" not in data:
                raise ValueError("Invalid response format: missing data property")

            return MarketMapper.map_token_prices(data["data"])

        except requests.HTTPError as e:
            logger.exception(
                "Failed to fetch token prices " "(market_id=%s, side=%s)",
                market_id,
                side,
            )
            raise RuntimeError("Failed to fetch token prices") from e

        except Exception as e:
            logger.exception(
                "Unexpected error in get_token_prices (market_id=%s, side=%s)",
                market_id,
                side,
            )
            raise RuntimeError(
                "Unexpected error while getting token prices data"
            ) from e
