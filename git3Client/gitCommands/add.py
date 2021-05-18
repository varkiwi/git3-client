import os, operator

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.gitInternals.fileMode import GIT_NORMAL_FILE_MODE
from git3Client.gitInternals.gitIndex import read_index, write_index
from git3Client.gitInternals.gitObject import hash_object
from git3Client.gitInternals.IndexEntry import IndexEntry

from git3Client.utils.utils import get_repo_root_path, read_file

def add(paths):
    """Add all file paths to git index."""
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)

    paths = [p.replace('\\', '/') for p in paths]
    all_entries = []
    # transfer paths to relative paths. Relative to the repository root
    # in case we are in a subdirectory and add a file
    paths = list(map(lambda path: os.path.relpath(os.path.abspath(path), repo_root_path), paths))

    try:
        all_entries = read_index()
    except errors.NoRepositoryError as nre:
        print(nre)
        exit(1)

    entries = [e for e in all_entries if e.path not in paths]
    for path in paths:
        file_path = repo_root_path + '/' + path
        try:
            data = read_file(file_path)
        except FileNotFoundError:
            print('fatal: pathspec \'{}\' did not match any files'.format(path))
            return
        sha1 = hash_object(data, 'blob')
        st = os.stat(file_path)
        #TODO: We will need to check for the file mode properly!
        mode = GIT_NORMAL_FILE_MODE
        flags = len(file_path.encode())
        assert flags < (1 << 12)
        # gets the relative path to the repository root folder for the index file
        relative_path = os.path.relpath(os.path.abspath(file_path), repo_root_path)
        entry = IndexEntry(
                int(st.st_ctime), 0, int(st.st_mtime), 0, st.st_dev,
                st.st_ino, mode, st.st_uid, st.st_gid, st.st_size,
                bytes.fromhex(sha1), flags, relative_path)
        entries.append(entry)
    entries.sort(key=operator.attrgetter('path'))
    write_index(entries)