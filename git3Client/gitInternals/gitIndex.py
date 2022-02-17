import struct
import os
import hashlib

from .gitObject import hash_object
from .IndexEntry import IndexEntry

from git3Client.gitInternals.gitCommit import read_commit_entries
from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import get_repo_root_path, read_file, write_file, get_active_branch_hash

def get_status_commit():
    """
    Get status of HEAD commit, return tuple of
    (changed_paths, new_paths, deleted_paths).
    """
    local_sha1 = get_active_branch_hash()
    commit_entries = read_commit_entries(local_sha1)
    commit_paths = set(commit_entries)

    entries_by_path = {e.path: e for e in read_index()}
    entry_paths = set(entries_by_path)

    changed = {p for p in (commit_paths & entry_paths)
            if commit_entries[p] != entries_by_path[p].sha1.hex()}
    deleted = commit_paths - entry_paths
    new = entry_paths - commit_paths
    return (sorted(changed), sorted(new), sorted(deleted))

def get_status_workspace():
    """
    Get status of working copy, return tuple of
    (changed_paths, new_paths, deleted_paths).
    """
    paths = set()
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:
            path = os.path.join(root, file)
            path = path.replace('\\', '/')
            if path.startswith('./'):
                path = path[2:]
            paths.add(path)
    entries_by_path = {e.path: e for e in read_index()}
    entry_paths = set(entries_by_path)
    
    changed = {p for p in (paths & entry_paths)
               if hash_object(read_file(p), 'blob', write=False) !=
                  entries_by_path[p].sha1.hex()}
    new = paths - entry_paths
    deleted = entry_paths - paths
    return (sorted(changed), sorted(new), sorted(deleted))


def is_stage_empty():
    """
    Comapres the entries from the last commit object with the ones in the index file. If there is a difference, 
    the stage is not empty. If there is a difference, the stage is not empty
    """
    from .gitObject import read_object
    from .gitTree import get_subtree_entries

    local_sha1 = get_active_branch_hash()
    obj_type, data = read_object(local_sha1)
    assert obj_type == 'commit'
    splitted_commit = data.decode().splitlines()
    #We want to get the tree hash
    for line in splitted_commit:
        if line.startswith('tree '):
            tree_sha1 = line[5:]
            break
    #so that we can read the top tree object
    committed_entries = []
    get_subtree_entries(tree_sha1, '', committed_entries)
    index = read_index()
    for indexEntry in index:
        # found is used for entries which have not been committed yet. 
        found = False
        for treeEntry in committed_entries:
            if treeEntry[0] == indexEntry.path: 
                if treeEntry[1] != indexEntry.sha1.hex():
                    return False
                found = True
        # if found is false, the entry has not been committed yet and there is a difference between staging and commit
        if not found:
            return False
    return True

def read_index():
    """Read git index file and return list of IndexEntry objects."""
    try:
        repo_root_path = get_repo_root_path()
        data = read_file(os.path.join(repo_root_path, '.git', 'index'))
    except FileNotFoundError:
        return []
    except NoRepositoryError as nre:
        raise NoRepositoryError(nre)
    digest = hashlib.sha1(data[:-20]).digest()
    assert digest == data[-20:], 'invalid index checksum'
    signature, version, num_entries = struct.unpack('!4sLL', data[:12])
    assert signature == b'DIRC', \
            'invalid index signature {}'.format(signature)
    assert version == 2, 'unknown index version {}'.format(version)
    entry_data = data[12:-20]
    entries = []
    i = 0
    while i + 62 < len(entry_data):
        fields_end = i + 62
        fields = struct.unpack('!LLLLLLLLLL20sH', entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields + (path.decode(),)))
        entries.append(entry)
        entry_len = ((62 + len(path) + 8) // 8) * 8
        i += entry_len
    assert len(entries) == num_entries
    return entries

def write_index(entries):
    """Write list of IndexEntry objects to git index file."""
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        raise NoRepositoryError(nre)
    packed_entries = []

    for entry in entries:
        entry_head = struct.pack('!LLLLLLLLLL20sH',
                entry.ctime_s, entry.ctime_n, entry.mtime_s, entry.mtime_n,
                entry.dev, entry.ino & 0xFFFFFFFF, entry.mode, entry.uid, entry.gid,
                entry.size, entry.sha1, entry.flags)
        path = entry.path.encode()
        # from ctime to object name it is 62 bytes
        # this // is integer devison
        length = ((62 + len(path) + 8) // 8) * 8
        packed_entry = entry_head + path + b'\x00' * (length - 62 - len(path))
        packed_entries.append(packed_entry)
    header = struct.pack('!4sLL', b'DIRC', 2, len(entries))
    all_data = header + b''.join(packed_entries)
    digest = hashlib.sha1(all_data).digest()
    write_file(os.path.join(repo_root_path, '.git', 'index'), all_data + digest)

