from web3 import Web3

# RPC_ADDRESS = 'https://rpc-mumbai.matic.today'

# RPC_ADDRESS = 'https://rpc-mainnet.maticvigil.com/v1/f632570838c8d7c5e5c508c6f24a0e23eabac8c7'
RPC_ADDRESS = 'https://rpc-mumbai.maticvigil.com/v1/f632570838c8d7c5e5c508c6f24a0e23eabac8c7'

def get_web3_provider():
    """
    Returns a web3 provider.
    """    
    return Web3(Web3.HTTPProvider(RPC_ADDRESS))