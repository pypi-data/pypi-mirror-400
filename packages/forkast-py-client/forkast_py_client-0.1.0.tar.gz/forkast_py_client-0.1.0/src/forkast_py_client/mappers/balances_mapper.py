from forkast_py_client.types import BalanceResponse, OutcomeBalanceResponse


class BalancesMapper:
    """
    Mapper class for converting raw balance data to typed objects
    """

    @staticmethod
    def map_balance(raw_balance: dict) -> BalanceResponse:
        """
        Maps raw balance data to a BalanceResponse class.

        :param raw_balance: Raw balance data from API
        :return: BalanceResponse class
        """
        return BalanceResponse(
            id=str(raw_balance["id"]),
            created_at=raw_balance["createdAt"],
            updated_at=raw_balance["updatedAt"],
            deleted_at=raw_balance["deletedAt"],
            user_id=int(raw_balance["userId"]),
            balance_usdc=str(raw_balance["balanceUSDC"]),
            lock_balance_usdc=str(raw_balance["lockBalanceUSDC"]),
            balance_usdt=str(raw_balance["balanceUSDT"]),
            lock_balance_usdt=str(raw_balance["lockBalanceUSDT"]),
            balance_cgpc=str(raw_balance["balanceCGPC"]),
            lock_balance_cgpc=str(raw_balance["lockBalanceCGPC"]),
            wallet_proxy_address=raw_balance["walletProxyAddress"],
            wallet_address=raw_balance["walletAddress"],
        )

    @staticmethod
    def map_outcome_balance(raw_outcome_balance: dict) -> OutcomeBalanceResponse:
        """
        Map raw outcome balance data to an OutcomeBalanceResponse class.

        :param raw_outcome_balance: Raw outcome balance data from API
        :return: OutcomeBalanceResponse class
        """
        return OutcomeBalanceResponse(
            id=str(raw_outcome_balance["id"]),
            created_at=raw_outcome_balance["createdAt"],
            updated_at=raw_outcome_balance["updatedAt"],
            deleted_at=raw_outcome_balance["deletedAt"],
            user_id=int(raw_outcome_balance["userId"]),
            outcome_id=int(raw_outcome_balance["outcomeId"]),
            token_id=str(raw_outcome_balance["tokenId"]),
            balance=str(raw_outcome_balance["balance"]),
            locked_balance=str(raw_outcome_balance["lockedBalance"]),
        )
