#!/usr/bin/env python3
"""Implement just enough git to commit and push to GitHub.

Read the story here: http://benhoyt.com/writings/pygit/

Released under a permissive MIT license (see LICENSE.txt).
"""
from web3 import Web3
from eth_account import Account
from getpass import getpass
from pathlib import Path
from Crypto.PublicKey import ECC

import argparse, collections, difflib, enum, hashlib, operator, os, stat
import struct, sys, time, urllib.request, zlib
import shutil
import ipfshttpclient
import binascii
import itertools
import re
import requests

# Data for one entry in the git index (.git/index)
IndexEntry = collections.namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode', 'uid',
    'gid', 'size', 'sha1', 'flags', 'path',
])

# mode of the file 33188 -> o100644 
# 100644 is a normal file in git
GIT_NORMAL_FILE_MODE = 33188
GIT_TREE_MODE = 16384


MUMBAI_GAS_STATION='https://gasstation-mumbai.matic.today'
# this is mumbai testnet
# CHAINID=80001
# RPC_ADDRESS = 'https://rpc-mumbai.matic.today'
# GIT_FACTORY_ADDRESS = '0x6AB62795EC9BD442461319E2113d21c1Ba278a71'

# this is matic mainnet
CHAINID=137
RPC_ADDRESS = 'https://rpc-mainnet.maticvigil.com/v1/f632570838c8d7c5e5c508c6f24a0e23eabac8c7'
GIT_FACTORY_ADDRESS = '0x5DD6E7D5F20a3ae586cFf4a03A54e51c32F02541'

IPFS_CONNECTION = '/dns4/ipfs.infura.io/tcp/5001/https'
FACTORY_ABI = '''
[
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "NewRepositoryCreated",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "activeRepository",
		"outputs": [
			{
				"internalType": "bool",
				"name": "isActive",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "index",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "collectTips",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_repoName",
				"type": "string"
			}
		],
		"name": "createRepository",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_repoName",
				"type": "string"
			}
		],
		"name": "getRepositoriesUserList",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "",
				"type": "address[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getRepositoryNames",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_owner",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_repoName",
				"type": "string"
			}
		],
		"name": "getUserRepoNameHash",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_owner",
				"type": "address"
			}
		],
		"name": "getUsersRepositories",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_owner",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_repoName",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_userIndex",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_repoIndex",
				"type": "uint256"
			}
		],
		"name": "removeRepository",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "reposUserList",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "repositoryList",
		"outputs": [
			{
				"internalType": "bool",
				"name": "isActive",
				"type": "bool"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "contract GitRepository",
				"name": "location",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "repositoryNames",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "tips",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "usersRepoList",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	}
]
'''

REPOSITORY_ABI = '''
[
	{
		"inputs": [
			{
				"internalType": "contract GitFactory",
				"name": "_factory",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "_owner",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_userIndex",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_repoIndex",
				"type": "uint256"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "Cid",
				"type": "string"
			}
		],
		"name": "NewIssue",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "branch",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "Cid",
				"type": "string"
			}
		],
		"name": "NewPush",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "tipper",
				"type": "address"
			}
		],
		"name": "ReceivedTip",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "branchNames",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "branches",
		"outputs": [
			{
				"internalType": "bool",
				"name": "isActive",
				"type": "bool"
			},
			{
				"internalType": "string",
				"name": "headCid",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "collectTips",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "deleteRepository",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "factory",
		"outputs": [
			{
				"internalType": "contract GitFactory",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getBranchNames",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "issues",
		"outputs": [
			{
				"internalType": "string",
				"name": "cid",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "bounty",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "branch",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "newCid",
				"type": "string"
			}
		],
		"name": "push",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "repoName",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "tips",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_newRepoIndex",
				"type": "uint256"
			}
		],
		"name": "updateRepoIndex",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_newUserIndex",
				"type": "uint256"
			}
		],
		"name": "updateUserIndex",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	}
]
'''

#used as global ipfshttpclient
client = None

class NoRepositoryError(Exception):
    """
    Exception raised for not finding a .git folder.

    Attributes:
        message -- Error message
    """
    def __init__(self, message):
        self.message = message

class ObjectType(enum.Enum):
    """Object type enum. There are other types too, but we don't need them.
    See "enum object_type" in git's source (git/cache.h).
    """
    commit = 1
    tree = 2
    blob = 3


def read_file(path):
    """Read contents of file at given path as bytes."""
    with open(path, 'rb') as f:
        return f.read()


def write_file(path, data):
    """Write data bytes to file at given path."""
    with open(path, 'wb') as f:
        f.write(data)


def init(repo):
    """
    Create .git directory for repository and fill with directories and files.
    """
    if os.path.exists(os.path.join(repo, '.git')):
        print('.git folder exists already')
        return

    cwd = os.getcwd()
    if repo != '.':
        os.mkdir(repo)
        repoName = repo
        fullPath = cwd + '/' + repo
    else:
        repoName = cwd.split('/')[-1]
        fullPath = cwd

    os.mkdir(os.path.join(repo, '.git'))
    # create necessary directories
    for name in ['objects', 'refs', 'refs/heads']:
        os.mkdir(os.path.join(repo, '.git', name))
    write_file(os.path.join(repo, '.git', 'HEAD'), b'ref: refs/heads/master')

    # write the name of the repository into a file
    write_file(os.path.join(repo, '.git', 'name'), str.encode(repoName))
        
    print('Initialized empty Git3 repository in: {}/.git/'.format(fullPath))


def hash_object(data, obj_type, write=True):
    """Compute hash of object data of given type and write to object store if
    "write" is True. Return SHA-1 object hash as hex string.
    """
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        raise NoRepositoryError(nre)
    header = '{} {}'.format(obj_type, len(data)).encode()
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    if write:
        path = os.path.join(repo_root_path, '.git', 'objects', sha1[:2], sha1[2:])
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, zlib.compress(full_data))
    return sha1


def find_object(sha1_prefix):
    """Find object with given SHA-1 prefix and return path to object in object
    store, or raise ValueError if there are no objects or multiple objects
    with this prefix.
    """
    if len(sha1_prefix) < 2:
        raise ValueError('hash prefix must be 2 or more characters')
    repo_root_path = get_repo_root_path()
    obj_dir = os.path.join(repo_root_path, '.git', 'objects', sha1_prefix[:2])
    rest = sha1_prefix[2:]
    objects = [name for name in os.listdir(obj_dir) if name.startswith(rest)]
    if not objects:
        raise ValueError('object {!r} not found'.format(sha1_prefix))
    if len(objects) >= 2:
        raise ValueError('multiple objects ({}) with prefix {!r}'.format(
                len(objects), sha1_prefix))
    return os.path.join(obj_dir, objects[0])


def read_object(sha1_prefix):
    """Read object with given SHA-1 prefix and return tuple of
    (object_type, data_bytes), or raise ValueError if not found.
    """
    path = find_object(sha1_prefix)
    full_data = zlib.decompress(read_file(path))
    nul_index = full_data.index(b'\x00')
    header = full_data[:nul_index]
    obj_type, size_str = header.decode().split()
    size = int(size_str)
    data = full_data[nul_index + 1:]
    assert size == len(data), 'expected size {}, got {} bytes'.format(
            size, len(data))
    return (obj_type, data)


