import os

from pathlib import Path

from git3Client.utils.utils import write_file


def init(repo: str = "."):
    """
    The init function creates an empty git repository by creating a .git directory in the current or given directory.

    Args:
        repo (str): Name of repository name. If none is given, the current directory is used.

    Returns:
        Boolean: Returns true if successful, false otherwise.
    """
    if repo == ".":
        repo = os.getcwd()

    if os.path.exists(os.path.join(repo, ".git")):
        print(f"Repository {repo} exists already")
        return False

    print("REPO", repo)
    print(os.path.exists(repo))
    if not os.path.exists(repo):
        os.makedirs(repo)
    os.mkdir(os.path.join(repo, ".git"))

    # create necessary directories
    for name in ["objects", "refs", "refs/heads"]:
        os.mkdir(os.path.join(repo, ".git", name))
    write_file(os.path.join(repo, ".git", "HEAD"), b"ref: refs/heads/main")

    repo_name = os.path.basename(repo)
    # write the name of the repository into a file
    write_file(os.path.join(repo, ".git", "name"), str.encode("name: " + repo_name))

    print("Initialized empty Git3 repository in: {}/.git/".format(repo))
    return True
