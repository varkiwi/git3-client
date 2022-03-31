#!/usr/bin/env python3

import argparse
import sys

from git3Client.gitCommands.add import add
from git3Client.gitCommands.branch import listBranches, createBranch
from git3Client.gitCommands.catFile import cat_file
from git3Client.gitCommands.checkout import checkout
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

def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command', metavar='command')
    sub_parsers.required = True

    # Add
    sub_parser = sub_parsers.add_parser('add',
            help='add file(s) to index')
    sub_parser.add_argument('paths', nargs='+', metavar='path',
            help='path(s) of files to add')

    # Branch
    sub_parser = sub_parsers.add_parser('branch',
            help='List and Create branches')
    sub_parser.add_argument('-r', '--remotes', action='store_true',
            help='act on remote-tracking branches')
    sub_parser = sub_parser.add_argument('branchname', metavar='<branchname>', nargs='?',
            help='Create a new branch named <branchname>')

    # Cat-file
    sub_parser = sub_parsers.add_parser('cat-file',
            help='display contents of object')
    valid_modes = ['commit', 'tree', 'blob', 'size', 'type', 'pretty']
    sub_parser.add_argument('mode', choices=valid_modes,
            help='object type (commit, tree, blob) or display mode (size, '
                 'type, pretty)')
    sub_parser.add_argument('hash_prefix',
            help='SHA-1 hash (or hash prefix) of object to display')

    # Checkout
    sub_parser = sub_parsers.add_parser('checkout',
            help='Switch branches')
    sub_parser.add_argument('-b', action='store_true',
            help='Create a new branch with name new_branch')
    sub_parser.add_argument('branch', metavar='<branch>',
            help='Checkout to <branch>')

    # Commit
    sub_parser = sub_parsers.add_parser('commit',
            help='commit current state of index to current active branch')
    sub_parser.add_argument('-a', '--author',
            help='commit author in format "A U Thor <author@example.com>" '
                 '(uses GIT_AUTHOR_NAME and GIT_AUTHOR_EMAIL environment '
                 'variables by default)')
    sub_parser.add_argument('-m', '--message', required=True,
            help='text of commit message')

    # Create
    sub_parser = sub_parsers.add_parser('create',
            help='create your remote repository')
    valid_networks = ['godwoken', 'mumbai']
    sub_parser.add_argument('-n', '--network', required=True, choices=valid_networks,
            help='Choose which network to interact with. Godwoken Testnet and'
                 ' Mumbai are currently supported.')
    
    # Clone
    sub_parser = sub_parsers.add_parser('clone',
            help='create your remote repository')    
    sub_parser.add_argument('name',
            help='name of repository to clone')

    # Diff
    sub_parser = sub_parsers.add_parser('diff',
            help='show diff of files changed (between index and working '
                 'copy)')
    sub_parser.add_argument('--staged', action='store_true',
            help='This form is to view the changes you staged for the '
            'next commit relative to the HEAD commmit.')

    # Hash-object
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

    # init
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

    # Fetch
    sub_parser = sub_parsers.add_parser('fetch',
            help='Download object and refs from another repository')
    sub_parser.add_argument('branch',
            nargs='?',
            help='branch data to fetch')

    # Get-Address
    sub_parser = sub_parsers.add_parser('get-address',
            help='Get Matic wallet address')

    # Merge
    sub_parser = sub_parsers.add_parser('merge',
            help='Join two or more development histories together')
    sub_parser.add_argument('sourceBranch',
            nargs='?',
            help='branch to be merged into the current branch')

    # Push
    sub_parser = sub_parsers.add_parser('push',
            help='push current active branch to given git server URL')
    #sub_parser.add_argument('git_url',
    #        help='URL of git repo, eg: https://github.com/benhoyt/pygit.git')
    #sub_parser.add_argument('-p', '--password',
            #help='password to use for authentication (uses GIT_PASSWORD '
                 #'environment variable by default)')
    #sub_parser.add_argument('-u', '--username',
            #help='username to use for authentication (uses GIT_USERNAME '
                 #'environment variable by default)')

    # Pull
    sub_parser = sub_parsers.add_parser('pull',
            help='pulls remote commits')

    # Status
    sub_parser = sub_parsers.add_parser('status',
            help='show status of working copy')

    args = parser.parse_args()
    if args.command == 'add':
        add(args.paths)
    elif args.command == 'branch':
        if args.branchname:
            createBranch(args.command, args.branchname)
        else:
            listBranches(args.remotes)
    elif args.command == 'checkout':
        if args.b is False:
            checkout(args.branch)
        else:
            createBranch('checkout', args.branch)
    elif args.command == 'cat-file':
        try:
            cat_file(args.mode, args.hash_prefix)
        except ValueError as error:
            print(error, file=sys.stderr)
            sys.exit(1)
    elif args.command == 'commit':
        commit(args.message, author=args.author)
    elif args.command == 'create':
        create(args.network)
    elif args.command == 'clone':
        clone(args.name)
    elif args.command == 'diff':
        diff(args.staged)
    elif args.command == 'fetch':
        fetch(args.branch)
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
        merge(args.sourceBranch)
    elif args.command == 'push':
        push()
    elif args.command == 'pull':
        pull()
    elif args.command == 'status':
        status()
    else:
        assert False, 'unexpected command {!r}'.format(args.command)
