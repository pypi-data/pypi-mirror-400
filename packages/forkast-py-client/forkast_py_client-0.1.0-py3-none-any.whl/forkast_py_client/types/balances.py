from dataclasses import dataclass
from typing import Optional


# Balance response class returned by the `get_balances` method
@dataclass
class BalanceResponse:
    id: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    user_id: int
    balance_usdc: str
    lock_balance_usdc: str
    balance_usdt: str
    lock_balance_usdt: str
    balance_cgpc: str
    lock_balance_cgpc: str
    wallet_proxy_address: str
    wallet_address: str


# Outcome balance response class returned by the `get_outcome_balances` method
@dataclass
class OutcomeBalanceResponse:
    id: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    user_id: int
    outcome_id: int
    token_id: str
    balance: str
    locked_balance: str
