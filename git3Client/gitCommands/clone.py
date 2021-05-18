import binascii, os

from git3Client.dlt.contract import get_factory_contract, get_repository_contract, get_facet_contract
from git3Client.dlt.repository import get_all_remote_commits

from git3Client.gitCommands.init import init
from git3Client.gitCommands.add import add

from git3Client.gitInternals.gitCommit import unpack_files_of_commit

from git3Client.utils.utils import write_file

def clone(repo_name):
    """
    Cloning a remote repository on the local machine.

    repo_name: Repository to be cloned
    """
    # git3 clone 0xE838bC8b2D069CE43894143836fA974643646291/repoDeppo
    user_address, repo_name = repo_name.split('/')

    git_factory = get_factory_contract()
    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())

    # repository = git_factory.functions.repositoryList(user_key).call()
    repository = git_factory.functions.getRepository(user_key).call()

    if not repository[0] or repository[1] != repo_name:
        print('No such repository')
        return
    git_repo_address = repository[2]
    # branch_contract = get_repository_contract(git_repo_address)
    branch_contract = get_facet_contract("GitBranch", git_repo_address)
    # branch = branch_contract.functions.branches('main').call()
    branch = branch_contract.functions.getBranch('main').call()
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
    write_file(os.path.join('.git', 'name'), str.encode('location: ' + user_key))
    # collecting all files from the repo in order to create the index file
    files_to_add = []
    for path, subdirs, files in os.walk('.'):
        for name in files:
            # we don't want to add the files under .git to the index
            if not path.startswith('./.git'):
                files_to_add.append(os.path.join(path, name)[2:])
    add(files_to_add)
    print('{:s} cloned'.format(repo_name))