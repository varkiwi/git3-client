import pytest
import unittest

from git3Client import git3

class MockedGitRepository:
    def __init__(self):
        pass

def test_error_required_arguments():
    with pytest.raises(SystemExit):
        git3.main([])

@pytest.mark.parametrize('init_params', [None, '.', 'test/123'])
@unittest.mock.patch('git3Client.git3.init', return_value=True)
def test_init_successful(mocked_init, init_params):
    git3.main(['init', init_params])
    mocked_init.assert_called_once()

@pytest.mark.parametrize('list_branch_params', [None, '-r', '--remote'])
@unittest.mock.patch('git3Client.git3.listBranches', return_value=True)
def test_branch_list_branches_successful(mocked_list_branches, list_branch_params):
    git3.main(['branch', list_branch_params])
    mocked_list_branches.assert_called_once()

@pytest.mark.parametrize('create_branch_params', ['test123', '.', 'test/test/123'])
@unittest.mock.patch('git3Client.git3.createBranch', return_value=True)
def test_branch_create_branch_successful(mocked_create_branch, create_branch_params):
    git3.main(['branch', create_branch_params])
    mocked_create_branch.assert_called_once()

def test_add_error_path_missing():
    with pytest.raises(SystemExit):
        git3.main(['add'])

@pytest.mark.parametrize('path', [['test_file.test'], ['test_file.test', 'test_file2.test']])
@unittest.mock.patch('git3Client.git3.GitRepository')
@unittest.mock.patch('git3Client.git3.add', return_value=True)
def test_add_successful(mocked_add, mocked_git_repository, path):
    mocked_git_repository_instance = mocked_git_repository.return_value
    git3.main(['add', *path])
    mocked_add.assert_called_once_with(mocked_git_repository_instance, path)