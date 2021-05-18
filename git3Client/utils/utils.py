import os, requests, zlib, sys

from pathlib import Path
from Crypto.PublicKey import ECC

from git3Client.exceptions import NoRepositoryError

MUMBAI_GAS_STATION='https://gasstation-mumbai.matic.today'

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

def get_value_from_config_file(key):
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

def get_private_key():
    """
    Reads the private key from a (encrypted) pem file and returns it
    """
    identity_file_path = get_value_from_config_file('IdentityFile')
    if identity_file_path == None:
        print('No identity file provided. Please provide an identity file on your config file')
        sys.exit(1)
    try:
        content = read_file(os.path.expanduser(identity_file_path))
    except FileNotFoundError as fnfe:
        print(fnfe)
        sys.exit(1)

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

def get_current_gas_price():
    """
    Gets the current standard gas price for the network
    """
    print('Getting current gas price')
    return requests.get(MUMBAI_GAS_STATION).json()['standard']

def read_repo_name():
    """Read the repoName file and return the name"""
    repo_root_path = get_repo_root_path()
    try:
        data = read_file(os.path.join(repo_root_path, '.git', 'name'))
    except FileNotFoundError:
        return ""
    return data.rstrip().decode('ascii')

def get_local_master_hash():
    """Get current commit hash (SHA-1 string) of local master branch."""
    repo_root_path = get_repo_root_path()
    master_path = os.path.join(repo_root_path, '.git', 'refs', 'heads', 'master')
    try:
        return read_file(master_path).decode().strip()
    except FileNotFoundError:
        return None

def read_file(path):
    """Read contents of file at given path as bytes."""
    with open(path, 'rb') as f:
        return f.read()

def write_file(path, data):
    """Write data bytes to file at given path."""
    with open(path, 'wb') as f:
        f.write(data)