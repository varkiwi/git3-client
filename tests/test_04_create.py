import pytest
import os
import shutil
import random

from pathlib import Path

from git3Client.exceptions.NoRepositoryError import NoRepositoryError
from git3Client.gitCommands.create import create

class Test_Create():

    def test_unsucessful_create_missing_identity_file(self, patch_web3_provider, cleanup_repository, create_file, add_file_to_index, create_local_config_file_without_identity_file, commit_to_repo):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create("mumbai")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
    
    def test_failing_create_missing_funds(self, patch_web3_provider, cleanup_repository, create_file, add_file_to_index, create_local_config_file_with_identity_file, commit_to_repo):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create("mumbai")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_create(self, patch_web3_provider, patch_git_factory_for_create, cleanup_repository, create_file, add_file_to_index, create_local_config_file_with_identity_file, commit_to_repo):
        create("mumbai")
