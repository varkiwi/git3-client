import os

from git3Client.utils.utils import write_file

def init(repo):
    """
    Function for the git init command. It creats a .git directory for repository and fills it with git related
    directories and files.
    """
    if os.path.exists(os.path.join(repo, '.git')):
        print(f"Repository {repo} exists already")
        return

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
    write_file(os.path.join(repo, '.git', 'HEAD'), b'ref: refs/heads/master')

    # write the name of the repository into a file
    write_file(os.path.join(repo, '.git', 'name'), str.encode('name: ' + repoName))
    
    print('Initialized empty Git3 repository in: {}/.git/'.format(fullPath))