def cat_file(mode, sha1_prefix):
    """Write the contents of (or info about) object with given SHA-1 prefix to
    stdout. If mode is 'commit', 'tree', or 'blob', print raw data bytes of
    object. If mode is 'size', print the size of the object. If mode is
    'type', print the type of the object. If mode is 'pretty', print a
    prettified version of the object.
    """
    obj_type, data = read_object(sha1_prefix)
    if mode in ['commit', 'tree', 'blob']:
        if obj_type != mode:
            raise ValueError('expected object type {}, got {}'.format(
                    mode, obj_type))
        sys.stdout.buffer.write(data)
    elif mode == 'size':
        print(len(data))
    elif mode == 'type':
        print(obj_type)
    elif mode == 'pretty':
        if obj_type in ['commit', 'blob']:
            sys.stdout.buffer.write(data)
        elif obj_type == 'tree':
            for mode, path, sha1 in read_tree(data=data):
                type_str = 'tree' if stat.S_ISDIR(mode) else 'blob'
                print('{:06o} {} {}\t{}'.format(mode, type_str, sha1, path))
        else:
            assert False, 'unhandled object type {!r}'.format(obj_type)
    else:
        raise ValueError('unexpected mode {!r}'.format(mode))

def __get_value_from_config_file(key):
    """
    Reads the values from the git config file and returns the value for the given key
    Key can be: email, name or IdentityFile
    """
    # we are going to check if there is a config file in the repo.
    root_path = get_repo_root_path()
    config_path = '{}/.git/config'.format(root_path)
    if not os.path.isfile(config_path):
        # if not, use the global config file
        config_path = '~/.gitconfig'
    try:
        content = read_file(os.path.expanduser(config_path))
    except FileNotFoundError:
        print('No config file found. Please setup a local config or ~/.gitconfig file.')
        sys.exit(1)
    splitted_config = content.decode().split('\n')
    user = False
    for entry in splitted_config:
        if entry == '[user]':
            user = True
        elif entry.startswith('['):
            user = False
        elif user:
            entry = entry.replace('\t', '')
            entry = entry.strip()
            if entry.startswith(key):
                return entry.split('=')[1].strip()

def __read_private_key():
    """
    Reads the private key from a (ebcrypted) pem file and returns it
    """
    identity_file_path = __get_value_from_config_file('IdentityFile')
    content = read_file(os.path.expanduser(identity_file_path))
    password = ''
    try:
        key = ECC.import_key(content)
    except ValueError as ve:
        if str(ve) == 'PEM is encrypted, but no passphrase available':
            password = input('Password to decrypt PEM file is required: ')
        else:
            print('Unable to load private key')
            sys.exit(1)
    try:
        key = ECC.import_key(content, password)
    except ValueError as ve:
        print('Unable to decrypt PEM file. Password is incorrect')
        sys.exit(1)
    return hex(key.d)[2:]


def __get_current_gas_price():
    """
    Gets the current standard gas price for the network
    """
    print('Getting current gas price')
    return requests.get(MUMBAI_GAS_STATION).json()['standard']

def __get_user_dlt_address():
    print('Getting users web3 address')
    private_key = __read_private_key()
    acct = Account.privateKeyToAccount(private_key)
    return acct.address


def create():
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    w3 = get_web3_provider()
    
    if repo_name == '':
        print('There is no repository name.')
        return
    #TODO: before creating tx and so on, check if this kind of repo exits already :)
    user_address = __get_user_dlt_address()
    nonce = w3.eth.getTransactionCount(user_address)
    print('User address', user_address)
    gas_price = __get_current_gas_price()
    # get current gas price
    print('Preparing transaction to create repository {}'.format(repo_name))
    create_repo_tx = git_factory.functions.createRepository(repo_name).buildTransaction({
        'chainId': CHAINID,
        'gas': 1947750,
        'gasPrice': w3.toWei(gas_price, 'gwei'),
        'nonce': nonce,
    })
    priv_key = bytes.fromhex(__read_private_key())

    print('Signing transaction')
    signed_txn = w3.eth.account.sign_transaction(create_repo_tx, private_key=priv_key)

    print('Sending transaction')
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    #TODO: print a clickable link to blockexplorer
    print('Transaction hash {}'.format(binascii.hexlify(receipt['transactionHash']).decode()))
    if receipt['status']:
        print('Repository {:s} has been created'.format(repo_name))
    else:
        print('Creating {:s} repository failed'.format(repo_name))

def get_web3_provider():
    """
    Returns a web3 provider.
    """    
    return Web3(Web3.HTTPProvider(RPC_ADDRESS))

def get_remote_cid_history():
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    git_repo_address = git_factory.functions.gitRepositories(repo_name).call()
    repo_contract = get_repository_contract(git_repo_address)
    return repo_contract.functions.getCidHistory().call()

def push_new_cid(cid):
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    user_address = __get_user_dlt_address()

    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    repository = git_factory.functions.repositoryList(user_key).call()

    git_repo_address = repository[2]
    repo_contract = get_repository_contract(git_repo_address)
    w3 = get_web3_provider()

    # user_address = __get_user_dlt_address()
    nonce = w3.eth.getTransactionCount(user_address)

    gas_price = __get_current_gas_price()
    create_push_tx = repo_contract.functions.push('main', cid).buildTransaction({
        'chainId': CHAINID,
        'gas': 746427,
        'gasPrice': w3.toWei(gas_price, 'gwei'),
        'nonce': nonce,
    })
    priv_key = bytes.fromhex(__read_private_key())
    print('Signing transaction')
    signed_txn = w3.eth.account.sign_transaction(create_push_tx, private_key=priv_key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('Transaction hash {}'.format(binascii.hexlify(receipt['transactionHash']).decode()))
    if receipt['status']:
        print('Successfully pushed')
    else:
        print('Pushing failed')


def write_commit(commit_object, repo_name):
    author = '{} {}'.format(commit_object['author']['name'], commit_object['author']['email'])
    author_time = '{} {}'.format(commit_object['author']['date_seconds'], commit_object['author']['date_timestamp'])

    committer = '{} {}'.format(commit_object['committer']['name'], commit_object['committer']['email'])
    committer_time = '{} {}'.format(commit_object['committer']['date_seconds'], commit_object['committer']['date_timestamp'])
    lines = []
    
    tree_obj = client.get_json(commit_object['tree'])
    lines = ['tree ' + tree_obj['sha1']]
    if commit_object['parents']:
        for parent in commit_object['parents']:
            parent_obj = client.get_json(parent)
            remote_commit_sha1 = parent_obj['sha1']
            lines.append('parent ' + remote_commit_sha1)
    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(committer, committer_time))
    lines.append('')
    lines.append(commit_object['commit_message'])
    lines.append('')
    data = '\n'.join(lines).encode()
    header = '{} {}'.format('commit', len(data)).encode()
    full_data = header + b'\x00' + data

    path = os.path.join(repo_name, '.git', 'objects', commit_object['sha1'][:2], commit_object['sha1'][2:])
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_file(path, zlib.compress(full_data))


def get_all_remote_commits(commit_cid, repo_name):
    """
    Gets all remote commits and returns those in a list
    """
    all_commits = []
    remote_object = client.get_json(commit_cid)
    all_commits.append(remote_object)
    while len(remote_object['parents']) > 0:
        for parent in remote_object['parents']:
            remote_object = client.get_json(parent)
            all_commits.append(remote_object)
    return all_commits

