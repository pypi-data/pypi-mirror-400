from dataclasses import dataclass
from typing import Optional


# Wallet details class returned by the `generate_wallet` method
@dataclass
class WalletDetails:
    private_key: str
    address: str


# Login response class returned by the `login_with_private_key` method
@dataclass
class LoginResponse:
    access_token: str
    wallet_salt: str


# Token approval data sign class used in `TokenApprovalResponse` class
@dataclass
class TokenApprovalDataSign:
    to: str
    value: int
    data: str
    operation: int
    nonce: int


# Token approval response class returned by the `approve_max_platform_credits_for_proxy_wallet` method
@dataclass
class TokenApprovalResponse:
    signature: str
    data_sign: TokenApprovalDataSign
    wallet_proxy: str


# User profile class returned by the `get_user` method
@dataclass
class UserProfile:
    id: str
    name: str
    email: str
    bio: str
    avatar: str
    wallet: str
    proxy_wallet: str
    created_at: str
    updated_at: str
    has_active_proxy_wallet: int
    is_admin: int
    is_region_warning_checked: int
    referral_code: str
    is_referred: Optional[bool]
    referred_at: Optional[str]
    is_won_market: int
    is_traded_market: int
    is_profitable: int
    is_linked_twitter: int
    is_terms_of_use_checked: int
    referral_count: str
    expiration_discount_at: Optional[str]
    is_referral_discount_active: bool
    twitter_username: str
    has_referred_others: bool
