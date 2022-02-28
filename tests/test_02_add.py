import pytest
import os
import shutil

from git3Client.gitCommands.init import init

class Test_Add():
    repo_name = 'test_repo'

    @pytest.fixture(scope='module', autouse=True)
    def run_before_and_after_tests(self):
        start_path = os.path.abspath(os.getcwd())

        init(self.repo_name)
        os.chdir(self.repo_name)

        # execute tests
        yield

        os.chdir(start_path)

        try:
            shutil.rmtree(self.repo_name)
            # shutil.rmtree(self.indir_repo_name)
        except OSError as e:
            print("Error: %s : %s" % (self.repo_name, e.strerror))
    
    
    def test_add(self):
        # TODO: write file and add to repo
        assert 1 + 1 == 2