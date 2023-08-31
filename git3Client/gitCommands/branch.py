import re
import os

from git3Client.gitInternals.repository import repository

from git3Client.utils.utils import list_files_in_dir
from git3Client.utils.utils import read_file
from git3Client.utils.utils import write_file


def list_branches(remotes: bool = False):
    """Lists all branches in the repository.
    
    Args:
        remotes (bool, optional): If true, lists all remote branches.
            Defaults to False.
    """
    repo_root_path = repository.get_repo_path()
    # if remotes flag is set, read remote branches from packed-refs file
    if remotes:
        packed_refs_content = read_file(
            f"{repo_root_path}/.git/packed-refs").decode("utf-8")
        branches = re.findall("refs\/remotes\/origin\/(\w*)",
                              packed_refs_content)
    else:
        branches = list_files_in_dir(f"{repo_root_path}/.git/refs/heads")
        if len(branches) == 0:
            branches = ["main"]
            
    active_branch = get_active_branch()
    branches.sort()
    result = ""
    for branch in branches:
        if branch == active_branch:
            result += f"* {branch}\n"
        else:
            result += f"  {branch}\n"
    print(result)


def create_branch(command: str, new_branch_name: str):
    """
    This function creates a new branch head named <name> which points to
    the current HEAD.

    Args:
        command (str): Command that was used to call this function. Can be
            either 'checkout' or 'branch'.
        new_branch_name (str): Name of the new branch.
    """
    repo_root_path = repository.get_repo_path()
    path_to_ref = f"{repo_root_path}/.git/refs/heads/{new_branch_name}"

    # check if branch already exists
    if os.path.isfile(path_to_ref):
        print(f"fatal: A branch named {new_branch_name} already exists.")
        exit(1)
    # If not,
    current_head_ref = (
        read_file(f"{repo_root_path}/.git/HEAD")
        .decode("utf-8")
        .split("ref:")[1]
        .strip()
    )

    # check if the file under the refs/heads/ directory exists
    if os.path.isfile(f"{repo_root_path}/.git/{current_head_ref}"):
        # if file exists, then we can read the content
        # and write it into the new file
        commit_hash = read_file(
            f"{repo_root_path}/.git/{current_head_ref}"
        ).decode("utf-8")
        write_file(f"{repo_root_path}/.git/refs/heads/{new_branch_name}",
                   commit_hash, binary="")
    else:
        # if the user executes git branch, an error is thrown
        if command == "branch":
            print("fatal: Not a valid object name: '"
                  f"{current_head_ref.split('/')[-1]}'.")
            exit(1)

    if command == "checkout":
        # in case of git switch or checkout, the HEAD file is updated
        update_HEAD(repo_root_path, new_branch_name)
        print(f"Switched to a new branch '{new_branch_name}'")


def get_active_branch() -> str:
    """
    Returns the branch name the HEAD is pointing to.

    Returns:
        str: Name of the branch.
    """
    repo_root_path = repository.get_repo_path()
    return (
        read_file(f"{repo_root_path}/.git/HEAD")
            .decode("utf-8")
            .split("ref:")[1]
            .strip()
            .split("/")[-1]
    )


def update_HEAD(path_to_repo: str, new_branch_name: str):
    """Writes the new branch name into the HEAD file.

    Args:
        path_to_repo (str): Path to the repository.
        new_branch_name (str): Name of the new branch.
    """
    write_file(f"{path_to_repo}/.git/HEAD",
        f"ref: refs/heads/{new_branch_name}", binary="")
