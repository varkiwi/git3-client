import pytest
import os
import shutil
import random

from pathlib import Path

from git3Client.exceptions.NoRepositoryError import NoRepositoryError
from git3Client.gitCommands.push import push

# we can't reach 100% coverage since we are currently not able to figure out how to mock 
# web3.eth.waitForTransactionReceipt(). The only idea we have is to put it into a separate function
# and use the wrapper function in create. Then we are able to mock it.

class Test_Push():

    def test_unsuccessful_push_missing_repository(self, prepare_local_repo_till_create):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            push()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
    
    def test_successful_push(self, prepare_local_repo_till_create, patch_push_data_to_storage_for_push, patch_check_if_repo_created_for_push, patch_push_new_cid_for_push):
        push()
