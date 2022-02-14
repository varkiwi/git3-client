import os

from git3Client.utils.utils import write_file

def init(repo: str = '.'):
    """
    The init function creates an empty git repository by creating a .git directory in the current or given directory.

    Args:
        repo (str): Name of repository name. If none is given, the current directory is used.
    
    Returns:
        Boolean: Returns true if successful, false otherwise.
    """
    if os.path.exists(os.path.join(repo, '.git')):
        print(f"Repository {repo} exists already")
        return False

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
    write_file(os.path.join(repo, '.git', 'HEAD'), b'ref: refs/heads/main')

    # write the name of the repository into a file
    write_file(os.path.join(repo, '.git', 'name'), str.encode('name: ' + repoName))
    
    print('Initialized empty Git3 repository in: {}/.git/'.format(fullPath))
    return True