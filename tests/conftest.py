import pytest
import os
import shutil

from git3Client.gitCommands.init import init
from git3Client.gitCommands.add import add

@pytest.fixture
def move_to_root_and_back():
    current_path = os.getcwd()
    os.chdir('/')
    yield
    os.chdir(current_path)

@pytest.fixture
def create_file():
    with open('Readme.md', 'w') as f:
        f.write('test text in Readme.md\n')
    yield

@pytest.fixture
def add_file_to_index():
    add(['Readme.md'])
    yield

@pytest.fixture
def create_local_config_file():
    config_content = "[user]\n\temail = test@test.com\n\tname = pytester"
    with open(os.path.join('.git', 'config'), 'w') as f:
        f.write(config_content)
    yield

@pytest.fixture
def create_repository():
    start_path = os.path.abspath(os.getcwd())
    repo_name = 'git3_test_repository'
    print('Init repo')
    init(repo_name)
    os.chdir(repo_name)
    yield start_path, repo_name

@pytest.fixture
def cleanup_repository(create_repository):
    yield

    start_path, repo_name = create_repository
    print('Delete repo')
    os.chdir(start_path)
    shutil.rmtree(repo_name)