def unpack_files_of_tree(repo_name, path_to_write, tree, unpack_blobs):
    """
    Gets a tree object and unpacks the references. The content of the blobs are written into a file if unpack_blobs
    is set true. Otherwise only the git objects are created
    """
    tree_entries = []
    for entry in tree['entries']:
        if entry['mode'] == GIT_NORMAL_FILE_MODE:
            blob = client.get_json(entry['cid'])
            # write content to the file if wanted
            if unpack_blobs:
                path = os.path.join(path_to_write, entry['name'])
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                write_file(path, blob['content'].encode())
            # time to create blob object if doesn't exists yet
            path = os.path.join(repo_name, '.git', 'objects', blob['sha1'][:2], blob['sha1'][2:])
            if not os.path.exists(path):
                header = '{} {}'.format('blob', len(blob['content'])).encode()
                full_data = header + b'\x00' + blob['content'].encode()
                os.makedirs(os.path.dirname(path), exist_ok=True)
                write_file(path, zlib.compress(full_data))
            # creating entry for tree object
            mode_path = '{:o} {}'.format(GIT_NORMAL_FILE_MODE, entry['name']).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(blob['sha1'])
            tree_entries.append(tree_entry)
        elif entry['mode'] == GIT_TREE_MODE:
            sub_tree = client.get_json(entry['cid'])
            unpack_files_of_tree(repo_name, "{}/{}".format(path_to_write, entry['name']), sub_tree, unpack_blobs)
            mode_path = '{:o} {}'.format(GIT_TREE_MODE, entry['name']).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(sub_tree['sha1'])
            tree_entries.append(tree_entry)

    data = b''.join(tree_entries)
    obj_type = 'tree'
    header = '{} {}'.format(obj_type, len(data)).encode()
    full_data = header + b'\x00' + data
    path = os.path.join(repo_name, '.git', 'objects', tree['sha1'][:2], tree['sha1'][2:])
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_file(path, zlib.compress(full_data))
            

def unpack_files_of_commit(repo_name, commit_object, unpack_blobs):
    """
    Takes a commit object and unpacks the trees. Might also unpack blob if the unpack_blobs parameter is set to true.
    repo_name is used in order to know where to find the .git directory and the path to write is used to unpack blobs
    and write the content into a file. Commit_object has to be of the ipfs structure.
    """
    write_commit(commit_object, repo_name)
    tree = client.get_json(commit_object['tree'])
    unpack_files_of_tree(repo_name, repo_name, tree, unpack_blobs)


def clone(repo_name):
    """
    Cloning a remote repository on the local machine.

    repo_name: Repository to be cloned
    """
    # 0x0539E6a1093a359C5720d053DB5e3D277F1762B6/mumbaiTestRepo
    user_address, repo_name = repo_name.split('/')

    git_factory = get_factory_contract()
    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    repository = git_factory.functions.repositoryList(user_key).call()

    if not repository[0] or repository[1] != repo_name:
        print('No such repository')
        return
    git_repo_address = repository[2]
    repo_contract = get_repository_contract(git_repo_address)
    branch = repo_contract.functions.branches('main').call()
    headCid = branch[1]

    print('Cloning {:s}'.format(repo_name))
    # initialize repository
    init(repo_name)
    # get all remote commits
    all_commits = get_all_remote_commits(headCid, repo_name)
    #unpack files from the newest commit
    first = True
    for commit in all_commits:
        unpack_files_of_commit(repo_name, commit, first)
        first = False
    # write to refs
    master_path = os.path.join(repo_name, '.git', 'refs', 'heads', 'master')
    write_file(master_path, (all_commits[0]['sha1'] + '\n').encode())
    #chaning into repo, also for add function, in order to find the index file
    os.chdir(repo_name)
    # collecting all files from the repo in order to create the index file
    files_to_add = []
    for path, subdirs, files in os.walk('.'):
        for name in files:
            # we don't want to add the files under .git to the index
            if not path.startswith('./.git'):
                files_to_add.append(os.path.join(path, name)[2:])
    add(files_to_add)
    print('{:s} cloned'.format(repo_name))
    
def get_factory_contract():
    w3 = get_web3_provider()
    return w3.eth.contract(address=GIT_FACTORY_ADDRESS, abi=FACTORY_ABI)

def get_repository_contract(address):
    w3 = get_web3_provider()
    return w3.eth.contract(address=address, abi=REPOSITORY_ABI)

def check_if_repo_created():
    """
    Checks if the repository has been already registered in the gitFactory contract
    If it hasn't, False is returned, otherwise True
    """
    repo_name = read_repo_name()
    w3 = get_web3_provider()
    if not w3.isConnected():
        #TODO: Throw an exception
        print('No connection. Establish a connection first')
        return False
    git_factory = get_factory_contract()
    user_address = __get_user_dlt_address()
    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    repository = git_factory.functions.repositoryList(user_key).call()
    return repository[0]
        
def read_repo_name():
    """Read the repoName file and return the name"""
    repo_root_path = get_repo_root_path()
    try:
        data = read_file(os.path.join(repo_root_path, '.git', 'name'))
    except FileNotFoundError:
        return ""
    return data.rstrip().decode('ascii')

