from forkast_py_client.types import UserProfile


class AccountMapper:
    """
    Mapper class for converting raw user data to typed objects
    """

    @staticmethod
    def map_user(raw_user: dict) -> UserProfile:
        """
        Maps raw user data to an UserProfile class.

        :param raw_user: Raw user data from API
        :return: UserProfile class
        """
        return UserProfile(
            id=str(raw_user["id"]),
            name=str(raw_user["name"]),
            email=str(raw_user["email"]),
            bio=str(raw_user["bio"]),
            avatar=str(raw_user["avatar"]),
            wallet=str(raw_user["wallet"]),
            proxy_wallet=str(raw_user["proxyWallet"]),
            created_at=str(raw_user["createdAt"]),
            updated_at=str(raw_user["updatedAt"]),
            has_active_proxy_wallet=raw_user["hasActiveProxyWallet"],
            is_admin=raw_user["isAdmin"],
            is_region_warning_checked=raw_user["isRegionWarningChecked"],
            referral_code=str(raw_user["referralCode"]),
            is_referred=raw_user["isReferred"],
            referred_at=raw_user["referredAt"],
            is_won_market=raw_user["isWonMarket"],
            is_traded_market=raw_user["isTradedMarket"],
            is_profitable=raw_user["isProfitable"],
            is_linked_twitter=raw_user["isLinkedTwitter"],
            is_terms_of_use_checked=raw_user["isTermsOfUseChecked"],
            referral_count=str(raw_user["referralCount"]),
            expiration_discount_at=raw_user["expirationDiscountAt"],
            is_referral_discount_active=raw_user["isReferralDiscountActive"],
            twitter_username=str(raw_user["twitterUsername"]),
            has_referred_others=raw_user["hasReferredOthers"],
        )
