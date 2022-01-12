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

def createBranch(name):
    """
    This function creates a new branch head named <name> which points to the current HEAD.
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

    if os.path.isfile('{}/.git/{}'.format(repo_root_path, currentHeadRef)):
        # if file exists, then we can read the content
        # and write it into the new file
        commitHash = read_file('{}/.git/{}'.format(repo_root_path, currentHeadRef)).decode("utf-8")
        write_file('{}/.git/refs/heads/{}'.format(repo_root_path, name), commitHash, binary='')
    else:
        print('fatal: Not a valid object name: \'{}\'.'.format(currentHeadRef.split('/')[-1]))
        exit(1)