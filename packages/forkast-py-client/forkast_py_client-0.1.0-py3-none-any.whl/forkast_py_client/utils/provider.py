import logging
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from forkast_py_client.config.constants import RPC_URLS, Network

logger = logging.getLogger(__name__)


def create_provider_without_signer(network: Network = Network.TESTNET) -> Web3:
    """
    Creates a Web3 provider without attaching a signer.

    :param network: Whether to use mainnet or testnet
    :return: Web3 instance
    """
    try:
        rpc_url = RPC_URLS[network]
        provider = Web3(HTTPProvider(rpc_url))

        if not provider.is_connected():
            raise RuntimeError("Failed to connect to RPC provider")

        return provider

    except Exception:
        logger.exception("Failed to create provider")
        raise
