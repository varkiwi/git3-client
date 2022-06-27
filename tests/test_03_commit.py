import pytest
import os
import shutil
import random

from pathlib import Path

from git3Client.gitCommands.commit import commit

class Test_Commit():
    
    def test_commit_no_repository(self, move_to_root_and_back):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            commit('test_commit')
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_commit_with_missing_config(self, prepare_local_repo_till_commit, delete_local_config_file):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            commit(message="1st commit message")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
    
    def test_successfully_commit(self, prepare_local_repo_till_commit):
        commit(message="1st commit message")

    