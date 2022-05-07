import pytest
import os
import shutil
import random

from pathlib import Path

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.gitCommands.init import init
from git3Client.gitCommands.add import add

class Test_Add():
    GIT_FOLDER = '.git'
    OBJECTS_DIR_PATH = os.path.join(GIT_FOLDER, 'objects')
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

    @pytest.fixture
    def move_to_root_and_back(self):
        current_path = os.getcwd()
        os.chdir('/')
        yield
        os.chdir(current_path)

    @pytest.fixture(scope='function')
    def empty_objects_dir(self):
        yield
        
        for path in Path(self.OBJECTS_DIR_PATH).glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    @pytest.fixture
    def delete_index_file(self):
        yield
        os.remove(os.path.join(self.GIT_FOLDER, 'index'))
        

    @pytest.fixture(scope='module', autouse=True)
    def run_before_and_after_tests(self):
        start_path = os.path.abspath(os.getcwd())

        init(self.repo_name)
        os.chdir(self.repo_name)

        # create dirs and write files
        os.mkdir(self.dir_name)

        for file_info in self.file_names_and_content:
            with open(file_info[0], 'w') as f:
                f.write(file_info[1])
        # execute tests
        yield

        os.chdir(start_path)
        try:
            shutil.rmtree(self.repo_name)
        except OSError as e:
            print("Error: %s : %s" % (self.repo_name, e.strerror))
    
    
    def test_add_single_file(self, empty_objects_dir, delete_index_file):
        assert os.listdir(self.OBJECTS_DIR_PATH) == []

        add([self.file_names_and_content[0][0]])

        assert os.listdir(self.OBJECTS_DIR_PATH) == [self.file_hashes[0][:2]]
        assert os.listdir(os.path.join(self.OBJECTS_DIR_PATH, self.file_hashes[0][:2])) == [self.file_hashes[0][2:]]

    def test_add_fileand_file_in_dir(self, empty_objects_dir, delete_index_file):
        assert os.listdir(self.OBJECTS_DIR_PATH) == []

        add([self.file_names_and_content[1][0], self.file_names_and_content[2][0]])

        assert os.listdir(self.OBJECTS_DIR_PATH).sort() == [self.file_hashes[1][:2], self.file_hashes[2][:2]].sort()
        assert os.listdir(os.path.join(self.OBJECTS_DIR_PATH, self.file_hashes[1][:2])) == [self.file_hashes[1][2:]]
        assert os.listdir(os.path.join(self.OBJECTS_DIR_PATH, self.file_hashes[2][:2])) == [self.file_hashes[2][2:]]

    def test_adding_in_non_reposiotry_dir(self, move_to_root_and_back):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            add(self.file_names_and_content)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
        #TODO: check index file

    def test_adding_non_existing_file(self, empty_objects_dir):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            add([self.non_existing_file])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
        