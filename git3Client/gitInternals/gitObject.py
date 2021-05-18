import os, zlib, hashlib

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

# from .gitTree import read_tree
from .fileMode import GIT_NORMAL_FILE_MODE, GIT_TREE_MODE

from git3Client.utils.utils import get_repo_root_path, read_file, write_file

def find_missing_objects(local_sha1, remote_sha1):
    """Return set of SHA-1 hashes of objects in local commit that are missing
    at the remote (based on the given remote commit hash).
    """
    from .gitCommit import find_commit_objects
    local_objects = find_commit_objects(local_sha1)
    if remote_sha1 is None:
        return local_objects
    remote_objects = find_commit_objects(remote_sha1)
    return local_objects - remote_objects

def find_object(sha1_prefix):
    """Find object with given SHA-1 prefix and return path to object in object
    store, or raise ValueError if there are no objects or multiple objects
    with this prefix.
    """
    if len(sha1_prefix) < 2:
        raise ValueError('hash prefix must be 2 or more characters')
    repo_root_path = get_repo_root_path()
    obj_dir = os.path.join(repo_root_path, '.git', 'objects', sha1_prefix[:2])
    rest = sha1_prefix[2:]
    objects = [name for name in os.listdir(obj_dir) if name.startswith(rest)]
    if not objects:
        raise ValueError('object {!r} not found'.format(sha1_prefix))
    if len(objects) >= 2:
        raise ValueError('multiple objects ({}) with prefix {!r}'.format(
                len(objects), sha1_prefix))
    return os.path.join(obj_dir, objects[0])

def hash_object(data, obj_type, write=True):
    """Compute hash of object data of given type and write to object store if
    "write" is True. Return SHA-1 object hash as hex string.
    """
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        raise NoRepositoryError(nre)
    header = '{} {}'.format(obj_type, len(data)).encode()
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    if write:
        path = os.path.join(repo_root_path, '.git', 'objects', sha1[:2], sha1[2:])
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, zlib.compress(full_data))
    return sha1

def read_object(sha1_prefix):
    """Read object with given SHA-1 prefix and return tuple of
    (object_type, data_bytes), or raise ValueError if not found.
    """
    path = find_object(sha1_prefix)
    full_data = zlib.decompress(read_file(path))
    nul_index = full_data.index(b'\x00')
    header = full_data[:nul_index]
    obj_type, size_str = header.decode().split()
    size = int(size_str)
    data = full_data[nul_index + 1:]
    assert size == len(data), 'expected size {}, got {} bytes'.format(
            size, len(data))
    return (obj_type, data)

def unpack_object(object_hash, repo_path, path_to_write):
    """
    Takes an tree sha1 hash and read the local object. It iterates over the entries and writes the content of blobs
    to the repository. In case it comes across another tree object, it makes a recursive call.
    """
    #TODO: have to make it more robust. What if it is not a tree object?
    from .gitTree import read_tree

    entries = read_tree(object_hash)
    for entry in entries:
        if entry[0] == GIT_NORMAL_FILE_MODE:
            object_path = os.path.join(repo_path, '.git/objects', entry[2][:2], entry[2][2:])
            full_data = zlib.decompress(read_file(object_path))
            nul_index = full_data.index(b'\x00')
            header = full_data[:nul_index]
            obj_type, size_str = header.decode().split()
            size = int(size_str)
            data = full_data[nul_index + 1:]
            data_path = os.path.join(path_to_write, entry[1])
            if not os.path.exists(data_path):
                os.makedirs(os.path.dirname(data_path), exist_ok=True)
            write_file(data_path, data)
        elif entry[0] == GIT_TREE_MODE:
            unpack_object(entry[2], repo_path, os.path.join(path_to_write, entry[1]))
