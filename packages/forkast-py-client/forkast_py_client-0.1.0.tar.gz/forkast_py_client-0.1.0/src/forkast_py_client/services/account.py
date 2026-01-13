import base64
from decimal import Decimal
import json
import logging
import requests
from typing import Optional, List, Dict, Any
from eth_abi import encode
from eth_abi.packed import encode_packed
from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data
from eth_account.signers.local import LocalAccount
from web3 import Web3
from forkast_py_client.config import (
    MAX_UINT256,
    MAX_BUY_AMOUNT,
    Network,
    ENDPOINTS,
    PREPARE_ACTIVE_PROXY,
    PREPARE_APPROVE_TOKEN,
)
from forkast_py_client.mappers import AccountMapper
from forkast_py_client.services.base import BaseService
from forkast_py_client.types import (
    TokenApprovalResponse,
    UserProfile,
    WalletDetails,
    LoginResponse,
)
from forkast_py_client.utils import load_abi, create_provider_without_signer

logger = logging.getLogger(__name__)


"""
Account service for account-related operations
"""


class AccountService(BaseService):
    def __init__(
        self,
        network: Network = Network.TESTNET,
        api_key: str = "",
    ) -> None:
        super().__init__(network=network, api_key=api_key)

    def generate_wallet(self) -> WalletDetails:
        """
        Generates a new Ethereum wallet.

        :return: Wallet details including private key and address
        """
        acct = Account.create()
        return WalletDetails(private_key=acct.key.hex(), address=acct.address)

    def login_with_private_key(self, private_key: str) -> LoginResponse:
        """
        Authenticates a user by signing a predefined message
        with the provided private key.

        :param private_key: User private key
        :return: Login response containing access token and wallet salt
        :raises RuntimeError: If login fails or an unexpected error occurs
        """
        acct = Account.from_key(private_key)

        message = PREPARE_ACTIVE_PROXY[self.network]["PUBLIC_MESSAGE_SIGN"]
        signed_message = Account.sign_message(encode_defunct(text=message), private_key)

        endpoint = ENDPOINTS[self.network]["LOGIN"]

        try:
            resp = self._post(
                endpoint,
                data={
                    "address": acct.address,
                    "signature": signed_message.signature.hex(),
                    "message": message,
                },
                headers=self._headers(),
            )

            return LoginResponse(
                access_token=resp["accessToken"],
                wallet_salt=resp["walletSalt"],
            )

        except requests.HTTPError as e:
            logger.exception("Login with private key failed")
            raise RuntimeError("Login with private key failed") from e

        except Exception as e:
            logger.exception("Unexpected error during login")
            raise RuntimeError("Unexpected error during login") from e

    def parse_jwt(self, token: str) -> dict[str, Any]:
        """
        Parses a JWT token payload without verifying its signature.

        :param token: JWT token string
        :return: Decoded JWT payload
        :raises ValueError: If token parsing fails
        """
        try:
            payload_part = token.split(".")[1]

            # Add padding if missing
            padding = "=" * (-len(payload_part) % 4)

            decoded_bytes = base64.urlsafe_b64decode(payload_part + padding)
            decoded_str = decoded_bytes.decode("utf-8")

            return json.loads(decoded_str)

        except Exception as e:
            raise ValueError("Failed to parse JWT token") from e

    def _build_multi_send_data(self, transactions: List[Dict[str, Any]]) -> str:
        """
        Builds calldata for Gnosis Safe MultiSend contract.

        :param transactions: List of transaction dictionaries
        :return: Hex-encoded multisend calldata
        """
        multi_send_arg = b""

        for tx in transactions:
            operation = 0  # CALL
            to = Web3.to_checksum_address(tx["to"])
            value = int(tx["value"])
            data = bytes.fromhex(tx["data"][2:])  # strip 0x

            encoded_tx = encode_packed(
                ["uint8", "address", "uint256", "uint256", "bytes"],
                [operation, to, value, len(data), data],
            )

            multi_send_arg += encoded_tx

        # encode function call: multiSend(bytes)
        selector = Web3.keccak(text="multiSend(bytes)")[:4]
        calldata = selector + encode(["bytes"], [multi_send_arg])

        return "0x" + calldata.hex()

    @staticmethod
    def _build_approve_data(spender: str, amount: int) -> str:
        """
        Builds ERC20 approve(spender, amount) calldata.

        :param spender: Address allowed to spend tokens
        :param amount: Approval amount
        :return: Hex-encoded calldata
        """
        selector = Web3.keccak(text="approve(address,uint256)")[:4]
        args = encode(
            ["address", "uint256"],
            [Web3.to_checksum_address(spender), int(amount)],
        )
        return "0x" + (selector + args).hex()

    async def _build_approve_token_data(
        self,
        proxy_wallet_address: str,
        ctf_exchange_address: str,
        pc_amount: int,
        conditional_tokens,
        pc_token,
    ) -> Optional[str]:
        """
        Builds multisend calldata to approve Platform Credits token
        and Conditional Tokens if required.

        :param proxy_wallet_address: Proxy (maker) wallet address
        :param ctf_exchange_address: Exchange address
        :param pc_amount: Platform Credits token amount
        :param conditional_tokens: Conditional token address
        :param pc_token: Platform Credits token address
        :return: Multisend calldata or None if no approval is needed
        """
        proxy_wallet_address = Web3.to_checksum_address(proxy_wallet_address)
        ctf_exchange_address = Web3.to_checksum_address(ctf_exchange_address)

        multisend_txs = []

        # -------- ERC20 allowance check --------
        pc_allowance = pc_token.functions.allowance(
            proxy_wallet_address, ctf_exchange_address
        ).call()

        if pc_allowance < pc_amount:
            approve_data = self._build_approve_data(ctf_exchange_address, MAX_UINT256)
            multisend_txs.append(
                {"to": pc_token.address, "value": 0, "data": approve_data}
            )
        else:
            return None

        # -------- ConditionalTokens approval --------
        is_approved_for_all = conditional_tokens.functions.isApprovedForAll(
            proxy_wallet_address, ctf_exchange_address
        ).call()

        if not is_approved_for_all:
            selector = Web3.keccak(text="setApprovalForAll(address,bool)")[:4]
            args = encode(
                ["address", "bool"],
                [ctf_exchange_address, True],
            )
            multisend_txs.append(
                {
                    "to": conditional_tokens.address,
                    "value": 0,
                    "data": "0x" + (selector + args).hex(),
                }
            )

        if not multisend_txs:
            return None

        return self._build_multi_send_data(multisend_txs)

    def _sign_proxy_wallet_transaction(
        self,
        signer: Account,
        contract_address: str,
        chain_id: int,
        to: str,
        value: int,
        data: str,
        nonce: int,
        operation: int,
    ) -> str:
        """
        Signs a Gnosis Safe transaction using EIP-712 typed data (SafeTx).

        :param signer: Local account used to sign the transaction
        :param contract_address: Gnosis Safe (proxy wallet) contract address
        :param chain_id: Chain ID of the target network
        :param to: Destination contract address
        :param value: ETH value to send (in wei)
        :param data: Hex-encoded calldata
        :param nonce: Safe transaction nonce
        :param operation: Operation type (0 = CALL, 1 = DELEGATE_CALL)
        :return: Hex-encoded EIP-712 signature
        """

        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "SafeTx": [
                    {"name": "to", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "data", "type": "bytes"},
                    {"name": "operation", "type": "uint8"},
                    {"name": "safeTxGas", "type": "uint256"},
                    {"name": "baseGas", "type": "uint256"},
                    {"name": "gasPrice", "type": "uint256"},
                    {"name": "gasToken", "type": "address"},
                    {"name": "refundReceiver", "type": "address"},
                    {"name": "nonce", "type": "uint256"},
                ],
            },
            "primaryType": "SafeTx",
            "domain": {
                "chainId": int(chain_id),
                "verifyingContract": Web3.to_checksum_address(contract_address),
            },
            "message": {
                "to": Web3.to_checksum_address(to),
                "value": int(value),
                "data": bytes.fromhex(data[2:]),
                "operation": int(operation),
                "safeTxGas": 0,
                "baseGas": 0,
                "gasPrice": 0,
                "gasToken": Web3.to_checksum_address(
                    "0x0000000000000000000000000000000000000000"
                ),
                "refundReceiver": Web3.to_checksum_address(
                    "0x0000000000000000000000000000000000000000"
                ),
                "nonce": int(nonce),
            },
        }

        signable_message = encode_typed_data(full_message=typed_data)
        signed = signer.sign_message(signable_message)

        return signed.signature.hex()

    async def approve_max_platform_credits_for_proxy_wallet(
        self,
        signer: LocalAccount,
        wallet_proxy_address: str,
        buy_amount: int = MAX_BUY_AMOUNT,
    ) -> TokenApprovalResponse | None:
        """
        Builds and signs a Gnosis Safe multisend transaction to approve
        the maximum Platform Credits (PC) and Conditional Tokens for trading.

        :param signer: Local account used to sign the Safe transaction
        :param wallet_proxy_address: Gnosis Safe proxy wallet address
        :param buy_amount: Maximum amount of Platform Credits to approve
        :return:
            - TokenApprovalResponse if approval is required
            - None if no approval is needed
        :raises ValueError: If proxy wallet contract is not deployed
        :raises Exception: If decimals, nonce retrieval or signing fails
        """
        w3: Web3 = create_provider_without_signer(self.network)
        wallet_proxy_address = Web3.to_checksum_address(wallet_proxy_address)

        # -------- addresses --------
        multi_send_address = PREPARE_APPROVE_TOKEN[self.network]["MULTI_SEND"]
        conditional_tokens_address = PREPARE_APPROVE_TOKEN[self.network][
            "CONDITIONAL_TOKENS"
        ]
        ctf_exchange_address = PREPARE_APPROVE_TOKEN[self.network]["CTF_EXCHANGE"]
        pc_token_address = PREPARE_APPROVE_TOKEN[self.network]["PC_TOKEN"]

        conditional_token_abi = load_abi("ConditionalTokens.abi.json")
        pc_token_abi = load_abi("PCToken.abi.json")
        gnosis_safe_abi = load_abi("GnosisSafe.abi.json")

        # -------- contracts --------
        conditional_tokens = w3.eth.contract(
            address=conditional_tokens_address,
            abi=conditional_token_abi,
        )

        pc_token = w3.eth.contract(
            address=pc_token_address,
            abi=pc_token_abi,
        )

        gnosis_safe = w3.eth.contract(
            address=wallet_proxy_address,
            abi=gnosis_safe_abi,
        )

        # -------- decimals --------
        try:
            decimals = pc_token.functions.decimals().call()
        except Exception as e:
            logger.error("Failed to get decimals, fallback to 18", exc_info=e)
            decimals = 18

        amount_wei = int(Decimal(buy_amount) * (10**decimals))

        # -------- build approve multisend --------
        approve_token_data = await self._build_approve_token_data(
            proxy_wallet_address=wallet_proxy_address,
            ctf_exchange_address=ctf_exchange_address,
            pc_amount=amount_wei,
            conditional_tokens=conditional_tokens,
            pc_token=pc_token,
        )

        if approve_token_data is None:
            logger.info("Nothing to approve, skipping")
            return None

        # -------- check proxy wallet deployed --------
        code = w3.eth.get_code(wallet_proxy_address)
        if code in (b"", b"\x00"):
            raise ValueError("No contract deployed at proxy wallet address")

        # -------- nonce --------
        try:
            nonce = gnosis_safe.functions.nonce().call()
        except Exception as e:
            logger.error("Failed to get nonce", exc_info=e)
            raise

        # -------- chain id --------
        chain_id = PREPARE_ACTIVE_PROXY[self.network]["CHAIN_ID"]

        # -------- sign safe tx --------
        signature = self._sign_proxy_wallet_transaction(
            signer=signer,
            contract_address=wallet_proxy_address,
            chain_id=chain_id,
            to=multi_send_address,
            value=0,
            data=approve_token_data,
            nonce=nonce,
            operation=1,  # DELEGATE_CALL
        )

        return TokenApprovalResponse(
            signature=signature,
            data_sign={
                "to": multi_send_address,
                "value": 0,
                "data": approve_token_data,
                "operation": 1,
                "nonce": nonce,
            },
            wallet_proxy=wallet_proxy_address,
        )

    def get_user(self, access_token: str) -> UserProfile:
        """
        Retrieves the authenticated user's profile information.

        :param access_token: JWT access token
        :return: User profile data
        :raises RuntimeError: If the request fails or an unexpected error occurs
        """
        endpoint = ENDPOINTS[self.network]["USER_PROFILE"]

        try:
            data = self._get(
                endpoint,
                headers=self._headers(access_token=access_token),
            )
            
            return AccountMapper.map_user(data)

        except requests.HTTPError as e:
            logger.exception("Failed to fetch user profile")
            raise RuntimeError("Failed to fetch user profile") from e

        except Exception as e:
            logger.exception("Unexpected error in get_user")
            raise RuntimeError("Unexpected error while fetching user profile") from e
