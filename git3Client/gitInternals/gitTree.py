import binascii, os, zlib, stat

from .IndexEntry import IndexEntry
from .fileMode import GIT_NORMAL_FILE_MODE, GIT_TREE_MODE
from .gitObject import read_object

from git3Client.dlt.storageClient import getStorageClient

from git3Client.utils.utils import write_file

def find_tree_objects(tree_sha1):
    """Return set of SHA-1 hashes of all objects in this tree (recursively),
    including the hash of the tree itself.
    """
    objects = {tree_sha1}
    for mode, path, sha1 in read_tree(sha1=tree_sha1):
        if stat.S_ISDIR(mode):
            objects.update(find_tree_objects(sha1))
        else:
            objects.add(sha1)
    return objects

def get_subtree_entries(tree_sha1, path, entries):
    """
    Get's all entries from a tree and writes the path and the hash into entries. 
    """
    tree = read_tree(tree_sha1)
    for entry in tree:
        if entry[0] == GIT_NORMAL_FILE_MODE:
            entries.append((os.path.join(path, entry[1]), entry[2]))
        elif entry[0] == GIT_TREE_MODE:
            get_subtree_entries(entry[2], os.path.join(path, entry[1]), entries)

def read_tree(sha1=None, data=None):
    """Read tree object with given SHA-1 (hex string) or data, and return list
    of (mode, path, sha1) tuples.
    """
    if sha1 is not None:
        obj_type, data = read_object(sha1)
        assert obj_type == 'tree'
    elif data is None:
        raise TypeError('must specify "sha1" or "data"')
    i = 0
    entries = []
    for _ in range(1000):
        end = data.find(b'\x00', i)
        if end == -1:
            break
        mode_str, path = data[i:end].decode().split()
        mode = int(mode_str, 8)
        digest = data[end + 1:end + 21]
        entries.append((mode, path, digest.hex()))
        i = end + 1 + 20
    return entries

def unpack_files_of_tree(repo_name, path_to_write, tree, unpack_blobs):
    """
    Gets a tree object and unpacks the references. The content of the blobs are written into a file if unpack_blobs
    is set true. Otherwise only the git objects are created
    """
    tree_entries = []
    client = getStorageClient()
    for entry in tree['entries']:
        if entry['mode'] == GIT_NORMAL_FILE_MODE:
            blob = client.get_json(entry['cid'])
            # write content to the file if wanted
            if unpack_blobs:
                path = os.path.join(path_to_write, entry['name'])
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                write_file(path, blob['content'].encode())
            # time to create blob object if doesn't exists yet
            path = os.path.join(repo_name, '.git', 'objects', blob['sha1'][:2], blob['sha1'][2:])
            if not os.path.exists(path):
                header = '{} {}'.format('blob', len(blob['content'])).encode()
                full_data = header + b'\x00' + blob['content'].encode()
                os.makedirs(os.path.dirname(path), exist_ok=True)
                write_file(path, zlib.compress(full_data))
            # creating entry for tree object
            mode_path = '{:o} {}'.format(GIT_NORMAL_FILE_MODE, entry['name']).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(blob['sha1'])
            tree_entries.append(tree_entry)
        elif entry['mode'] == GIT_TREE_MODE:
            sub_tree = client.get_json(entry['cid'])
            unpack_files_of_tree(repo_name, "{}/{}".format(path_to_write, entry['name']), sub_tree, unpack_blobs)
            mode_path = '{:o} {}'.format(GIT_TREE_MODE, entry['name']).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(sub_tree['sha1'])
            tree_entries.append(tree_entry)

    data = b''.join(tree_entries)
    obj_type = 'tree'
    header = '{} {}'.format(obj_type, len(data)).encode()
    full_data = header + b'\x00' + data
    path = os.path.join(repo_name, '.git', 'objects', tree['sha1'][:2], tree['sha1'][2:])
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_file(path, zlib.compress(full_data))

def write_tree(index):
    """Write a tree object from the current index entries."""
    tree_entries = []
    tree_to_process = {'.': []}
    indexEntries = index #read_index()

    for entry in indexEntries:
        # we are going to create a dict, where the repo hierarchy is shown and used 
        # to create the git objects
        splitted_path = entry.path.split('/')
        filename = splitted_path.pop()
        if len(splitted_path) == 0:
            tree_to_process['.'].append(entry)
        else:
            previous = '.'
            for dir_name in splitted_path:
                if previous in tree_to_process:
                    if dir_name not in tree_to_process[previous]:
                        tree_to_process[previous].append(dir_name)
                else:
                    tree_to_process[previous] = [dir_name]
                previous = dir_name
            if previous in tree_to_process:
                tree_to_process[previous].append(entry)
            else:
                tree_to_process[previous] = [entry]

    for entry in tree_to_process['.']:
        if isinstance(entry, IndexEntry):
            mode_path = '{:o} {}'.format(entry.mode, entry.path).encode()
            tree_entry = mode_path + b'\x00' + entry.sha1
        elif isinstance(entry, str):
            tree_hash = write_subtree(tree_to_process, entry)
            mode_path = '{:o} {}'.format(GIT_TREE_MODE, entry).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(tree_hash)

        tree_entries.append(tree_entry)
    return tree_entries

def write_subtree(indexEntries, dirName):
    """
    Create a subtree for a subdirectories which is going to be added to the normal tree
    """
    from .gitObject import hash_object
    
    tree_entries = []
    for entry in indexEntries[dirName]:
        if isinstance(entry, IndexEntry):
            mode_path = '{:o} {}'.format(entry.mode, entry.path.split('/')[-1]).encode()
            tree_entry = mode_path + b'\x00' + entry.sha1
        elif isinstance(entry, str):
            tree_hash = write_subtree(indexEntries, entry)
            mode_path = '{:o} {}'.format(GIT_TREE_MODE, entry.split('/')[-1]).encode()
            tree_entry = mode_path + b'\x00' + binascii.unhexlify(tree_hash)

        tree_entries.append(tree_entry)
    return hash_object(b''.join(tree_entries), 'tree')