def read_index():
    """Read git index file and return list of IndexEntry objects."""
    try:
        repo_root_path = get_repo_root_path()
        data = read_file(os.path.join(repo_root_path, '.git', 'index'))
    except FileNotFoundError:
        return []
    except NoRepositoryError as nre:
        raise NoRepositoryError(nre)
    digest = hashlib.sha1(data[:-20]).digest()
    assert digest == data[-20:], 'invalid index checksum'
    signature, version, num_entries = struct.unpack('!4sLL', data[:12])
    assert signature == b'DIRC', \
            'invalid index signature {}'.format(signature)
    assert version == 2, 'unknown index version {}'.format(version)
    entry_data = data[12:-20]
    entries = []
    i = 0
    while i + 62 < len(entry_data):
        fields_end = i + 62
        fields = struct.unpack('!LLLLLLLLLL20sH', entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields + (path.decode(),)))
        print(entry)
        entries.append(entry)
        entry_len = ((62 + len(path) + 8) // 8) * 8
        i += entry_len
    assert len(entries) == num_entries
    return entries


def ls_files(details=False):
    """Print list of files in index (including mode, SHA-1, and stage number
    if "details" is True).
    """
    for entry in read_index():
        if details:
            stage = (entry.flags >> 12) & 3
            print('{:6o} {} {:}\t{}'.format(
                    entry.mode, entry.sha1.hex(), stage, entry.path))
        else:
            print(entry.path)


def get_status():
    """
    Get status of working copy, return tuple of
    (changed_paths, new_paths, deleted_paths).
    """
    paths = set()
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:
            path = os.path.join(root, file)
            path = path.replace('\\', '/')
            if path.startswith('./'):
                path = path[2:]
            paths.add(path)
    entries_by_path = {e.path: e for e in read_index()}
    entry_paths = set(entries_by_path)
    changed = {p for p in (paths & entry_paths)
               if hash_object(read_file(p), 'blob', write=False) !=
                  entries_by_path[p].sha1.hex()}
    new = paths - entry_paths
    deleted = entry_paths - paths
    return (sorted(changed), sorted(new), sorted(deleted))


def status():
    """Show status of working copy."""
    changed, new, deleted = get_status()
    if changed:
        print('changed files:')
        for path in changed:
            print('   ', path)
    if new:
        print('new files:')
        for path in new:
            print('   ', path)
    if deleted:
        print('deleted files:')
        for path in deleted:
            print('   ', path)


def diff():
    """Show diff of files changed (between index and working copy)."""
    changed, _, _ = get_status()
    entries_by_path = {e.path: e for e in read_index()}
    for i, path in enumerate(changed):
        sha1 = entries_by_path[path].sha1.hex()
        obj_type, data = read_object(sha1)
        assert obj_type == 'blob'
        index_lines = data.decode().splitlines()
        working_lines = read_file(path).decode().splitlines()
        diff_lines = difflib.unified_diff(
                index_lines, working_lines,
                '{} (index)'.format(path),
                '{} (working copy)'.format(path),
                lineterm='')
        for line in diff_lines:
            print(line)
        if i < len(changed) - 1:
            print('-' * 70)


def write_index(entries):
    """Write list of IndexEntry objects to git index file."""
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        raise NoRepositoryError(nre)
    packed_entries = []

    for entry in entries:
        entry_head = struct.pack('!LLLLLLLLLL20sH',
                entry.ctime_s, entry.ctime_n, entry.mtime_s, entry.mtime_n,
                entry.dev, entry.ino & 0xFFFFFFFF, entry.mode, entry.uid, entry.gid,
                entry.size, entry.sha1, entry.flags)
        path = entry.path.encode()
        length = ((62 + len(path) + 8) // 8) * 8
        packed_entry = entry_head + path + b'\x00' * (length - 62 - len(path))
        packed_entries.append(packed_entry)
    header = struct.pack('!4sLL', b'DIRC', 2, len(entries))
    all_data = header + b''.join(packed_entries)
    digest = hashlib.sha1(all_data).digest()
    write_file(os.path.join(repo_root_path, '.git', 'index'), all_data + digest)
    

def get_repo_root_path():
    """
    Finds the root path of the repository where the .git folder resides and returns the path.
    If no .git folder is found, returns False
    """
    path_to_test = Path(os.getcwd())
    contains_git_folder = os.path.isdir(str(path_to_test) + '/.git')
    if contains_git_folder:
        return str(path_to_test)
    parent = 0
    while not contains_git_folder and str(path_to_test.parents[parent]) != '/':
        contains_git_folder = os.path.isdir(str(path_to_test.parents[parent]) + '/.git')
        if contains_git_folder:
            break
        parent += 1
    if contains_git_folder:
        return str(path_to_test.parents[parent])
    raise NoRepositoryError('fatal: not a git repository (or any of the parent directories): .git')


def add(paths):
    """Add all file paths to git index."""
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)

    paths = [p.replace('\\', '/') for p in paths]
    all_entries = []
    # transfer paths to relative paths. Relative to the repository root
    # in case we are in a subdirectory and add a file
    paths = list(map(lambda path: os.path.relpath(os.path.abspath(path), repo_root_path), paths))

    try:
        all_entries = read_index()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)

    entries = [e for e in all_entries if e.path not in paths]
    for path in paths:
        file_path = repo_root_path + '/' + path
        try:
            data = read_file(file_path)
        except FileNotFoundError:
            print('fatal: pathspec \'{}\' did not match any files'.format(path))
            return
        sha1 = hash_object(data, 'blob')
        st = os.stat(file_path)
        #TODO: We will need to check for the file mode properly!
        mode = GIT_NORMAL_FILE_MODE
        flags = len(file_path.encode())
        assert flags < (1 << 12)
        # gets the relative path to the repository root folder for the index file
        relative_path = os.path.relpath(os.path.abspath(file_path), repo_root_path)
        entry = IndexEntry(
                int(st.st_ctime), 0, int(st.st_mtime), 0, st.st_dev,
                st.st_ino, mode, st.st_uid, st.st_gid, st.st_size,
                bytes.fromhex(sha1), flags, relative_path)
        entries.append(entry)
    entries.sort(key=operator.attrgetter('path'))
    write_index(entries)


def write_tree():
    """Write a tree object from the current index entries."""
    tree_entries = []
    tree_to_process = {'.': []}
    indexEntries = read_index()

    for entry in indexEntries:
        # we are going to create a dict, where the repo hierarchy is shown and used 
        # to create the git objects
        splitted_path = entry.path.split('/')
        filename = splitted_path.pop()
        if len(splitted_path) == 0:
            tree_to_process['.'].append(entry)
        else:
            previous = '.'
            for dir_name in splitted_path:
                if previous in tree_to_process:
                    if dir_name not in tree_to_process[previous]:
                        tree_to_process[previous].append(dir_name)
                else:
                    tree_to_process[previous] = [dir_name]
                previous = dir_name
            if previous in tree_to_process:
                tree_to_process[previous].append(entry)
            else:
                tree_to_process[previous] = [entry]

    for entry in tree_to_process['.']:
        if isinstance(entry, IndexEntry):
            mode_path = '{:o} {}'.format(entry.mode, entry.path).encode()
            tree_entry = mode_path + b'\x00' + entry.sha1
        elif isinstance(entry, str):
            tree_hash = __write_subtree(tree_to_process, entry)
            mode_path = '{:o} {}'.format(GIT_TREE_MODE, entry).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(tree_hash)

        tree_entries.append(tree_entry)
    return hash_object(b''.join(tree_entries), 'tree')

def __write_subtree(indexEntries, dirName):
    """
    Create a subtree for a subdirectories which is going to be added to the normal tree
    """
    tree_entries = []
    for entry in indexEntries[dirName]:
        if isinstance(entry, IndexEntry):
            mode_path = '{:o} {}'.format(entry.mode, entry.path.split('/')[-1]).encode()
            tree_entry = mode_path + b'\x00' + entry.sha1
        elif isinstance(entry, str):
            tree_hash = __write_subtree(indexEntries, entry)
            mode_path = '{:o} {}'.format(GIT_TREE_MODE, entry.split('/')[-1]).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(tree_hash)

        tree_entries.append(tree_entry)
    return hash_object(b''.join(tree_entries), 'tree')

def get_local_master_hash():
    """Get current commit hash (SHA-1 string) of local master branch."""
    repo_root_path = get_repo_root_path()
    master_path = os.path.join(repo_root_path, '.git', 'refs', 'heads', 'master')
    try:
        return read_file(master_path).decode().strip()
    except FileNotFoundError:
        return None


