import pytest
import unittest
import os
import shutil
# import random

from pathlib import Path

from git3Client.gitCommands.init import init
from git3Client.gitCommands.add import add
from git3Client.gitInternals.repository import GitRepository

# class Test_Add():
GIT_FOLDER = '.git'
OBJECTS_DIR_PATH = os.path.join(GIT_FOLDER, 'objects')
INDEX_PATH = os.path.join(GIT_FOLDER, 'index')
repo_name = 'test_repo'
dir_name = 'test_dir'
file_names_and_content = [
    ('Readme.md', 'test text in Readme.md\n'),
    ('test_file_1', 'test text in test_file_1\n'),
    (os.path.join(dir_name, 'test_file_2'), 'test text in test_file_2\n'),
]
non_existing_file = 'non_existing_file'

file_hashes = [
    '08a1b6cf33d58d68c06175aa1e3027d131a977cb',
    '47542dc7cc3e931375909330a1bc069a59b45331',
    '4ec55bf2dce0b83b4fabbdffb90f1165d32daacb',
]

@pytest.fixture(scope='function')
def empty_objects_dir():
    yield
    
    for path in Path(OBJECTS_DIR_PATH).glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

@pytest.fixture
def delete_index_file():
    yield
    os.remove(os.path.join(GIT_FOLDER, 'index'))
    

@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    current_dir = os.getcwd()
    os.chdir(tmpdir)
    init(repo_name)
    os.chdir(repo_name)
    # create dirs and write files
    os.mkdir(dir_name)

    for file_info in file_names_and_content:
        with open(file_info[0], 'w') as f:
            f.write(file_info[1])
    # execute tests
    yield

    os.chdir(current_dir)
    try:
        shutil.rmtree(repo_name)
    except OSError as e:
        print("Error: %s : %s" % (repo_name, e.strerror))


@unittest.mock.patch('git3Client.gitCommands.add.repository')
def test_add_single_file(mocked_repository, empty_objects_dir, delete_index_file):
    mocked_repository.get_repo_path.return_value = os.getcwd()
    assert os.listdir(OBJECTS_DIR_PATH) == []

    add([file_names_and_content[0][0]])

    assert os.listdir(OBJECTS_DIR_PATH) == [file_hashes[0][:2]]
    assert os.listdir(os.path.join(OBJECTS_DIR_PATH, file_hashes[0][:2])) == [file_hashes[0][2:]]

    # def test_add_fileand_file_in_dir(self, empty_objects_dir, delete_index_file):
    #     assert os.listdir(OBJECTS_DIR_PATH) == []

    #     add([file_names_and_content[1][0], file_names_and_content[2][0]])

    #     assert os.listdir(OBJECTS_DIR_PATH).sort() == [file_hashes[1][:2], file_hashes[2][:2]].sort()
    #     assert os.listdir(os.path.join(OBJECTS_DIR_PATH, file_hashes[1][:2])) == [file_hashes[1][2:]]
    #     assert os.listdir(os.path.join(OBJECTS_DIR_PATH, file_hashes[2][:2])) == [file_hashes[2][2:]]

    # def test_adding_in_non_reposiotry_dir(self, move_to_root_and_back):
    #     with pytest.raises(SystemExit) as pytest_wrapped_e:
    #         add(file_names_and_content)
    #     assert pytest_wrapped_e.type == SystemExit
    #     assert pytest_wrapped_e.value.code == 1

    # def test_adding_non_existing_file(self, empty_objects_dir):
    #     with pytest.raises(SystemExit) as pytest_wrapped_e:
    #         add([non_existing_file])
    #     assert pytest_wrapped_e.type == SystemExit
    #     assert pytest_wrapped_e.value.code == 1
        