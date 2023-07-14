import argparse
import pytest
import unittest

from git3Client import git3
from git3Client.exceptions.NoRepositoryError import NoRepositoryError


class MockedGitRepository:
    def __init__(self):
        pass


def test_error_required_arguments():
    with pytest.raises(SystemExit):
        git3.main([])


@pytest.mark.parametrize("init_params", [None, ".", "test/123"])
@unittest.mock.patch("git3Client.git3.init", return_value=True)
def test_init_successful(mocked_init, init_params):
    git3.main(["init", init_params])
    mocked_init.assert_called_once()


@pytest.mark.parametrize("list_branch_params", [None, "-r", "--remote"])
@unittest.mock.patch("git3Client.git3.list_branches", return_value=True)
def test_branch_list_branches_successful(mocked_list_branches, list_branch_params):
    git3.main(["branch", list_branch_params])
    mocked_list_branches.assert_called_once()


@pytest.mark.parametrize("create_branch_params", ["test123", ".", "test/test/123"])
@unittest.mock.patch("git3Client.git3.create_branch", return_value=True)
def test_branch_create_branch_successful(mocked_create_branch, create_branch_params):
    git3.main(["branch", create_branch_params])
    mocked_create_branch.assert_called_once()


@unittest.mock.patch("git3Client.git3.checkout", return_value=True)
def test_checkout_successful(mocked_checkout):
    git3.main(["checkout", "test123"])
    mocked_checkout.assert_called_once()


@unittest.mock.patch("git3Client.git3.create_branch", return_value=True)
def test_checkout_successful_create_new_branch(mocked_create_branch):
    git3.main(["checkout", "-b", "test123"])
    mocked_create_branch.assert_called_once()


@unittest.mock.patch("git3Client.git3.checkout", return_value=True)
def test_checkout_error_missing_branch_name(mocked_checkout):
    with pytest.raises(SystemExit):
        git3.main(["checkout"])


def test_add_error_path_missing():
    with pytest.raises(SystemExit):
        git3.main(["add"])


@pytest.mark.parametrize(
    "path", [["test_file.test"], ["test_file.test", "test_file2.test"]]
)
@unittest.mock.patch("git3Client.git3.GitRepository")
@unittest.mock.patch("git3Client.git3.add", return_value=True)
def test_add_successful(mocked_add, mocked_git_repository, path):
    mocked_git_repository_instance = mocked_git_repository.return_value
    git3.main(["add", *path])
    mocked_add.assert_called_once_with(mocked_git_repository_instance, path)


@pytest.mark.parametrize(
    "mode_param", ["commit", "tree", "blob", "size", "type", "pretty"]
)
@unittest.mock.patch("git3Client.git3.cat_file", return_value=True)
def test_cat_file_successful(mocked_cat_file, mode_param):
    git3.main(["cat-file", mode_param, "sha1hash"])
    mocked_cat_file.assert_called_once_with(mode_param, "sha1hash")


@unittest.mock.patch("git3Client.git3.cat_file", side_effect=ValueError)
def test_cat_file_error_value_error(mocked_cat_file):
    with pytest.raises(SystemExit):
        git3.main(["cat-file", "commit", "sha1hash"])


@unittest.mock.patch("git3Client.git3.commit", return_value=True)
def test_commit_successful(mocked_commit):
    git3.main(["commit", "-m", "test commit message"])
    mocked_commit.assert_called_once_with("test commit message", author=None)


def test_commit_error_message_missing():
    with pytest.raises(SystemExit):
        git3.main(["commit"])


@pytest.mark.parametrize("network_name", ["godwoken", "mumbai"])
@unittest.mock.patch("git3Client.git3.create", return_value=True)
def test_create_successful(mocked_create, network_name):
    git3.main(["create", "--network", network_name])
    mocked_create.assert_called_once_with(network_name)


def test_create_error_wrong_network():
    with pytest.raises(SystemExit):
        git3.main(["create", "--network", "test"])


def test_create_error_missing_network():
    with pytest.raises(SystemExit):
        git3.main(["create"])


@unittest.mock.patch("git3Client.git3.clone", return_value=True)
def test_clone_successful(mocked_clone):
    git3.main(["clone", "repo_name"])
    mocked_clone.assert_called_once_with("repo_name")


def test_clone_error_missing_repository_name():
    with pytest.raises(SystemExit):
        git3.main(["clone"])


@unittest.mock.patch("git3Client.git3.diff", return_value=True)
def test_diff_successful(mocked_diff):
    git3.main(["diff"])
    mocked_diff.assert_called_once()


@unittest.mock.patch("git3Client.git3.fetch", return_value=True)
def test_fetch_successful(mocked_fetch):
    git3.main(["fetch"])
    mocked_fetch.assert_called_once()


@unittest.mock.patch("git3Client.git3.getAddress", return_value="UsersAddress")
def test_get_address_successful(mocked_get_address):
    git3.main(["get-address"])
    mocked_get_address.assert_called_once()


@unittest.mock.patch("git3Client.git3.read_file", return_value="test_file_content")
@unittest.mock.patch("git3Client.git3.hashObject", return_value=True)
def test_hash_object_successful(mocked_hash_object, mocked_read_file):
    git3.main(["hash-object", "test_file.test"])
    mocked_hash_object.assert_called_once_with("test_file_content", "blob", write=False)


@unittest.mock.patch("git3Client.git3.merge", return_value=True)
def test_merge_successful(mocked_merge):
    git3.main(["merge", "source_branch"])
    mocked_merge.assert_called_once_with("source_branch")


@unittest.mock.patch("git3Client.git3.push", return_value=True)
def test_push_successful(mocked_push):
    git3.main(["push"])
    mocked_push.assert_called_once()


@unittest.mock.patch("git3Client.git3.pull", return_value=True)
def test_pull_successful(mocked_pull):
    git3.main(["pull"])
    mocked_pull.assert_called_once()


@unittest.mock.patch("git3Client.git3.status", return_value=True)
def test_status_successful(mocked_status):
    git3.main(["status"])
    mocked_status.assert_called_once()


@unittest.mock.patch(
    "git3Client.git3.get_repo_root_path",
    side_effect=NoRepositoryError(
        "fatal: not a git repository (or any of the parent directories): .git"
    ),
)
def test_get_repo_root_path_error(mocked_get_repo_root_path):
    with pytest.raises(SystemExit):
        git3.main(["status"])
