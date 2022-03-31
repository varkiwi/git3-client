from web3 import Web3
import sys

from git3Client.config.config import MUMBAI_RPC_ADDRESS, GODWOKEN_TESTNET_RPC_ADDRESS


def get_web3_provider(network):
    """
    Returns a web3 provider.

    network: the network for which the provider should be loaded
    """
    if network == 'mumbai':
        return Web3(Web3.HTTPProvider(MUMBAI_RPC_ADDRESS))
    elif network == 'godwoken':
        return Web3(Web3.HTTPProvider(GODWOKEN_TESTNET_RPC_ADDRESS))
    else:
        print(f"Network {network} not supported")
        sys.exit(1)
        
    