import os

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import list_files_in_dir, get_repo_root_path, read_file, write_file

def listBranches():
    """Add all file paths to git index."""
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)

    branches = list_files_in_dir('{}/.git/refs/heads'.format(repo_root_path))
    branches.sort()
    result = ''
    for branch in branches:
        result += '* {}\n'.format(branch)
    print(result)

def createBranch(command, name):
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
    
    pathToRef = '{}/.git/refs/heads/{}'.format(repo_root_path, name)

    # check if branch already exists
    if os.path.isfile(pathToRef):
        print('fatal: A branch named {} already exists.'.format(name))
        exit(1)
    # If not, 
    currentHeadRef = read_file('{}/.git/HEAD'.format(repo_root_path)).decode("utf-8").split('ref:')[1].strip()

    # check if the file under the refs/heads/ directory exists
    if os.path.isfile('{}/.git/{}'.format(repo_root_path, currentHeadRef)):
        # if file exists, then we can read the content
        # and write it into the new file
        commitHash = read_file('{}/.git/{}'.format(repo_root_path, currentHeadRef)).decode("utf-8")
        write_file('{}/.git/refs/heads/{}'.format(repo_root_path, name), commitHash, binary='')
    else:
        # if the user executes git branch, an error is thrown
        if command == 'branch':
            print('fatal: Not a valid object name: \'{}\'.'.format(currentHeadRef.split('/')[-1]))
            exit(1)
    
    if command == 'checkout':
        # in case of git switch or checkout, the HEAD file is updated
        write_file('{}/.git/HEAD'.format(repo_root_path, name), 'ref: refs/heads/{}'.format(name), binary='')