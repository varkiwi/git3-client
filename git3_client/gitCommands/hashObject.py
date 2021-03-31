import os

#from git3_client.exceptions.NoRepositoryError import NoRepositoryError

#from git3_client.gitInternals.fileMode import GIT_NORMAL_FILE_MODE
#from git3_client.gitInternals.gitIndex import read_index, write_index
from git3_client.gitInternals.gitObject import hash_object
#from git3_client.gitInternals.IndexEntry import IndexEntry

# from git3_client.utils.utils import get_repo_root_path, read_file

def hashObject(data, obj_type, write=True):
    try:
        sha1 = hash_object(data, obj_type, write)
        print(sha1)
    except NoRepositoryError as nre:
        print(nre)