import os, re

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import list_files_in_dir, get_repo_root_path, read_file, write_file

def listBranches(remotes):
    """Add all file paths to git index."""
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)

    # if remotes flag is set, read remote branches from packed-refs file    
    if remotes:
        packed_refs_content = read_file('{}/.git/packed-refs'.format(repo_root_path)).decode('utf-8')
        branches = re.findall('refs\/remotes\/origin\/(\w*)', packed_refs_content)
    else:
        branches = list_files_in_dir('{}/.git/refs/heads'.format(repo_root_path))
    
    branches.sort()
    result = ''
    for branch in branches:
        result += '* {}\n'.format(branch)
    print(result)

def createBranch(command, newBranchName):
    """
    This function creates a new branch head named <name> which points to the current HEAD.

    command arg is used to distinguish if it has been called by checkout or branch, since it behaves
    a bit differently.
    """
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)
    
    pathToRef = '{}/.git/refs/heads/{}'.format(repo_root_path, newBranchName)

    # check if branch already exists
    if os.path.isfile(pathToRef):
        print('fatal: A branch named {} already exists.'.format(newBranchName))
        exit(1)
    # If not, 
    currentHeadRef = read_file('{}/.git/HEAD'.format(repo_root_path)).decode("utf-8").split('ref:')[1].strip()

    # check if the file under the refs/heads/ directory exists
    if os.path.isfile('{}/.git/{}'.format(repo_root_path, currentHeadRef)):
        # if file exists, then we can read the content
        # and write it into the new file
        commitHash = read_file('{}/.git/{}'.format(repo_root_path, currentHeadRef)).decode("utf-8")
        write_file('{}/.git/refs/heads/{}'.format(repo_root_path, newBranchName), commitHash, binary='')
    else:
        # if the user executes git branch, an error is thrown
        if command == 'branch':
            print('fatal: Not a valid object name: \'{}\'.'.format(currentHeadRef.split('/')[-1]))
            exit(1)
    
    if command == 'checkout':
        # in case of git switch or checkout, the HEAD file is updated
        update_HEAD(repo_root_path, newBranchName)
        print('Switched to a new branch \'{}\''.format(newBranchName))

def get_active_branch():
    """
    Returns the branch name the HEAD is pointing to.
    """
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)
    return read_file('{}/.git/HEAD'.format(repo_root_path)).decode("utf-8").split('ref:')[1].strip().split('/')[-1]


def update_HEAD(pathToRepo, newBranchName):
    write_file('{}/.git/HEAD'.format(pathToRepo), 'ref: refs/heads/{}'.format(newBranchName), binary='')