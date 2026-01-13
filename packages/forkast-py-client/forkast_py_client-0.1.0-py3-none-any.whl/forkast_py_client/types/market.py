from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


# Market status enum used in `Market` class
class MarketStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"


# Market position class used in `Market` class
@dataclass
class MarketPosition:
    outcome_id: str
    amount: str
    price: int


# Outcome type enum used in `MarketOutcome` class
class OutcomeType(str, Enum):
    NO = 0
    YES = 1


# Market outcome class used in `Market` class
@dataclass
class MarketOutcome:
    id: int  # outcome id
    token_id: str  # token id
    outcome_type: OutcomeType

    title: Optional[str] = None
    price: Optional[float] = None


# Market class
@dataclass
class Market:
    id: int
    title: str
    question: str
    question_id: str
    image: str
    rules: str
    volume: str
    status: MarketStatus

    resolved_address: Optional[str]
    resolved_outcome: Optional[str]
    resolved_outcome_id: Optional[str]
    resolved_on: Optional[str]

    open_order_number: int
    positions: List[MarketPosition]
    condition_id: str
    outcomes: List[MarketOutcome]


# Markets response class
@dataclass
class MarketsResponse:
    markets: List[Market]


# Orderbook entry class used in `OrderBook` class
@dataclass
class OrderBookEntry:
    price: str
    size: str


# Orderbook class returned by the `get_order_book` method
@dataclass
class OrderBook:
    asks: List[OrderBookEntry]
    bids: List[OrderBookEntry]


# Side enum used in `TokenPrice` class
class Side(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


# Token price class used in `TokenPrices`
@dataclass
class TokenPrice:
    outcome_id: int
    price: float
    side: Side


# Token prices returned by the `get_token_prices` method
TokenPrices = List[TokenPrice]


# Event class returned by the `get_event_data` method
@dataclass
class Event:
    id: int
    created_at: datetime
    title: str
    description: str
    status: str
    start_date: datetime
    end_date: datetime
    image: str
    resolution_source: str
    volume: str
    resolved_on: Optional[datetime]
    is_favorite: int
    markets: List[Market]
    fixture_id: Optional[str]
