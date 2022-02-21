import pytest
import shutil
import os.path
import glob

from git3Client.gitCommands.init import init

class Test_Init():
    repo_name = 'test_repo'
    indir_repo_name = 'indir_repo'

    @pytest.fixture(scope='module', autouse=True)
    def run_before_and_after_tests(self):
        start_path = os.path.abspath(os.getcwd())
        
        # execute tests
        yield

        os.chdir(start_path)

        try:
            shutil.rmtree(self.repo_name)
            shutil.rmtree(self.indir_repo_name)
        except OSError as e:
            print("Error: %s : %s" % (self.repo_name, e.strerror))

    def test_create_repo(self):
        result = init(self.repo_name)
        assert result is True
        assert os.path.isdir(os.path.join(self.repo_name, '.git'))

        directories = ['objects', 'refs', 'refs/heads']

        for dir in directories:
            assert os.path.isdir(os.path.join(self.repo_name, '.git', dir))
        
        # since the repo has been just created, there shouldn't be any files in the heads dir
        assert  len(glob.glob(os.path.join(self.repo_name, '.git', 'refs', 'heads', '*'))) == 0

        # check that the head points to the main branch
        with open(os.path.join(self.repo_name, '.git', 'HEAD'), 'r') as f:
            assert f.read() == 'ref: refs/heads/main'

    def test_create_another_repo(self):
        result = init(self.repo_name)
        assert result is False

    def test_create_repo_in_dir(self):
        os.mkdir(self.indir_repo_name)
        os.chdir(self.indir_repo_name)
        result = init()
        assert result is True

    def test_create_repo_in_existing_repo(self):
        result = init()
        assert result is False
        