def commit(message, author=None, parent1=None, parent2=None):
    """Commit the current state of the index to master with given message.
    Return hash of commit object.
    """
    # we are working on write tree
    tree = write_tree()
    if parent1 == None:
        parent = get_local_master_hash()
    else:
        parent = parent1

    # check if there is a MERGE_HEAD file. If there is, parent2 is set to the sha1 hash
    merge_head_path = os.path.join(get_repo_root_path(), '.git/MERGE_HEAD')
    if os.path.exists(merge_head_path):
        parent2 = read_file(merge_head_path).decode().strip()

    if author is None:
        user_name = __get_value_from_config_file('name')
        user_email = __get_value_from_config_file('email')
        author = '{} <{}>'.format(user_name, user_email)

    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone
    author_time = '{} {}{:02}{:02}'.format(
            timestamp,
            '+' if utc_offset > 0 else '-',
            abs(utc_offset) // 3600,
            (abs(utc_offset) // 60) % 60)
    lines = ['tree ' + tree]
    if parent:
        lines.append('parent ' + parent)
    if parent2 != None:
        lines.append('parent ' + parent2)
    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(author, author_time))
    lines.append('')
    lines.append(message)
    lines.append('')
    data = '\n'.join(lines).encode()
    sha1 = hash_object(data, 'commit')

    repo_root_path = get_repo_root_path()
    master_path = os.path.join(repo_root_path, '.git', 'refs', 'heads', 'master')
    write_file(master_path, (sha1 + '\n').encode())

    # remove the merge files from the .git directory if committed
    if parent2 != None and os.path.exists(merge_head_path):
        os.remove(merge_head_path)
        merge_mode_path = merge_head_path.replace('MERGE_HEAD', 'MERGE_MODE')
        os.remove(merge_mode_path)
        merge_msg_path = merge_head_path.replace('MERGE_HEAD', 'MERGE_MSG')
        os.remove(merge_msg_path)
    #print('committed to master: {:7}'.format(sha1))
    #TODO: git returns the number of files added and changed. Would be good too
    print('[{} {}] {}'.format('master', sha1[:7], message))
    print('Author: {}'.format(author))
    return sha1


def extract_lines(data):
    """Extract list of lines from given server data."""
    lines = []
    i = 0
    for _ in range(1000):
        line_length = int(data[i:i + 4], 16)
        line = data[i + 4:i + line_length]
        lines.append(line)
        if line_length == 0:
            i += 4
        else:
            i += line_length
        if i >= len(data):
            break
    return lines


def build_lines_data(lines):
    """Build byte string from given lines to send to server."""
    result = []
    for line in lines:
        result.append('{:04x}'.format(len(line) + 5).encode())
        result.append(line)
        result.append(b'\n')
    result.append(b'0000')
    return b''.join(result)


def http_request(url, username, password, data=None):
    """Make an authenticated HTTP request to given URL (GET by default, POST
    if "data" is not None).
    """
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, username, password)
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
    opener = urllib.request.build_opener(auth_handler)
    f = opener.open(url, data=data)
    return f.read()

def get_remote_master_hash():
    """
    Get commit hash of remote master branch, return CID or None if no remote commits.
    """
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    user_address = __get_user_dlt_address()

    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    repository = git_factory.functions.repositoryList(user_key).call()
    
    if not repository[0]:
        print('No such repository')
        return
    git_repo_address = repository[2]
    repo_contract = get_repository_contract(git_repo_address)
    # headCid = repo_contract.functions.headCid().call()
    branch = repo_contract.functions.branches('main').call()
    # check if the branch is active
    if not branch[0]:
        return None
    # if active, return head cid
    return branch[1]

def read_tree(sha1=None, data=None):
    """Read tree object with given SHA-1 (hex string) or data, and return list
    of (mode, path, sha1) tuples.
    """
    if sha1 is not None:
        obj_type, data = read_object(sha1)
        assert obj_type == 'tree'
    elif data is None:
        raise TypeError('must specify "sha1" or "data"')
    i = 0
    entries = []
    for _ in range(1000):
        end = data.find(b'\x00', i)
        if end == -1:
            break
        mode_str, path = data[i:end].decode().split()
        mode = int(mode_str, 8)
        digest = data[end + 1:end + 21]
        entries.append((mode, path, digest.hex()))
        i = end + 1 + 20
    return entries


def find_tree_objects(tree_sha1):
    """Return set of SHA-1 hashes of all objects in this tree (recursively),
    including the hash of the tree itself.
    """
    objects = {tree_sha1}
    for mode, path, sha1 in read_tree(sha1=tree_sha1):
        if stat.S_ISDIR(mode):
            objects.update(find_tree_objects(sha1))
        else:
            objects.add(sha1)
    return objects


def find_commit_objects(commit_sha1):
    """Return set of SHA-1 hashes of all objects in this commit (recursively),
    its tree, its parents, and the hash of the commit itself.
    """
    objects = {commit_sha1}
    obj_type, commit = read_object(commit_sha1)
    assert obj_type == 'commit'
    lines = commit.decode().splitlines()
    tree = next(l[5:45] for l in lines if l.startswith('tree '))
    objects.update(find_tree_objects(tree))
    parents = (l[7:47] for l in lines if l.startswith('parent '))
    for parent in parents:
        objects.update(find_commit_objects(parent))
    return objects


def find_missing_objects(local_sha1, remote_sha1):
    """Return set of SHA-1 hashes of objects in local commit that are missing
    at the remote (based on the given remote commit hash).
    """
    local_objects = find_commit_objects(local_sha1)
    if remote_sha1 is None:
        return local_objects
    remote_objects = find_commit_objects(remote_sha1)
    return local_objects - remote_objects


def encode_pack_object(obj):
    """Encode a single object for a pack file and return bytes (variable-
    length header followed by compressed data bytes).
    """
    obj_type, data = read_object(obj)
    type_num = ObjectType[obj_type].value
    size = len(data)
    byte = (type_num << 4) | (size & 0x0f)
    size >>= 4
    header = []
    while size:
        header.append(byte | 0x80)
        byte = size & 0x7f
        size >>= 7
    header.append(byte)
    return bytes(header) + zlib.compress(data)


def create_pack(objects):
    """Create pack file containing all objects in given given set of SHA-1
    hashes, return data bytes of full pack file.
    """
    header = struct.pack('!4sLL', b'PACK', 2, len(objects))
    body = b''.join(encode_pack_object(o) for o in sorted(objects))
    contents = header + body
    sha1 = hashlib.sha1(contents).digest()
    data = contents + sha1
    return data


def __push_tree(tree_hash, folder_name):
    entries = read_tree(tree_hash)
    tree_entries = []
    for entry in entries:
        if entry[0] == GIT_NORMAL_FILE_MODE:
            obj_type, blob = read_object(entry[2])
            assert obj_type == 'blob'
            blob_to_push = {
                'type': 'blob',
                'content': blob.decode(),
                'sha1': entry[2]
            }
            cid = client.add_json(blob_to_push)
            print('Pushing {} to IPFS'.format(entry[1]))
            tree_entries.append({
                'mode': entry[0],
                'name': entry[1],
                'cid': cid
            })
        elif entry[0] == GIT_TREE_MODE:
            cid = __push_tree(entry[2], entry[1])
            tree_entries.append({
                'mode': entry[0],
                'name': entry[1],
                'cid': cid
            })
    tree_to_push = {
        'type': 'tree',
        'entries': tree_entries,
        'name': folder_name,
        'sha1': tree_hash
    }
    cid = client.add_json(tree_to_push)
    return cid

def __check_if_remote_ahead(remote_sha1):
    """
    Check if the remote repository is ahead. It get's the remote sha1 hash and checks if the file exists in the 
    .git/objects directory. If it does not exist, the remote repository is ahead of the local repository
    """
    if remote_sha1 == None:
        return False
    root_path = get_repo_root_path()
    path_to_check = os.path.join(root_path, '.git', 'objects', remote_sha1[:2], remote_sha1[2:])
    return not os.path.isfile(path_to_check) 

