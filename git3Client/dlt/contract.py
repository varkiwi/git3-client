from .provider import get_web3_provider

from git3Client.config.config import MUMBAI_GIT_FACTORY_ADDRESS, GODWOKEN_TESTNET_GIT_FACTORY_ADDRESS

import json
import os

def read_contract_abi(contractName):
    """
    Takes a contract name and returns the abi of the smart contract

    contractName: the name of the Smart Contract for which the abi should be loaded

    returns: abi
    """
    real_path = os.path.realpath(__file__).split('/')
    real_path[-2] = 'artifacts'
    real_path[-1] = 'contracts'

    if contractName is not "GitFactory" and contractName is not "GitRepository":
        real_path.append('facets')

    abi_path = '/'.join(real_path)

    with open(f"{abi_path}/{contractName}.sol/{contractName}.json", "r") as f:
        data = json.load(f)
    return data['abi']

def get_factory_contract(network):
    """
    Returns a GitFactory Web3 Contract object

    network: the network for which the contract should be loaded

    returns: Web3 Contract object for GitFactory
    """
    w3 = get_web3_provider(network)
    abi = read_contract_abi("GitFactory")
    if network == 'mumbai':
        return w3.eth.contract(address=MUMBAI_GIT_FACTORY_ADDRESS, abi=abi)
    return w3.eth.contract(address=GODWOKEN_TESTNET_GIT_FACTORY_ADDRESS, abi=abi)

def get_repository_contract(address):
    """
    Returns a GitRepository Web3 Contract object

    returns: Web3 Contract object for GitRepository
    """
    w3 = get_web3_provider()
    abi = read_contract_abi("GitRepository")
    return w3.eth.contract(address=address, abi=abi)

def get_facet_contract(contractName, address):
    """
    Returns an ABI for a Smart Contract based on the given parameter

    parameter: contractName - of the Smart Contract the ABI is read for
    parameter: address - address of the smart contract

    returns: Web3 Contract object for Smart Contract based on the given parameter
    """
    w3 = get_web3_provider()
    abi = read_contract_abi(contractName)
    return w3.eth.contract(address=address, abi=abi)