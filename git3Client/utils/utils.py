import os, requests, zlib, sys, shutil

from pathlib import Path
from cryptography.hazmat.primitives import serialization

from git3Client.exceptions.NoRepositoryError import NoRepositoryError
from git3Client.config.config import MUMBAI_GAS_STATION, MUMBAI_CHAINID, GODWOKEN_TESTNET_CHAINID

def get_repo_root_path() -> str:
    """
    Finds the root path of the repository where the .git folder resides and returns the path.
    If no .git folder is found, returns False

    Returns:
        str: path to the root of the repository

    Raises:
        NoRepositoryError: if no .git folder is found
    """
    path_to_test = Path(os.getcwd())
    contains_git_folder = os.path.isdir(str(path_to_test) + '/.git')
    if contains_git_folder:
        return str(path_to_test)
    parent = 0

    while not contains_git_folder and len(path_to_test.parents) != 0 and str(path_to_test.parents[parent]) != '/':
        contains_git_folder = os.path.isdir(str(path_to_test.parents[parent]) + '/.git')
        if contains_git_folder:
            break
        parent += 1
    if contains_git_folder:
        return str(path_to_test.parents[parent])
    
    raise NoRepositoryError('fatal: not a git repository (or any of the parent directories): .git')

def get_value_from_config_file(key: str) -> str:
    """
    Reads the values from the git config file and returns the value for the given key
    Key can be: email, name or IdentityFile.

    Args:
        key: key to look for in the config file

    Returns:
        str: value of the key

    Raises:
        NoRepositoryError: if no .git folder is found
    """
    try:
        # we are going to check if there is a config file in the repo.
        root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        raise nre

    config_path = os.path.join(root_path, '.git' , 'config')
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
        pem_content = read_file(os.path.expanduser(identity_file_path))
    except FileNotFoundError as fnfe:
        print(fnfe)
        sys.exit(1)

    private_key = serialization.load_pem_private_key(
        pem_content,
        password=None
    )
    return hex(private_key.private_numbers().private_value)[2:]

def get_current_gas_price(network):
    """
    Gets the current standard gas price for the network
    """
    print('Getting current gas price')
    if network == 'mumbai':
        return requests.get(MUMBAI_GAS_STATION, verify=False).json()['fast']['maxPriorityFee']
    elif network == 'godwoken':
        return 0
    else:
        print(f"Network {network} not supported")
        sys.exit(1)

def get_chain_id(network):
    if network == 'mumbai':
        return MUMBAI_CHAINID
    elif network == 'godwoken':
        return GODWOKEN_TESTNET_CHAINID
    else:
        print(f"Network {network} not supported")
        sys.exit(1)

def read_repo_name():
    """Read the repoName file and return the name"""
    repo_root_path = get_repo_root_path()
    try:
        data = read_file(os.path.join(repo_root_path, '.git', 'name'))
    except FileNotFoundError:
        return ""
    return data.rstrip().decode('ascii')

def get_current_branch_name() -> str:
    """
    Get the current branch name and return the string

    Returns:
        str: name of the current branch

    Raises:
        NoRepositoryError: if no .git folder is found
        FileNotFoundError: if no branch file is found
    """
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError:
        raise nre
    try:
        headContent = read_file(path=os.path.join(repo_root_path, '.git', 'HEAD')).decode('ascii')
    except FileNotFoundError as fnfe:
        raise fnfe

    branchName = headContent.split('/')[-1].strip()
    return branchName

def get_active_branch_hash() -> str:
    """
    Get current commit hash (SHA-1 string) of local active branch.

    Returns:
        str: commit hash of active branch, None if no specific branch file is available

    Raises:
        NoRepositoryError: if no .git folder is found
    """
    try:
        repo_root_path = get_repo_root_path()
        activeBranch = get_current_branch_name()
    except NoRepositoryError as nre:
        raise nre
    except FileNotFoundError as fnfe:
        return None

    branch_path = os.path.join(repo_root_path, '.git', 'refs', 'heads', activeBranch)
    try:
        return read_file(branch_path).decode().strip()
    except FileNotFoundError:
        return None

def get_branch_hash(branchName):
    """Get commit hash (SHA-1 string) of a branch."""
    repo_root_path = get_repo_root_path()
    branch_path = os.path.join(repo_root_path, '.git', 'refs', 'heads', branchName)
    try:
        return read_file(branch_path).decode().strip()
    except FileNotFoundError:
        return None

def remove_files_from_repo():
    """Remove all files from the repository"""
    repo_root_path = get_repo_root_path()
    files = list_files_in_dir(repo_root_path)
    for file in files:
        if file != '.git':
            if os.path.isfile(file):
                os.remove(os.path.join(repo_root_path, file))
            else:
                shutil.rmtree(os.path.join(repo_root_path, file))

def list_files_in_dir(path):
    """List all files in a directory."""
    return os.listdir(path)

def read_file(path) -> bytes:
    """
    Reads contents of file at given path as bytes.

    Args:
        path (str): path to file to read

    Returns:
        bytes: contents of file

    Raises:
        FileNotFoundError: if file does not exist
    """
    try:
        with open(path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError('File not found: {}'.format(path))

def write_file(path: str, data :bytes, binary: str = 'b'):
    """
    Write data bytes to file at given path.
    
    Args:
        path (str): path to file to write
        data (bytes): data to write to file
        binary (str): 'b' for binary
    """
    os.makedirs('/'.join(path.split('/')[0:-1]), exist_ok=True)
    with open(path, 'w{}'.format(binary)) as f:
        f.write(data)