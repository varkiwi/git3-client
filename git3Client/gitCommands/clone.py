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
    user_address, repo_name = repo_name.split('/')

    git_factory = get_factory_contract()
    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())

    repository = git_factory.functions.getRepository(user_key).call()

    if not repository[0] or repository[1] != repo_name:
        print('No such repository')
        return
    git_repo_address = repository[2]
    
    branch_contract = get_facet_contract("GitBranch", git_repo_address)
    
    branches = branch_contract.functions.getBranchNames().call()

    # string, which is going to be written into the .git/packed-refs file
    packed_refs_content = ""
    head_cids = set()

    for branch_name in branches:
        branch = branch_contract.functions.getBranch(branch_name).call()
        head_cids.add(branch[1])
        packed_refs_content += '{} refs/remotes/origin/{}\n'.format(branch[1], branch_name)
        if branch_name == 'main':
            main_cid = branch[1]

    print('Cloning {:s}'.format(repo_name))
    # initialize repository
    if not init(repo_name):
        return

    # get all remote commits
    for head_cid in head_cids:
        commits = get_all_remote_commits(head_cid)
        
        # replacing cid with sha1
        packed_refs_content = packed_refs_content.replace(head_cid, commits[0]['sha1'])

        # we are going to unpack only the files for the main branch. Commits and all
        # other git objects should be still downloaded
        if head_cid == main_cid:
            # write to refs
            main_ref_path = os.path.join(repo_name, '.git', 'refs', 'heads', 'main')
            write_file(main_ref_path, (commits[0]['sha1'] + '\n').encode())      
            first = True
        else:
            first = False

        for commit in commits:
            unpack_files_of_commit(repo_name, commit, first)
            first = False

    #chaning into repo, also for add function, in order to find the index file
    os.chdir(repo_name)

    # write packed-refs
    write_file('.git/packed-refs', packed_refs_content, binary='')

    write_file('.git/name', str.encode('location: ' + user_key))
    # collecting all files from the repo in order to create the index file
    files_to_add = []
    for path, subdirs, files in os.walk('.'):
        for name in files:
            # we don't want to add the files under .git to the index
            if not path.startswith('./.git'):
                files_to_add.append(os.path.join(path, name)[2:])
    add(files_to_add)
    print('{:s} cloned'.format(repo_name))