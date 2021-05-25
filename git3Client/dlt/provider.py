from web3 import Web3

from git3Client.config.config import RPC_ADDRESS


def get_web3_provider():
    """
    Returns a web3 provider.
    """    
    return Web3(Web3.HTTPProvider(RPC_ADDRESS))