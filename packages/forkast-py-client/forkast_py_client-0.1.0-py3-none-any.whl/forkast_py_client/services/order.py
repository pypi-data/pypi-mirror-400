from decimal import Decimal, ROUND_DOWN
import hashlib
import logging
import secrets
import time
import requests
from typing import Dict
from eth_account import Account
from eth_utils import is_address
from web3 import Web3
from forkast_py_client.config import (
    ENDPOINTS,
    Network,
    PREPARE_ACTIVE_PROXY,
    PREPARE_APPROVE_TOKEN,
    ORDER_STRUCTURE,
)
from forkast_py_client.mappers import OrderMapper
from forkast_py_client.services.base import BaseService
from forkast_py_client.services import MarketService, BalancesService
from forkast_py_client.types import MarketOutcome, OrderResponse
from forkast_py_client.utils import load_abi, create_provider_without_signer

logger = logging.getLogger(__name__)

"""
Order service for fetching, canceling and placing order
"""


class OrderService(BaseService):
    def __init__(
        self,
        network: Network = Network.TESTNET,
        api_key: str = "",
    ) -> None:
        super().__init__(network=network, api_key=api_key)

    def _validate_wallet_and_key(self, wallet: str, private_key: str) -> None:
        """
        Validates that the wallet address and private key are present and match.

        :param wallet: Wallet address to validate
        :param private_key: Private key corresponding to the wallet
        :raises ValueError: If wallet or private key is invalid or mismatched
        """
        if not wallet or not is_address(wallet):
            raise ValueError("Invalid or missing wallet address")

        if (
            not private_key
            or not private_key.startswith("0x")
            or len(private_key) != 66
        ):
            raise ValueError("Invalid or missing private key")

        try:
            acct = Account.from_key(private_key)
        except Exception as exc:
            raise ValueError(
                "Failed to extract wallet address from private key"
            ) from exc

        if acct.address.lower() != wallet.lower():
            raise ValueError("Wallet address does not match the private key")

    def get_all_orders(
        self,
        address: str,
        outcome_id: int,
        access_token: str,
        status: int = 1,
        limit: int = 1000,
        page: int = 1,
    ) -> OrderResponse:
        """
        Fetches all orders for a given wallet address and outcome.

        :param address: Wallet address to query orders for
        :param outcome_id: Outcome ID to filter orders
        :param access_token: Bearer access token for authentication
        :param status: Order status filter
        :param limit: Maximum number of orders per page
        :param page: Page number for pagination
        :return: Parsed order response
        :raises RuntimeError: If the API request fails
        """
        endpoint = ENDPOINTS[self.network]["GET_ORDER"]
        url = (
            f"{endpoint}"
            f"?status={status}"
            f"&limit={limit}"
            f"&outcomeId={outcome_id}"
            f"&page={page}"
            f"&address={address}"
        )

        try:
            data = self._get(
                url,
                headers=self._headers(access_token=access_token),
            )

            return OrderMapper.map_order_response(data)

        except requests.HTTPError as e:
            logger.exception("Failed to fetch all orders")
            raise RuntimeError("Failed to fetch all orders") from e

        except Exception as e:
            logger.exception("Unexpected error in get_all_orders")
            raise RuntimeError("Unexpected error while getting all orders") from e

    def cancel_order(self, order_id: str, access_token: str) -> dict:
        """
        Cancels an existing order by order ID.

        :param order_id: ID of the order to cancel
        :param access_token: Bearer access token for authentication
        :return: API response payload
        :raises RuntimeError: If the cancel request fails
        """
        endpoint = ENDPOINTS[self.network]["CANCEL_ORDER"]
        url = f"{endpoint}/{order_id}"

        try:
            return self._post(
                url,
                data={},
                headers=self._headers(access_token=access_token),
            )

        except requests.HTTPError as e:
            logger.exception("Failed to cancel order (order_id=%s)", order_id)
            raise RuntimeError("Failed to cancel order") from e

        except Exception as e:
            logger.exception(
                "Unexpected error while canceling order (order_id=%s)", order_id
            )
            raise RuntimeError("Unexpected error while canceling order") from e

    def _build_order(
        self,
        wallet: str,
        proxy_wallet: str,
        market_id: int,
        amount: float,
        price: float,
        token: MarketOutcome,
        side: int,
    ):
        """
        Builds an internal order object used for signing and submission.

        :param wallet: Signer wallet address
        :param proxy_wallet: Proxy (maker) wallet address
        :param market_id: Market identifier
        :param amount: Order amount
        :param price: Order price
        :param token: Market outcome information
        :param side: Order side (0 = buy, 1 = sell)
        :return: Order payload dictionary
        """
        return {
            "SIGNER_ADDRESS": wallet,
            "MAKER_ADDRESS": proxy_wallet,
            "MARKET_ID": int(market_id),
            "AMOUNT": amount,
            "PRICE": price,
            "OUTCOME_ID": int(token.id),
            "TOKEN_ID": token.token_id,
            "OUTCOME_TYPE": token.outcome_type,
            "SIDE": side,
            "TYPE": 1,  # 1: Limit, 2: Market
        }

    def _generate_order_salt(self, order_info: dict) -> str:
        """
        Generate random order salt

        :param order_info: Order information dictionary
        :return: uint256-compatible salt
        """
        price = Decimal(str(order_info["PRICE"])).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        amount = Decimal(str(order_info["AMOUNT"])).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        entropy = secrets.token_bytes(8).hex()  # 64 bit randomness

        raw = "|".join(
            [
                order_info["SIGNER_ADDRESS"].lower(),
                order_info["MAKER_ADDRESS"].lower(),
                str(order_info["MARKET_ID"]),
                str(order_info["OUTCOME_ID"]),
                str(order_info["TOKEN_ID"]),
                str(order_info["OUTCOME_TYPE"]),
                str(order_info["SIDE"]),
                str(order_info["TYPE"]),
                str(price),
                str(amount),
                str(time.time_ns()),
                entropy,
            ]
        )

        digest = hashlib.sha256(raw.encode()).hexdigest()
        return str(int(digest, 16) % (2**53 - 1))

    def _validate_order(self, event_id: int, order_info: dict, access_token: str):
        """
        Validates order before signing & submission

        :param event_id: Unique identifier of the event
        :param order_info: Order information dictionary
        :param access_token: Optional bearer access token for authentication
        :raises RuntimeError: If the API request fails
        """
        # -------- Validate inputs --------
        if order_info["SIDE"] not in (0, 1):
            raise ValueError("Invalid order side")
        if order_info["AMOUNT"] <= 0:
            raise ValueError("Order amount must be greater than 0")
        if not (0 < order_info["PRICE"] < 1):
            raise ValueError("Order price must be between 0 and 1")
        d_price = Decimal(str(order_info["PRICE"]))
        decimals_price = (
            -d_price.as_tuple().exponent if d_price.as_tuple().exponent < 0 else 0
        )
        if decimals_price > 2:
            raise ValueError(
                f"price supports at most 2 decimal places, got {decimals_price}: {order_info['PRICE']}"
            )
        d_amount = Decimal(str(order_info["AMOUNT"]))
        decimals_amount = (
            -d_amount.as_tuple().exponent if d_amount.as_tuple().exponent < 0 else 0
        )
        if decimals_amount > 2:
            raise ValueError(
                f"amount supports at most 2 decimal places, got {decimals_amount}: {order_info["AMOUNT"]}"
            )

        market_service = MarketService(self.network, self.api_key)
        event_data = market_service.get_event_data(event_id, access_token)

        # -------- Find and validate market id --------
        market_id = str(order_info["MARKET_ID"])
        market = next(
            (m for m in event_data.markets if str(m.id) == market_id),
            None,
        )
        if not market:
            raise RuntimeError(f"Market {market_id} not found in event {event_id}")

        # -------- Find and validate outcome id --------
        outcome_id = str(order_info["OUTCOME_ID"])
        outcome = next(
            (o for o in market.outcomes if str(o.id) == outcome_id),
            None,
        )
        if not outcome:
            raise RuntimeError(f"Outcome {outcome_id} not found in market {market_id}")

        # -------- Validate outcome token id --------
        if str(outcome.token_id) != str(order_info["TOKEN_ID"]):
            raise RuntimeError(
                "Outcome tokenId mismatch: "
                f"expected {outcome.token_id}, "
                f"got {order_info['TOKEN_ID']}"
            )

        # -------- Validate outcome type --------
        if int(outcome.outcome_type) != int(order_info["OUTCOME_TYPE"]):
            raise RuntimeError(
                "Outcome type mismatch: "
                f"expected {int(outcome.outcome_type)}, "
                f"got {order_info['OUTCOME_TYPE']}"
            )

        # -------- Validate balance --------
        balances_service = BalancesService(self.network, self.api_key)
        SCALE = Decimal(1_000_000)
        amount = Decimal(str(order_info["AMOUNT"])).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        price = Decimal(str(order_info["PRICE"])).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        if order_info["SIDE"] == 0:  # BUY
            maker_amount = (price * amount).quantize(
                Decimal("0.00"), rounding=ROUND_DOWN
            )
            balances = balances_service.get_balances(access_token)
            balance_cgpc = Decimal(str(balances.balance_cgpc))
            lock_balance_cgpc = Decimal(str(balances.lock_balance_cgpc))
            available_balance_cgpc = balance_cgpc - lock_balance_cgpc
            if maker_amount > available_balance_cgpc:
                raise RuntimeError("Not enough PC balance")

        else:  # SELL
            outcome_balances = balances_service.get_outcome_balances(
                order_info["TOKEN_ID"], access_token
            )
            outcome_balance = Decimal(str(outcome_balances.balance))
            outcome_locked_balance = Decimal(str(outcome_balances.locked_balance))
            available_outcome_balance = outcome_balance - outcome_locked_balance
            if amount > available_outcome_balance:
                raise RuntimeError("Not enough outcome token balance")

        # -------- Validate allowance --------
        w3: Web3 = create_provider_without_signer(self.network)
        order_maker = order_info["MAKER_ADDRESS"]
        exchange = PREPARE_APPROVE_TOKEN[self.network]["CTF_EXCHANGE"]

        if order_info["SIDE"] == 0:  # BUY
            maker_amount = (
                (amount * price).quantize(Decimal("0.00"), rounding=ROUND_DOWN) * SCALE
            ).to_integral_value(rounding=ROUND_DOWN)
            pc_token_abi = load_abi("PCToken.abi.json")
            pc_token = w3.eth.contract(
                address=PREPARE_APPROVE_TOKEN[self.network]["PC_TOKEN"],
                abi=pc_token_abi,
            )
            pc_allowance = pc_token.functions.allowance(order_maker, exchange).call()
            if pc_allowance == 0:
                raise RuntimeError(
                    "PC allowance is 0. " "Please approve before placing order."
                )
            if pc_allowance < maker_amount:
                raise RuntimeError(
                    "PC allowance is not enough. "
                    "Please approve before placing order."
                )

        else:  # SELL
            conditional_token_abi = load_abi("ConditionalTokens.abi.json")
            conditional_tokens = w3.eth.contract(
                address=PREPARE_APPROVE_TOKEN[self.network]["CONDITIONAL_TOKENS"],
                abi=conditional_token_abi,
            )
            is_approved_for_all = conditional_tokens.functions.isApprovedForAll(
                order_maker, exchange
            ).call()
            if not is_approved_for_all:
                raise RuntimeError(
                    "ERC1155 token not approved for exchange. "
                    "Please approve before placing order."
                )

    def _sign_and_send_order(
        self,
        order_info: dict,
        private_key: str,
        access_token: str,
    ):
        """
        Signs an order using EIP-712 and submits it to the exchange.

        :param order_info: Order information dictionary
        :param private_key: Private key used to sign the order
        :param access_token: Bearer access token for authentication
        :return: API response payload
        :raises RuntimeError: If the API request fails
        """
        salt = self._generate_order_salt(order_info)
        price = Decimal(str(order_info["PRICE"])).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        amount = Decimal(str(order_info["AMOUNT"])).quantize(
            Decimal("0.00"), rounding=ROUND_DOWN
        )
        total = (price * amount).quantize(Decimal("0.00"), rounding=ROUND_DOWN)

        # ---------- orderData ----------
        order_data = {
            "marketId": order_info["MARKET_ID"],
            "outcomeId": order_info["OUTCOME_ID"],
            "tokenId": order_info["TOKEN_ID"],
            "side": order_info["SIDE"],
            "type": order_info["TYPE"],
            "outcomeType": order_info["OUTCOME_TYPE"],
            "price": str(price),
            "amount": str(amount),
            "total": str(total),
            "maxMatchedTimes": 9999,
            "expiredAt": 0,
        }

        # ---------- amounts ----------
        SCALE = Decimal(1_000_000)
        if order_info["SIDE"] == 0:  # BUY
            maker_amount = (
                (amount * price).quantize(Decimal("0.00"), rounding=ROUND_DOWN) * SCALE
            ).to_integral_value(rounding=ROUND_DOWN)

            taker_amount = (amount * SCALE).to_integral_value(rounding=ROUND_DOWN)

        else:  # SELL
            maker_amount = (amount * SCALE).to_integral_value(rounding=ROUND_DOWN)

            taker_amount = (
                (amount * price).quantize(Decimal("0.00"), rounding=ROUND_DOWN) * SCALE
            ).to_integral_value(rounding=ROUND_DOWN)

        maker_amount = int(maker_amount)
        taker_amount = int(taker_amount)

        # ---------- EIP-712 ----------
        order_typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Order": ORDER_STRUCTURE,
            },
            "primaryType": "Order",
            "domain": {
                "name": "CTF Exchange",
                "version": "1",
                "chainId": PREPARE_ACTIVE_PROXY[self.network]["CHAIN_ID"],
                "verifyingContract": PREPARE_APPROVE_TOKEN[self.network][
                    "CTF_EXCHANGE"
                ],
            },
            "message": {
                "salt": salt,
                "maker": order_info["MAKER_ADDRESS"],
                "signer": order_info["SIGNER_ADDRESS"],
                "taker": Web3.to_checksum_address(
                    "0x0000000000000000000000000000000000000000"
                ),
                "tokenId": order_info["TOKEN_ID"],
                "makerAmount": str(maker_amount),
                "takerAmount": str(taker_amount),
                "expiration": "0",
                "nonce": "0",
                "feeRateBps": "0",
                "side": order_info["SIDE"],
                "signatureType": 3,
                "signature": "",
            },
        }

        # ---------- sign ----------
        signed = Account.sign_typed_data(private_key, full_message=order_typed_data)
        order_typed_data["message"]["signature"] = signed.signature.hex()

        endpoint = ENDPOINTS[self.network]["ADD_ORDER"]

        try:
            resp = self._post(
                endpoint,
                data={
                    **order_data,
                    "order": order_typed_data["message"],
                },
                headers=self._headers(access_token=access_token),
            )

            return resp

        except requests.HTTPError as e:
            logger.exception(
                "Failed to place order (market_id=%s, side=%s)",
                order_info["MARKET_ID"],
                order_info["SIDE"],
            )
            raise RuntimeError("Failed to place order") from e

        except Exception as e:
            logger.exception(
                "Unexpected error while placing order (market_id=%s, side=%s)",
                order_info["MARKET_ID"],
                order_info["SIDE"],
            )
            raise RuntimeError("Unexpected error while placing order") from e

    def place_single_order(
        self,
        event_id: int,
        market_id: int,
        token: MarketOutcome,
        account: Dict[str, str],
        price: float,
        amount: float,
        side: int,
        access_token: str,
    ) -> OrderResponse:
        """
        Places a single order and returns a structured order response.

        :param market_id: Market identifier
        :param token: Market outcome information
        :param account: Account information including wallet and private key
        :param price: Order price
        :param amount: Order amount
        :param side: Order side (0 = buy, 1 = sell)
        :param access_token: Bearer access token for authentication
        :return: OrderResponse indicating success or failure
        """
        try:
            # ---------- Validate (fail fast) ----------
            self._validate_wallet_and_key(
                account["wallet"],
                account["private_key"],
            )

            # ---------- Build order ----------
            order = self._build_order(
                wallet=account["wallet"],
                proxy_wallet=account["proxy_wallet"],
                market_id=market_id,
                amount=amount,
                price=price,
                token=token,
                side=side,
            )

            # ---------- Validate order ----------
            self._validate_order(
                event_id=event_id, order_info=order, access_token=access_token
            )

            # ---------- Sign & send order ----------
            resp = self._sign_and_send_order(
                order_info=order,
                private_key=account["private_key"],
                access_token=access_token,
            )

            return OrderResponse(success=True, order_result=resp)

        except ValueError as exc:
            logger.warning("Order validation failed: %s", exc)
            return OrderResponse(success=False, error=str(exc))

        except RuntimeError as exc:
            logger.error("Order error: %s", exc)
            return OrderResponse(success=False, error=str(exc))

        except Exception:
            logger.exception("Unexpected error while placing order")
            return OrderResponse(success=False, error="Failed to place order")