def __push_commit(commit_hash, remote_commit_hash, remote_commit_cid):
    """
    Used to push a commit, the tree it references and the blobs to ipfs. 

    commit_hash - The sha1 hash of the local commit object
    remote_commit_hash - The sha1 hash of the remote commit object. With this we know that we don't have to push that one
    """
    # we don't need to push a commit object if remote sha1 is equal to local sha1 hash
    if commit_hash == remote_commit_hash:
       return remote_commit_cid
    obj_type, commit = read_object(commit_hash)
    assert obj_type == 'commit'
    lines = commit.decode().splitlines()
    commit_to_push = {
        'type': 'commit',
        'parents': [],
        'sha1': commit_hash,
    }
    for line in lines:
        if line.startswith('tree '):
            tree_hash = line[5:45]
            commit_to_push['tree'] = __push_tree(tree_hash, '.')
        elif line.startswith('parent '):
            parent_cid = __push_commit(line[7:47], remote_commit_hash, remote_commit_cid)
            commit_to_push['parents'].append(parent_cid)
        elif line.startswith('author'):
            splitted_line = line.split(' ')
            commit_to_push['author'] = {
                'name': splitted_line[1],
                'email': splitted_line[2],
                'date_seconds': splitted_line[3],
                'date_timestamp': splitted_line[4],
            }
        elif line.startswith('committer'):
            splitted_line = line.split(' ')
            commit_to_push['committer'] = {
                'name': splitted_line[1],
                'email': splitted_line[2],
                'date_seconds': splitted_line[3],
                'date_timestamp': splitted_line[4],
            }
        else:
            if line == '':
                space_commit_message = True
                
            if space_commit_message:
                commit_to_push['commit_message'] = line
    commit_cid = client.add_json(commit_to_push)
    return commit_cid
            
def push():
    """Push master branch to given git repo URL.""" 
    if not check_if_repo_created():
        print('Repository has not been registered yet. Use\n\n`git3 create`\n\nbefore you push')
        return
    local_sha1 = get_local_master_hash()
    remote_cid = get_remote_master_hash()
    if remote_cid != None:
        # since there is already something pushed, we will have to get the remote cid
        remote_commit = client.get_json(remote_cid)
        remote_sha1 = remote_commit['sha1']
    else:
        remote_sha1 = None

    if local_sha1 == remote_sha1:
       print('Everything up-to-date')
       return
    elif __check_if_remote_ahead(remote_sha1):
       print('Remote repository is ahead. Pull the changes first')
       return
    print('Pushing files to IPFS')
    master_cid = __push_commit(local_sha1, remote_sha1, remote_cid)
    if master_cid == remote_cid:
        print('Everything up-to-date')
    else:
        print('Going to write the CID into repository contract')
        push_new_cid(master_cid)

def get_subtree_entries(tree_sha1, path, entries):
    """
    Get's all entries from a tree and writes the path and the hash into entries. 
    """
    tree = read_tree(tree_sha1)
    for entry in tree:
        if entry[0] == GIT_NORMAL_FILE_MODE:
            entries.append((os.path.join(path, entry[1]), entry[2]))
        elif entry[0] == GIT_TREE_MODE:
            get_subtree_entries(entry[2], os.path.join(path, entry[1]), entries)

def is_stage_empty():
    """
    Comapres the entries from the last commit object with the ones in the index file. If there is a difference, 
    the stage is not empty. If there is a difference, the stage is not empty
    """
    local_sha1 = get_local_master_hash()
    obj_type, data = read_object(local_sha1)
    assert obj_type == 'commit'
    splitted_commit = data.decode().splitlines()
    #We want to get the tree hash
    for line in splitted_commit:
        if line.startswith('tree '):
            tree_sha1 = line[5:]
            break
    #so that we can read the top tree object
    committed_entries = []
    get_subtree_entries(tree_sha1, '', committed_entries)
    index = read_index()
    for indexEntry in index:
        # found is used for entries which have not been committed yet. 
        found = False
        for treeEntry in committed_entries:
            if treeEntry[0] == indexEntry.path: 
                if treeEntry[1] != indexEntry.sha1.hex():
                    return False
                found = True
        # if found is false, the entry has not been committed yet and there is a difference between staging and commit
        if not found:
            return False
    return True

def get_all_local_commits(commit_hash):
    """
    Returns a list contains all hashes of the local commits
    """
    all_commits = []
    parents = []
    #local_sha1 = get_local_master_hash()
    all_commits.append(commit_hash)
    obj_type, commit = read_object(commit_hash)
    lines = commit.decode().splitlines()
    for l in lines:
        if l.startswith('parent '):
            parents.append(l[7:47])
    while len(parents) > 0:
        parent = parents.pop()
        all_commits.append(parent)
        obj_type, commit = read_object(parent)
        lines = commit.decode().splitlines()
        for l in lines:
            if l.startswith('parent '):
                parents.append(l[7:47])
    return all_commits

def pull():
    print('Pulling')
    changed, _, _ = get_status()
    # we are checking if there a changed files in the working copy or files staged which have not been committed.
    # if one case is true, pull won't be executed
    if len(changed) > 0 or not is_stage_empty:
        print("You have local changes. Add and commit those first")
        return
    
    repo_name = read_repo_name()
    git_factory = get_factory_contract()
    git_repo_address = git_factory.functions.gitRepositories(repo_name).call()
    if git_repo_address == '0x0000000000000000000000000000000000000000':
        print('No such repository')
        return
    repo_contract = get_repository_contract(git_repo_address)
    headCid = repo_contract.functions.headCid().call()
    
    remote_commits = get_all_remote_commits(headCid, repo_name)
    #extract only the sha1 hash
    remote_commits_sha1 = [e['sha1'] for e in remote_commits]
    print(remote_commits_sha1)

    local_commits = get_all_local_commits()
    print(local_commits)
    if local_commits[0] == remote_commits_sha1[0]:
        print('Already up to date')
        return
    remote_to_local_difference = set(remote_commits_sha1) - set(local_commits)
    local_to_remote_difference = set(local_commits) - set(remote_commits_sha1)
    if len(local_to_remote_difference) == 0:
        print('We can download and unpack all of it :)')
        print(remote_to_local_difference)
    #print(local_to_remote_difference, len(local_to_remote_difference))
    #TODO: get all remote and local commits and get the difference
    #use the difference to know which commits and trees need to be downloaded
    #Go through the most recent commit, get the trees and files and merge those with the local files
    #Go throug all other commits and unpack the commits and trees

