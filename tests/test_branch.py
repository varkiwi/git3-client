import os
import pytest
import unittest

from git3Client.gitCommands.branch import create_branch
from git3Client.gitCommands.branch import get_active_branch
from git3Client.gitCommands.branch import list_branches
from git3Client.gitCommands.branch import update_HEAD

def test_update_head_correct(change_test_dir):
    assert os.listdir() == []

    update_HEAD(os.getcwd(), 'main')

    with open('.git/HEAD', 'r') as f:
        assert f.read() == 'ref: refs/heads/main'

@unittest.mock.patch('git3Client.gitCommands.branch.repository')
def test_get_branch_name_correct(mocked_repository, change_test_dir,
                                 create_repository):
    mocked_repository.get_repo_path.return_value = os.getcwd()
    assert get_active_branch() == 'main'


@unittest.mock.patch('git3Client.gitCommands.branch.repository')
def test_create_branch_success_checkout(mocked_repository, change_test_dir,
                                        create_repository):
    mocked_repository.get_repo_path.return_value = os.getcwd()
    
    create_branch('checkout', 'test')

    with open('.git/HEAD', 'r') as f:
        head_content = f.read()

    assert head_content == 'ref: refs/heads/test'

@unittest.mock.patch('git3Client.gitCommands.branch.repository')
def test_create_branch_success_branch(mocked_repository, change_test_dir,
                                      create_repository):
    commit_hash = '1234567890'
    with open('.git/refs/heads/main', 'w') as f:
        f.write(commit_hash)
    mocked_repository.get_repo_path.return_value = os.getcwd()
    
    create_branch('branch', 'test')

    with open('.git/refs/heads/test', 'r') as f:
        assert f.read() == commit_hash

@unittest.mock.patch('git3Client.gitCommands.branch.os.path.isfile', return_value=True)
@unittest.mock.patch('git3Client.gitCommands.branch.repository')
def test_create_branch_error_exists_already(mocked_repository, mocked_isfile,
                                            change_test_dir,
                                            create_repository):
    mocked_repository.get_repo_path.return_value = os.getcwd()
    with pytest.raises(SystemExit):
        create_branch('checkout', 'test')


@unittest.mock.patch('git3Client.gitCommands.branch.os.path.isfile', return_value=False)
@unittest.mock.patch('git3Client.gitCommands.branch.repository')
def test_create_branch_error_invalid_object(mocked_repository, mocked_isfile,
                                            change_test_dir,
                                            create_repository):
    mocked_repository.get_repo_path.return_value = os.getcwd()
    with pytest.raises(SystemExit):
        create_branch('branch', 'test')

@pytest.mark.parametrize('output_ref_heads', [([], "* main\n\n"),
                         (['main', 'test'], "* main\n  test\n\n")])
@unittest.mock.patch('git3Client.gitCommands.branch.list_files_in_dir')
@unittest.mock.patch('git3Client.gitCommands.branch.repository')
def test_list_branches_correct(mocked_repository,
                               mocked_list_files_in_dir,
                               output_ref_heads,
                               change_test_dir, create_repository,
                               capsys):
    mocked_repository.get_repo_path.return_value = os.getcwd()
    mocked_list_files_in_dir.return_value = output_ref_heads[0]
    list_branches()
    captured = capsys.readouterr()
    assert captured.out == output_ref_heads[1]
