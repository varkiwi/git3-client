from .provider import get_web3_provider

import json
import pkg_resources

GIT_FACTORY_ADDRESS = '0x5545fc8e2cc3815e351E37C6F2f372e2A878E364'

def read_contract_abi(contractName):
    """
    Takes a contract name and returns the abi of the smart contract

    contractName: the name of the Smart Contract for which the abi should be loaded

    returns: abi
    """
    if contractName == "GitFactory" or contractName == "GitRepository":
        path = f"../artifacts/contracts/{contractName}.sol/{contractName}.json"
    else:
        path = f"../artifacts/contracts/facets/{contractName}.sol/{contractName}.json"
    
    contract_data = pkg_resources.resource_string(__name__, path)
    data = json.loads(contract_data) 

    return data['abi']

def get_factory_contract():
    """
    Returns a GitFactory Web3 Contract object

    returns: Web3 Contract object for GitFactory
    """
    w3 = get_web3_provider()
    abi = read_contract_abi("GitFactory")
    return w3.eth.contract(address=GIT_FACTORY_ADDRESS, abi=abi)

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