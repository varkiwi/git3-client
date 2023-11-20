import argparse
import pytest
import unittest

from git3Client.gitInternals.repository import GitRepository
from git3Client.gitCommands.checkout import checkout


class MockedGitRepository:
    def __init__(self):
        pass

    def get_repo_root_path(self):
        return "test_repo_path"

def test_checkout_missing_branch(capsys):
    with pytest.raises(SystemExit) as excinfo:
        checkout(None)
    captured = capsys.readouterr()
    assert captured.out == "fatal: Branch name not given.\n"
    assert excinfo.value.code == 1


@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_branch_already_active(mocked_get_active_branch, capsys):
    with pytest.raises(SystemExit) as excinfo:
        checkout("test_branch")
    captured = capsys.readouterr()
    assert captured.out == "Already on 'test_branch'\n"
    assert excinfo.value.code == 0


@unittest.mock.patch("git3Client.gitCommands.checkout.write_file")
@unittest.mock.patch("git3Client.gitCommands.checkout.read_file", return_value=b"test_commit_hash")
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", return_value=True)
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_without_change(mocked_get_active_branch, mocked_git_repository,
                                 mocked_os_path_is_file, mocked_read_file, mocked_write_file):
    with pytest.raises(SystemExit) as excinfo:
        checkout("another_branch")
    assert mocked_write_file.call_count == 1
    assert excinfo.value.code == 0


@unittest.mock.patch("git3Client.gitCommands.checkout.write_file")
@unittest.mock.patch("git3Client.gitCommands.checkout.read_file", side_effect=[
    b"40624cfcac6bfa105167a255baa6625e84d337d8\tnot-for-merge branch test",
    b"40624cfcac6bfa105167a255baa6625e84d337d8"])
# False = select branch does not exist, FETCH_HEAD exists
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", side_effect=[False, True])
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_without_change_from_fetch_head(mocked_get_active_branch,
                                                 mocked_git_repository,
                                                 mocked_os_path_is_file,
                                                 mocked_read_file,
                                                 mocked_write_file):
    with pytest.raises(SystemExit) as excinfo:
        checkout("another_branch")
    assert mocked_write_file.call_count == 1
    assert excinfo.value.code == 0

@unittest.mock.patch("git3Client.gitCommands.checkout.write_file")
@unittest.mock.patch("git3Client.gitCommands.checkout.read_file", side_effect=[
    b"40624cfcac6bfa105167a255baa6625e84d337d8 refs/remotes/origin/another_branch\n",
    b"40624cfcac6bfa105167a255baa6625e84d337d8"])
# False = select branch does not exist, FETCH_HEAD does not exists, packed refs exists
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", side_effect=[False, False, True])
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_without_change_from_packed_refs(mocked_get_active_branch,
                                                  mocked_git_repository,
                                                  mocked_os_path_is_file,
                                                  mocked_read_file,
                                                  mocked_write_file):
    with pytest.raises(SystemExit) as excinfo:
        checkout("another_branch")
    assert mocked_write_file.call_count == 2
    assert excinfo.value.code == 0


# False = select branch does not exist, FETCH_HEAD does not exists, packed does not refs exists
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", side_effect=[False, False, False])
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_error_no_branch(mocked_get_active_branch,
                                  mocked_git_repository,
                                  mocked_os_path_is_file, capsys):
    with pytest.raises(SystemExit) as excinfo:
        checkout("another_branch")
    
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == "error: pathspec 'another_branch' did not match any file(s) known to git3\n"


@unittest.mock.patch("git3Client.gitCommands.checkout.get_status_workspace", return_value=(["test_file"], [], []))
@unittest.mock.patch("git3Client.gitCommands.checkout.read_file", side_effect=[b"test_commit_hash", b"another_commit_hash"])
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", return_value=True)
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_error_active_status(mocked_get_active_branch,
                                      mocked_git_repository,
                                      mocked_os_path_is_file, mocked_read_file,
                                      mocked_get_status_workspace, capsys):
    with pytest.raises(SystemExit) as excinfo:
        checkout("another_branch")

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == "error: Your local changes to the following files would be overwritten by checkout:\n\ttest_file\nPlease commit your changes or stash them before you switch branches.\nAborting\n"

