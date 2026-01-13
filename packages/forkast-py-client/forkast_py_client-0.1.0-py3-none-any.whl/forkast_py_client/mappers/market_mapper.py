from datetime import datetime
from forkast_py_client.types import (
    MarketOutcome,
    Market,
    OrderBookEntry,
    OrderBook,
    TokenPrice,
    TokenPrices,
    Event,
)


class MarketMapper:
    """
    Mapper class for converting raw JSON data to typed objects
    """

    @staticmethod
    def map_order_book(data: dict) -> OrderBook:
        """
        Maps raw data to an OrderBook class.

        :param data: Raw data from API
        :return: OrderBook class
        """
        return OrderBook(
            asks=[
                OrderBookEntry(price=entry["price"], size=entry["size"])
                for entry in data["asks"]
            ],
            bids=[
                OrderBookEntry(price=entry["price"], size=entry["size"])
                for entry in data["bids"]
            ],
        )

    @staticmethod
    def map_market(raw_market: dict) -> Market:
        """
        Maps raw market data to a Market class.

        :param raw_market: Raw market data from API
        :return: Market class
        """
        return Market(
            id=raw_market["id"],
            title=raw_market["title"],
            question=raw_market["question"],
            question_id=raw_market["questionId"],
            image=raw_market["image"],
            rules=raw_market["rules"],
            volume=raw_market["volume"],
            status=raw_market["status"],
            resolved_address=raw_market["resolvedAddress"],
            resolved_outcome=raw_market["resolvedOutcome"],
            resolved_outcome_id=raw_market["resolvedOutcomeId"],
            resolved_on=raw_market["resolvedOn"],
            open_order_number=raw_market["openOrderNumber"],
            positions=raw_market.get("positions", []),
            condition_id=raw_market["conditionId"],
            outcomes=[
                MarketMapper.map_outcome(outcome) for outcome in raw_market["outcomes"]
            ],
        )

    @staticmethod
    def map_outcome(raw_outcome: dict) -> MarketOutcome:
        """
        Maps raw outcome data to a MarketOutcome class.

        :param raw_outcome: Raw outcome data from API
        :return: MarketOutcome class
        """
        return MarketOutcome(
            id=raw_outcome["id"],
            title=raw_outcome["title"],
            price=raw_outcome["price"],
            token_id=raw_outcome["tokenId"],
            outcome_type=raw_outcome["outcomeType"],
        )

    @staticmethod
    def map_event(raw_event_data: dict) -> Event:
        """
        Maps raw event data to an Event class.

        :param raw_event_data: Raw event data from API
        :return: Event class
        """
        return Event(
            id=raw_event_data["id"],
            created_at=datetime.fromisoformat(raw_event_data["createdAt"]),
            title=raw_event_data["title"],
            description=raw_event_data["description"],
            status=raw_event_data["status"],
            start_date=datetime.fromisoformat(raw_event_data["startDate"]),
            end_date=datetime.fromisoformat(raw_event_data["endDate"]),
            image=raw_event_data["image"],
            resolution_source=raw_event_data["resolutionSource"],
            volume=raw_event_data["volume"],
            resolved_on=(
                datetime.fromisoformat(raw_event_data["resolvedOn"])
                if raw_event_data.get("resolvedOn")
                else None
            ),
            fixture_id=raw_event_data.get("fixtureId"),
            is_favorite=raw_event_data["isFavorite"],
            markets=[
                MarketMapper.map_market(market) for market in raw_event_data["markets"]
            ],
        )

    @staticmethod
    def map_token_prices(data: list[dict]) -> TokenPrices:
        """
        Maps raw data to a TokenPrices class.

        :param data: Raw data from API
        :return: TokenPrices class
        """
        return [
            TokenPrice(
                outcome_id=int(item["outcomeId"]),
                price=float(item["price"]),
                side=item["side"],
            )
            for item in data
        ]
