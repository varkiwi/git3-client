import os

#from git3Client.exceptions.NoRepositoryError import NoRepositoryError

#from git3Client.gitInternals.fileMode import GIT_NORMAL_FILE_MODE
#from git3Client.gitInternals.gitIndex import read_index, write_index
from git3Client.gitInternals.gitObject import hash_object
#from git3Client.gitInternals.IndexEntry import IndexEntry

# from git3Client.utils.utils import get_repo_root_path, read_file

def hashObject(data, obj_type, write=True):
    try:
        sha1 = hash_object(data, obj_type, write)
        print(sha1)
    except NoRepositoryError as nre:
        print(nre)