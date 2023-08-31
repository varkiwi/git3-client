import os
import glob
import pytest
import unittest

from git3Client.gitCommands.init import init


REPOSITORY_NAME = "test_repo"


@unittest.mock.patch("git3Client.gitCommands.init.os.path.exists", return_value=True)
def test_init_error_repository_exists(mocked_os_exists, tmpdir):
    assert not init(f"{tmpdir}/{REPOSITORY_NAME}")


@pytest.mark.parametrize(
    "repository_name", [REPOSITORY_NAME, f"subdir/{REPOSITORY_NAME}"]
)
def test_init_successful(repository_name, tmpdir):
    repository_path = tmpdir.join(repository_name)

    assert init(repository_path)

    assert os.path.isdir(repository_path.join(".git"))

    directories = ["objects", "refs", "refs/heads"]

    for dir in directories:
        assert os.path.isdir(repository_path.join(".git", dir))

    # since the repo has been just created, there shouldn't be any files in the heads dir
    assert (
        len(glob.glob(os.path.join(repository_path, ".git", "refs", "heads", "*"))) == 0
    )

    # check that the head points to the main branch
    with open(repository_path.join(".git", "HEAD"), "r") as f:
        assert f.read() == "ref: refs/heads/main"


def test_init_successful_without_param(change_test_dir):
    cwd = os.getcwd()
    assert init()

    assert os.path.isdir(f"{cwd}/.git")

    directories = ["objects", "refs", "refs/heads"]

    for dir in directories:
        assert os.path.isdir(f"{cwd}/.git/{dir}")

    # since the repo has been just created, there shouldn't be any files in the heads dir
    assert len(glob.glob(os.path.join(cwd, ".git", "refs", "heads", "*"))) == 0

    # check that the head points to the main branch
    with open(os.path.join(cwd, ".git", "HEAD"), "r") as f:
        assert f.read() == "ref: refs/heads/main"
