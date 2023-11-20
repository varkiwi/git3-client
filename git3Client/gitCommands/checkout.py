import os

from git3Client.gitCommands.add import add
from git3Client.gitCommands.branch import get_active_branch, update_HEAD

from git3Client.gitInternals.repository import repository
from git3Client.gitInternals.gitIndex import get_status_workspace, get_status_commit
from git3Client.gitInternals.gitCommit import read_commit_entries
from git3Client.gitInternals.gitObject import read_object
from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import (
    get_repo_root_path,
    read_file,
    write_file,
    remove_files_from_repo,
)


def print_checkout_error(changed, new, deleted): # pragma: no cover
    print(
        "error: Your local changes to the following files would be overwritten by checkout:"
    )
    if len(changed) != 0:
        print(f"\t{changed[0]}")
    elif len(new) != 0:
        print(f"  {new[0]}")
    elif len(deleted) != 0:
        print(f"  {deleted[0]}")
    print("Please commit your changes or stash them before you switch branches.\nAborting")
    exit(1)


def checkout(branch: str):
    if branch is None:
        print("fatal: Branch name not given.")
        exit(1)

    active_branch = get_active_branch()

    if active_branch == branch:
        print(f"Already on '{branch}'")
        exit(0)

    # boolean to see if the commit hash is taken from the packed-refs file
    from_packed_refs = False
    target_commit_hash = None

    repo_root_path = repository.get_repo_path()
    # check if branch exists
    # first we check if git/refs/heads exists. If it does exist
    if os.path.isfile(f"{repo_root_path}/.git/refs/heads/{branch}"):
        # we load the commit hash
        target_commit_hash = (
            read_file(f"{repo_root_path}/.git/refs/heads/{branch}")
            .decode("utf-8")
            .strip()
        )
    else:
        # if it doesn't exist, we check if the FETCH_HEAD file exists
        if os.path.isfile(f"{repo_root_path}/.git/FETCH_HEAD"):
            fetch_head_content = read_file(
                f"{repo_root_path}/.git/FETCH_HEAD").decode("utf-8")
            target_commit_hash = (
                fetch_head_content.split(f"branch '{branch}'")[0]
                .split("\n")[-1]
                .split("\t")[0]
                .strip()
            )
        # if it does not exist, we check if packed-refs exists
        elif os.path.isfile(f"{repo_root_path}/.git/packed-refs"):
            # in case it exists, we check if the branch exists in packed-refs
            packed_refs_content = read_file(
                f"{repo_root_path}/.git/packed-refs").decode("utf-8")
            if branch in packed_refs_content:
                # get the commit hash
                from_packed_refs = True
                target_commit_hash = (
                    packed_refs_content.split(
                        f"refs/remotes/origin/{branch}\n"
                    )[0]
                    .split("\n")[-1]
                    .strip()
                )
        else:
            # if does not exist, we exit
            print(f"error: pathspec '{branch}' did not match any"
                  " file(s) known to git3")
            exit(1)

    current_commit_hash = (
        read_file(f"{repo_root_path}/.git/refs/heads/{active_branch}")
        .decode("utf-8")
        .strip()
    )

    # if the commit hash has been taken from the packed-refs, we need to write
    # the .git/refs/heads/<branch> file
    if from_packed_refs:
        print(f"Branch '{branch}' set up to track remote branch "
              f"'{branch}' from 'origin'.")
        write_file(f"{repo_root_path}/.git/refs/heads/{branch}",
                   target_commit_hash, binary="")

    if current_commit_hash == target_commit_hash:
        # switch branch when the hashes are the same.
        # we don't have to do anything else
        write_file(
            f"{repo_root_path}/.git/HEAD",
            f"ref: refs/heads/{branch}",
            binary="",
        )
        exit(0)

    changed, new, deleted = get_status_workspace()
    if len(changed) != 0 or len(new) != 0 or len(deleted) != 0:
        print_checkout_error(changed, new, deleted)

    changed, new, deleted = get_status_commit()
    if len(changed) != 0 or len(new) != 0 or len(deleted) != 0:
        print_checkout_error(changed, new, deleted)

    commit_entries = read_commit_entries(target_commit_hash)

    # we are deleting all the files in the repo
    # there might be a better way, where we iterate over all of the files,
    # hash and compare the hashes. If there is no difference, leave as is, otherwise
    # overwrite. We would also need to check for files which are not in the index!
    # Maybe something at a later point in time :)
    remove_files_from_repo()

    files_to_add = []

    for filename in commit_entries:
        object_type, data = read_object(commit_entries[filename])
        assert object_type == "blob"
        write_file(
            f"{repo_root_path}/{filename}", data.decode("utf-8"), binary=""
        )
        files_to_add.append(filename)

    # remove index file
    os.remove(f"{repo_root_path}/.git/index")
    add(files_to_add)
    update_HEAD(repo_root_path, branch)
    print(f"Switched to branch '{branch}'")
