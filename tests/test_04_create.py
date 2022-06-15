import pytest
import os
import shutil
import random

from pathlib import Path

from git3Client.exceptions.NoRepositoryError import NoRepositoryError
from git3Client.gitCommands.create import create

# we can't reach 100% coverage since we are currently not able to figure out how to mock 
# web3.eth.waitForTransactionReceipt(). The only idea we have is to put it into a separate function
# and use the wrapper function in create. Then we are able to mock it.

class Test_Create():

    def test_unsuccessful_create_missing_identity_file(self, patch_web3_provider, prepare_local_repo_till_create, remove_identify_path_from_config):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create("mumbai")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
    
    def test_failing_create_missing_funds(self, patch_web3_provider, prepare_local_repo_till_create, remove_identify_path_from_config):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create("mumbai")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_unsuccessful_create_wrong_text_in_name_file(self,
            patch_web3_provider,
            patch_git_factory_for_create,
            prepare_local_repo_till_create,
            change_content_of_name_file
        ):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create("mumbai")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_unsuccessful_create_missing_repo_name_in_name_file(self,
            patch_web3_provider,
            patch_git_factory_for_create,
            prepare_local_repo_till_create,
            change_repository_name_in_name_file
        ):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create("mumbai")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_unsuccessful_missing_gas_price(
        self,
        patch_web3_provider,
        patch_git_factory_for_create,
        prepare_local_repo_till_create,
        patch_get_current_gas_price_for_create
    ):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            create("mumbai")
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_create(self, patch_web3_provider, patch_git_factory_for_create, prepare_local_repo_till_create):
        create("mumbai")