def fetch():
    """
    Downloads commits and objects from the remote repository
    """
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    user_address = __get_user_dlt_address()

    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    repository = git_factory.functions.repositoryList(user_key).call()

    if not repository[0]:
        print('No such repository')
        return

    git_repo_address = repository[2]
    repo_contract = get_repository_contract(git_repo_address)

    branch = repo_contract.functions.branches('main').call()
    headCid = branch[1]
    
    remote_commits = get_all_remote_commits(headCid, repo_name)
    #extract only the sha1 hash
    remote_commits_sha1 = [e['sha1'] for e in remote_commits]

    local_sha1 = get_local_master_hash()
    local_commits = get_all_local_commits(local_sha1)
    if local_commits[0] == remote_commits_sha1[0]:
        return
    remote_to_local_difference = set(remote_commits_sha1) - set(local_commits)
    repo_root_path = get_repo_root_path()
    for commit_hash in remote_to_local_difference:
        for commit in remote_commits:
            if commit['sha1'] == commit_hash:
                unpack_files_of_commit(repo_root_path, commit, False)
    data = '{}\t\t{}\'{}\' of {}\n'.format(remote_commits_sha1[0], 'branch ', 'main', git_repo_address).encode()
    path = os.path.join(repo_root_path, '.git', 'FETCH_HEAD')
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    write_file(path, data)
    path = os.path.join(repo_root_path, '.git', 'refs/remote/origin/main')
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    write_file(path, remote_commits_sha1[0].encode())

def __unpack_object(object_hash, repo_path, path_to_write):
    """
    Takes an tress sha1 hash and read the local object. It iterates over the entries and writes the content of blobs
    to the repository. In case it comes across another tree object, it makes a recursive call.
    """
    #TODO: have to make it more robust. What if it is not a tree object?
    entries = read_tree(object_hash)
    for entry in entries:
        if entry[0] == GIT_NORMAL_FILE_MODE:
            object_path = os.path.join(repo_path, '.git/objects', entry[2][:2], entry[2][2:])
            full_data = zlib.decompress(read_file(object_path))
            nul_index = full_data.index(b'\x00')
            header = full_data[:nul_index]
            obj_type, size_str = header.decode().split()
            size = int(size_str)
            data = full_data[nul_index + 1:]
            data_path = os.path.join(path_to_write, entry[1])
            if not os.path.exists(data_path):
                os.makedirs(os.path.dirname(data_path), exist_ok=True)
            write_file(data_path, data)
        elif entry[0] == GIT_TREE_MODE:
            __unpack_object(entry[2], repo_path, os.path.join(path_to_write, entry[1]))
        

def merge():
    """
    Merges two branches. Since we currently support only one branch, merge takes the commit from FETCH_HEAD for now
    """
    repo_root_path = get_repo_root_path()
    fetch_head_path = os.path.join(repo_root_path, '.git', 'FETCH_HEAD')
    if not os.path.exists(fetch_head_path):
        print('Nothing to merge. Have you called fetch before?')
        return
    fetch_head = read_file(fetch_head_path)

    remote_sha1 = fetch_head.decode()[0:40]
    local_sha1 = get_local_master_hash()

    if remote_sha1 == local_sha1:
       return
    remote_commits = get_all_local_commits(remote_sha1)
    local_commits = get_all_local_commits(local_sha1)

    difference = set(local_commits) - set(remote_commits)
    
    if len(difference) == 0:
        #fast forward strategy
        path = os.path.join(repo_root_path, '.git/refs/heads/master')
        write_file(path, "{}\n".format(remote_sha1).encode())
        obj_type, commit_data = read_object(remote_sha1)
        tree_sha1 = commit_data.decode().splitlines()[0][5:45]
        __unpack_object(tree_sha1, repo_root_path, repo_root_path)
        return
    # non fast forward strategy
    intersection = set(local_commits).intersection(remote_commits)
    for commit_hash in remote_commits:
        if commit_hash in intersection:
            ancestor = commit_hash
            break

    # We need to find an ancestor and run 3-way merge on these files!
    # than we need to create a new tree and a commit object with 2 parents
    
    obj_type, ancestor_commit = read_object(ancestor)
    obj_type, a_commit = read_object(local_commits[0])
    obj_type, b_commit = read_object(remote_commits[0])
    # list for the 3 branches
    ancestor_entries = []
    a_entries = []
    b_entries = []
    # here we get a list in the following format [(filename, sha1), (filename, sha2), ...]
    get_subtree_entries(ancestor_commit.splitlines()[0][5:45].decode(), '', ancestor_entries)
    get_subtree_entries(a_commit.splitlines()[0][5:45].decode(), '', a_entries)
    get_subtree_entries(b_commit.splitlines()[0][5:45].decode(), '', b_entries)

    merge = {}
    # wo go through each list and use the filename as key and create a list of hashed
    for e in ancestor_entries:
        if e[0] not in merge:
            merge[e[0]] = [e[1]]

    for e in a_entries:
        if e[0] not in merge:
            merge[e[0]] = [None, e[1]]
        else:
            merge[e[0]].append(e[1])

    for e in b_entries:
        if e[0] not in merge:
            merge[e[0]] = [None, None, e[1]]
        else:
            merge[e[0]].append(e[1])

    # if all hashes are the same, there is nothing we have to do
    # In case the second and third entry are not None, but the first one is: I am not sure if this case actually is possible
    conflict_files = []
    for f in merge:
        if len(merge[f]) == 2 and merge[f][0] != merge[f][1]:
            # if there are only two entries, the remote branch does not have the file and we will add it to the repository
            obj_type, data = read_object(merge[f][1])
            path = os.path.join(repo_root_path, f)
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, data)
        elif merge[f][0] == None and merge[f][1] == None:
            # if there are three entries and the first two entries are none, the local repository does not have the file
            # so we add it.
            obj_type, data = read_object(merge[f][2])
            path = os.path.join(repo_root_path, f)
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, data)
        elif len(set(merge[f])) == 3:
            # all entries are different, so 3-way merge
            # read the content of each file
            obj_type, base_data = read_object(merge[f][0])
            obj_type, local_data = read_object(merge[f][1])
            obj_type, remote_data = read_object(merge[f][2])
            #do the 3-way merge
            had_conflict, merged_lines = three_way_merge(
                base_data.decode().splitlines(),
                local_data.decode().splitlines(),
                remote_data.decode().splitlines(),
                "HEAD",
                merge[f][2]
            )
            # writing the merged lines into the file
            with open(os.path.join(repo_root_path, f), 'w') as file:
                for line in merged_lines:
                    file.write(line)
            if had_conflict:
                # adding file to list, so that we don't add it to the index
                conflict_files.append(f)
                path = os.path.join(repo_root_path, '.git/ORIG_HEAD')
                write_file(path, '{}\n'.format(local_sha1).encode())
                path = os.path.join(repo_root_path, '.git/MERGE_HEAD')
                write_file(path, '{}\n'.format(fetch_head[:40].decode()).encode())
                path = os.path.join(repo_root_path, '.git/MERGE_MODE')
                write_file(path, b'')
                path = os.path.join(repo_root_path, '.git/MERGE_MSG')
                if os.path.exists(path):
                    # append file name to conflict
                    with open(path, 'a') as f:
                        f.write('# \t{}'.format(f))
                else:
                    repo_name = read_repo_name()
                    git_factory = get_factory_contract()
                    git_repo_address = git_factory.functions.gitRepositories(repo_name).call()
                    write_file(path, 'Merge branch \'main\' of {} into main\n\n# Conflicts\n# \t{}\n'.format(git_repo_address, f).encode())

    # adding all the files to the index. TODO: can be more efficient if we add it to the previous loop
    files_to_add = []
    pwd = os.getcwd()
    os.chdir(repo_root_path)
    for path, subdirs, files in os.walk('.'):
        for name in files:
            # we don't want to add the files under .git to the index
            if not path.startswith('./.git') and name not in conflict_files:
                files_to_add.append(os.path.join(path, name)[2:])
    os.chdir(pwd)
    add(files_to_add)
    # creating a commit object with two parents
    if not had_conflict:
        commit('Merging remote into master', parent1=local_commits[0], parent2=remote_commits[0])
    

