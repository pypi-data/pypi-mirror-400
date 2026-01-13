from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


# Order class
@dataclass
class Order:
    market_id: int
    outcome_id: int
    token_id: str
    side: int
    type: int
    outcome_type: int
    price: Decimal
    amount: int
    total: int
    max_matched_times: int
    expired_at: int


# Order data class used in `OrderResult` class
@dataclass
class OrderData:
    orders_id: int
    orders_address: str
    orders_type: int
    orders_side: int
    orders_outcome_type: int
    orders_status: int
    orders_price: str
    orders_average_price: str
    orders_amount: str
    orders_filled_amount: str
    orders_remaining_amount: str
    orders_total: str
    orders_created_at: str
    orders_expired_at: Optional[str]
    outcome_id: str
    outcome_outcome_type: int
    outcome_title: str
    outcome_result: str
    user_id: str
    user_name: str
    user_avatar: str
    market_id: str
    market_event_id: int
    market_title: str
    market_question: str
    market_image: str


# Order result class used in `OrderResponse` class
@dataclass
class OrderResult:
    data: List["OrderData"]


# Order response class returned by the `get_all_orders` and `place_single_order` methods
@dataclass
class OrderResponse:
    success: bool
    order_result: Optional[OrderResult] = None
    error: Optional[str] = None


# Order info class
@dataclass
class OrderInfo:
    SIGNER_ADDRESS: str
    MARKET_ADDRESS: str
    MARKET_ID: int
    AMOUNT: int
    PRICE: Decimal
    OUTCOME_ID: int
    TOKEN_ID: str
    OUTCOME_TYPE: int
    SIDE: int
    TYPE: int