@unittest.mock.patch("git3Client.gitCommands.checkout.get_status_commit", return_value=(["commit_hash"], [], []))
@unittest.mock.patch("git3Client.gitCommands.checkout.get_status_workspace", return_value=([], [], []))
@unittest.mock.patch("git3Client.gitCommands.checkout.read_file", side_effect=[b"test_commit_hash", b"another_commit_hash"])
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", return_value=True)
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_error_active_commit(mocked_get_active_branch,
                                      mocked_git_repository,
                                      mocked_os_path_is_file, mocked_read_file,
                                      mocked_get_status_workspace,
                                      mocked_get_status_commit, capsys):
    with pytest.raises(SystemExit) as excinfo:
        checkout("another_branch")

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == "error: Your local changes to the following files would be overwritten by checkout:\n\tcommit_hash\nPlease commit your changes or stash them before you switch branches.\nAborting\n"

@unittest.mock.patch("git3Client.gitCommands.checkout.update_HEAD")
@unittest.mock.patch("git3Client.gitCommands.checkout.add")
@unittest.mock.patch("git3Client.gitCommands.checkout.os.remove")
@unittest.mock.patch("git3Client.gitCommands.checkout.write_file")
@unittest.mock.patch("git3Client.gitCommands.checkout.read_object", return_value=("blob", b"data"))
@unittest.mock.patch("git3Client.gitCommands.checkout.remove_files_from_repo")
@unittest.mock.patch("git3Client.gitCommands.checkout.read_commit_entries", return_value={'file': 'something'})
@unittest.mock.patch("git3Client.gitCommands.checkout.get_status_commit", return_value=([], [], []))
@unittest.mock.patch("git3Client.gitCommands.checkout.get_status_workspace", return_value=([], [], []))
@unittest.mock.patch("git3Client.gitCommands.checkout.read_file", side_effect=[b"test_commit_hash", b"another_commit_hash"])
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", return_value=True)
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_correct_with_commit_files(mocked_get_active_branch, mocked_git_repository,
                                            mocked_os_path_is_file, mocked_read_file,
                                            mocked_get_status_workspace, mocked_get_status_commit,
                                            mocked_read_commit_entries,
                                            mocked_remove_files_from_repo,
                                            mocked_read_object,
                                            mocked_os_remove,
                                            mocked_write_file,
                                            mocked_add, mocked_update_head, capsys):
    checkout("another_branch")

    captured = capsys.readouterr()
    assert captured.out == "Switched to branch 'another_branch'\n"

@unittest.mock.patch("git3Client.gitCommands.checkout.update_HEAD")
@unittest.mock.patch("git3Client.gitCommands.checkout.add")
@unittest.mock.patch("git3Client.gitCommands.checkout.os.remove")
@unittest.mock.patch("git3Client.gitCommands.checkout.remove_files_from_repo")
@unittest.mock.patch("git3Client.gitCommands.checkout.read_commit_entries", return_value={})
@unittest.mock.patch("git3Client.gitCommands.checkout.get_status_commit", return_value=([], [], []))
@unittest.mock.patch("git3Client.gitCommands.checkout.get_status_workspace", return_value=([], [], []))
@unittest.mock.patch("git3Client.gitCommands.checkout.read_file", side_effect=[b"test_commit_hash", b"another_commit_hash"])
@unittest.mock.patch("git3Client.gitCommands.checkout.os.path.isfile", return_value=True)
@unittest.mock.patch("git3Client.gitCommands.checkout.repository", return_value=MockedGitRepository()) 
@unittest.mock.patch("git3Client.gitCommands.checkout.get_active_branch", return_value="test_branch")
def test_checkout_correct_without_commit_files(mocked_get_active_branch,
                                               mocked_git_repository,
                                               mocked_os_path_is_file,
                                               mocked_read_file,
                                               mocked_get_status_workspace,
                                               mocked_get_status_commit,
                                               mocked_read_commit_entries,
                                               mocked_remove_files_from_repo,
                                               mocked_os_remove,
                                               mocked_add, mocked_update_head,
                                               capsys):
    checkout("another_branch")

    captured = capsys.readouterr()
    assert captured.out == "Switched to branch 'another_branch'\n"