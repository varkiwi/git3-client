import os
import operator

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.gitInternals.fileMode import GIT_NORMAL_FILE_MODE
from git3Client.gitInternals.gitIndex import read_index, write_index
from git3Client.gitInternals.gitObject import hash_object
from git3Client.gitInternals.IndexEntry import IndexEntry

from git3Client.utils.utils import get_repo_root_path, read_file

def add(paths):
    """
    Add all file paths to git index.

    Args:
        paths (List): List of files to be added to the git index.
    
    Raises:
        NoRepositoryError: If not git repository is found.
        FileNotFoundError: If a file to be added to the index is not found.
    """
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
    except NoRepositoryError as nre:
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
        # the spec says, that the mode is 32 bits and consists of 4 bits object type, 3 unused bits, 
        # and the 9 bits of the unix permission.
        # the 4 bits has the following binary value: 1000 (regular file), 1010 (symbolic link), and 1110 (gitlink)
        # the 9 bit unix permission can be 0755 and 0644 for regular files. Symbolic links and gitLinks have
        # value 0
        # TODO: We don't do this step poperly yet. We assume, that we use a regular file!
        # TODO: this seems to cover everything! We should have a proper check regarding this!
        mode = st.st_mode
        # get the length of the file
        flags = len(file_path.split('/')[-1].encode())
        #TODO: we have to check regarding the assume-valid flag what is means!
        #TODO: I believe this is the test of flags < 0xFFF. We need to make this part clearer!
        assert flags < (1 << 12)
        # gets the relative path to the repository root folder for the index file
        relative_path = os.path.relpath(os.path.abspath(file_path), repo_root_path)
        # st.st_ctime_ns % 1000000000 this part gets only the nanosecond fraction of the timestamp
        entry = IndexEntry(
                int(st.st_ctime), st.st_ctime_ns % 1000000000, int(st.st_mtime),
                st.st_mtime_ns % 1000000000, st.st_dev,
                st.st_ino, mode, st.st_uid, st.st_gid, st.st_size,
                bytes.fromhex(sha1), flags, relative_path)
        entries.append(entry)
    entries.sort(key=operator.attrgetter('path'))
    write_index(entries)