def drop_inline_diffs(diff):
    r = []
    for t in diff:
        if not t.startswith('?'):
            r.append(t)
    return r

def three_way_merge(x, a, b, conflict_commit_one, conflict_commit_two):
    dxa = difflib.Differ()
    dxb = difflib.Differ()
    xa = drop_inline_diffs(dxa.compare(x, a))
    xb = drop_inline_diffs(dxb.compare(x, b))

    m = []
    index_a = 0
    index_b = 0
    had_conflict = 0

    while (index_a < len(xa)) and (index_b < len(xb)):
        # no changes or adds on both sides
        if (xa[index_a] == xb[index_b] and
            (xa[index_a].startswith('  ') or xa[index_a].startswith('+ '))):
            m.append(xa[index_a][2:])
            index_a += 1
            index_b += 1
            continue

        # removing matching lines from one or both sides
        if ((xa[index_a][2:] == xb[index_b][2:])
            and (xa[index_a].startswith('- ') or xb[index_b].startswith('- '))):
            index_a += 1
            index_b += 1
            continue

        # adding lines in A
        if xa[index_a].startswith('+ ') and xb[index_b].startswith('  '):
            m.append(xa[index_a][2:])
            index_a += 1
            continue

        # adding line in B
        if xb[index_b].startswith('+ ') and xa[index_a].startswith('  '):
            m.append(xb[index_b][2:])
            index_b += 1
            continue

        # conflict - list both A and B, similar to GNU's diff3
        m.append("\n<<<<<<< {}\n".format(conflict_commit_one))
        while (index_a < len(xa)) and not xa[index_a].startswith('  '):
            m.append(xa[index_a][2:])
            index_a += 1
        m.append("\n=======\n")
        while (index_b < len(xb)) and not xb[index_b].startswith('  '):
            m.append(xb[index_b][2:])
            index_b += 1
        m.append("\n>>>>>>> {}\n".format(conflict_commit_two))
        had_conflict = 1

    # append remining lines - there will be only either A or B
    for i in range(len(xa) - index_a):
        m.append(xa[index_a + i][2:])
    for i in range(len(xb) - index_b):
        m.append(xb[index_b + i][2:])

    return had_conflict, m

def connect_to_infura():
    global client
    client = ipfshttpclient.connect(IPFS_CONNECTION)

def close_to_infura():
    global client
    client.close()

# if __name__ == '__main__':
def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command', metavar='command')
    sub_parsers.required = True

    sub_parser = sub_parsers.add_parser('add',
            help='add file(s) to index')
    sub_parser.add_argument('paths', nargs='+', metavar='path',
            help='path(s) of files to add')

    #sub_parser = sub_parsers.add_parser('cat-file',
            #help='display contents of object')
    #valid_modes = ['commit', 'tree', 'blob', 'size', 'type', 'pretty']
    #sub_parser.add_argument('mode', choices=valid_modes,
            #help='object type (commit, tree, blob) or display mode (size, '
                 #'type, pretty)')
    #sub_parser.add_argument('hash_prefix',
            #help='SHA-1 hash (or hash prefix) of object to display')

    sub_parser = sub_parsers.add_parser('commit',
            help='commit current state of index to master branch')
    sub_parser.add_argument('-a', '--author',
            help='commit author in format "A U Thor <author@example.com>" '
                 '(uses GIT_AUTHOR_NAME and GIT_AUTHOR_EMAIL environment '
                 'variables by default)')
    sub_parser.add_argument('-m', '--message', required=True,
            help='text of commit message')

    sub_parser = sub_parsers.add_parser('create',
            help='create your remote repository')
    
    sub_parser = sub_parsers.add_parser('clone',
            help='create your remote repository')    
    sub_parser.add_argument('name',
            help='name of repository to clone')    
    #sub_parser = sub_parsers.add_parser('diff',
            #help='show diff of files changed (between index and working '
                 #'copy)')

    #sub_parser = sub_parsers.add_parser('hash-object',
            #help='hash contents of given path (and optionally write to '
                 #'object store)')
    #sub_parser.add_argument('path',
            #help='path of file to hash')
    #sub_parser.add_argument('-t', choices=['commit', 'tree', 'blob'],
            #default='blob', dest='type',
            #help='type of object (default %(default)r)')
    #sub_parser.add_argument('-w', action='store_true', dest='write',
            #help='write object to object store (as well as printing hash)')

    sub_parser = sub_parsers.add_parser('init',
            help='initialize a new repo')
    sub_parser.add_argument('repo',
            nargs='?',
            default='.',
            help='directory name for new repo')

    #sub_parser = sub_parsers.add_parser('ls-files',
            #help='list files in index')
    #sub_parser.add_argument('-s', '--stage', action='store_true',
            #help='show object details (mode, hash, and stage number) in '
                 #'addition to path')

    sub_parser = sub_parsers.add_parser('fetch',
            help='Download object and refs from another repository')

    sub_parser = sub_parsers.add_parser('merge',
            help='Join two or more development histories together')

    sub_parser = sub_parsers.add_parser('push',
            help='push master branch to given git server URL')
    #sub_parser.add_argument('git_url',
    #        help='URL of git repo, eg: https://github.com/benhoyt/pygit.git')
    #sub_parser.add_argument('-p', '--password',
            #help='password to use for authentication (uses GIT_PASSWORD '
                 #'environment variable by default)')
    #sub_parser.add_argument('-u', '--username',
            #help='username to use for authentication (uses GIT_USERNAME '
                 #'environment variable by default)')

    sub_parser = sub_parsers.add_parser('pull',
            help='pulls remote commits')

    sub_parser = sub_parsers.add_parser('status',
            help='show status of working copy')

    args = parser.parse_args()
    if args.command == 'add':
        add(args.paths)
    elif args.command == 'cat-file':
        try:
            cat_file(args.mode, args.hash_prefix)
        except ValueError as error:
            print(error, file=sys.stderr)
            sys.exit(1)
    elif args.command == 'commit':
        commit(args.message, author=args.author)
    elif args.command == 'create':
        create()
    elif args.command == 'clone':
        connect_to_infura()
        clone(args.name)
        close_to_infura()
    elif args.command == 'diff':
        diff()
    elif args.command == 'fetch':
        connect_to_infura()
        fetch()
        close_to_infura()
    elif args.command == 'hash-object':
        sha1 = hash_object(read_file(args.path), args.type, write=args.write)
        print(sha1)
    elif args.command == 'init':
        init(args.repo)
    elif args.command == 'ls-files':
        ls_files(details=args.stage)
    elif args.command == 'merge':
        merge()
    elif args.command == 'push':
        connect_to_infura()
        # push(args.git_url)
        push()
        close_to_infura()
    elif args.command == 'pull':
        connect_to_infura()
        pull()
        close_to_infura()
    elif args.command == 'status':
        status()
    else:
        assert False, 'unexpected command {!r}'.format(args.command)

if __name__ == '__main__':
    main()