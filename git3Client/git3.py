#!/usr/bin/env python3

# from eth_account import Account
import argparse
import sys
import ipfshttpclient

from git3Client.exceptions import NoRepositoryError
#from git3Client.gitInternals.gitObject import hash_object

from git3Client.gitCommands.add import add
from git3Client.gitCommands.catFile import cat_file
from git3Client.gitCommands.clone import clone
from git3Client.gitCommands.commit import commit
from git3Client.gitCommands.create import create
from git3Client.gitCommands.diff import diff
from git3Client.gitCommands.fetch import fetch
from git3Client.gitCommands.getAddress import getAddress
from git3Client.gitCommands.hashObject import hashObject
from git3Client.gitCommands.init import init
from git3Client.gitCommands.lsFiles import ls_files
from git3Client.gitCommands.merge import merge
from git3Client.gitCommands.push import push
from git3Client.gitCommands.pull import pull
from git3Client.gitCommands.status import status

from git3Client.utils.utils import read_file

MUMBAI_GAS_STATION='https://gasstation-mumbai.matic.today'
# this is mumbai testnet
CHAINID=80001
# RPC_ADDRESS = 'https://rpc-mumbai.matic.today'
# GIT_FACTORY_ADDRESS = '0x6AB62795EC9BD442461319E2113d21c1Ba278a71'

# this is matic mainnet
#CHAINID=137
RPC_ADDRESS = 'https://rpc-mainnet.maticvigil.com/v1/f632570838c8d7c5e5c508c6f24a0e23eabac8c7'
GIT_FACTORY_ADDRESS = '0x5DD6E7D5F20a3ae586cFf4a03A54e51c32F02541'

IPFS_CONNECTION = '/dns4/ipfs.infura.io/tcp/5001/https'

#used as global ipfshttpclient
client = None

def connect_to_infura():
    global client
    client = ipfshttpclient.connect(IPFS_CONNECTION)
    return client

def close_to_infura():
    global client
    client.close()

def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command', metavar='command')
    sub_parsers.required = True

    sub_parser = sub_parsers.add_parser('add',
            help='add file(s) to index')
    sub_parser.add_argument('paths', nargs='+', metavar='path',
            help='path(s) of files to add')

    sub_parser = sub_parsers.add_parser('cat-file',
            help='display contents of object')
    valid_modes = ['commit', 'tree', 'blob', 'size', 'type', 'pretty']
    sub_parser.add_argument('mode', choices=valid_modes,
            help='object type (commit, tree, blob) or display mode (size, '
                 'type, pretty)')
    sub_parser.add_argument('hash_prefix',
            help='SHA-1 hash (or hash prefix) of object to display')

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

    sub_parser = sub_parsers.add_parser('hash-object',
            help='hash contents of given path (and optionally write to '
                 'object store)')
    sub_parser.add_argument('path',
            help='path of file to hash')
    sub_parser.add_argument('-t', choices=['commit', 'tree', 'blob'],
            default='blob', dest='type',
            help='type of object (default %(default)r)')
    sub_parser.add_argument('-w', action='store_true', dest='write',
            help='write object to object store (as well as printing hash)')

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

    sub_parser = sub_parsers.add_parser('get-address',
            help='Get Matic wallet address')

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
    elif args.command == 'get-address':
        address = getAddress()
        print('Your address is: {}'.format(address))
    elif args.command == 'hash-object':
        hashObject(read_file(args.path), args.type, write=args.write)
    elif args.command == 'init':
        init(args.repo)
    elif args.command == 'ls-files':
        ls_files(details=args.stage)
    elif args.command == 'merge':
        merge()
    elif args.command == 'push':
        connect_to_infura()
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
