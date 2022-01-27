import os, zlib

from .fileMode import GIT_TREE_MODE
from .gitObject import read_object
from .gitTree import find_tree_objects, unpack_files_of_tree, read_tree

from git3Client.dlt.storageClient import getStorageClient

from git3Client.utils.utils import write_file

def find_commit_objects(commit_sha1):
    """Return set of SHA-1 hashes of all objects in this commit (recursively),
    its tree, its parents, and the hash of the commit itself.
    """
    objects = {commit_sha1}
    obj_type, commit = read_object(commit_sha1)
    assert obj_type == 'commit'
    lines = commit.decode().splitlines()
    tree = next(l[5:45] for l in lines if l.startswith('tree '))
    objects.update(find_tree_objects(tree))
    parents = (l[7:47] for l in lines if l.startswith('parent '))
    for parent in parents:
        objects.update(find_commit_objects(parent))
    return objects

def get_all_local_commits(commit_hash):
    """
    Returns a list contains all hashes of the local commits
    starting from the given parameter commit_hash
    """
    if commit_hash == None:
        return []

    all_commits = []
    parents = []

    all_commits.append(commit_hash)
    obj_type, commit = read_object(commit_hash)
    lines = commit.decode().splitlines()
    for l in lines:
        if l.startswith('parent '):
            parents.append(l[7:47])
    while len(parents) > 0:
        parent = parents.pop()
        all_commits.append(parent)
        obj_type, commit = read_object(parent)
        lines = commit.decode().splitlines()
        for l in lines:
            if l.startswith('parent '):
                parents.append(l[7:47])
    return all_commits

def unpack_files_of_commit(repo_name, commit_object, unpack_blobs):
    """
    Takes a commit object and unpacks the trees. Might also unpack blob if the unpack_blobs parameter is set to true.
    repo_name is used in order to know where to find the .git directory and the path to write is used to unpack blobs
    and write the content into a file. Commit_object has to be of the ipfs structure.
    """
    write_commit(commit_object, repo_name)
    client = getStorageClient()
    tree = client.get_json(commit_object['tree'])
    unpack_files_of_tree(repo_name, repo_name, tree, unpack_blobs)

def write_commit(commit_object, repo_name):
    author = '{} {}'.format(commit_object['author']['name'], commit_object['author']['email'])
    author_time = '{} {}'.format(commit_object['author']['date_seconds'], commit_object['author']['date_timestamp'])

    committer = '{} {}'.format(commit_object['committer']['name'], commit_object['committer']['email'])
    committer_time = '{} {}'.format(commit_object['committer']['date_seconds'], commit_object['committer']['date_timestamp'])
    lines = []
    
    client = getStorageClient()
    tree_obj = client.get_json(commit_object['tree'])

    lines = ['tree ' + tree_obj['sha1']]
    if commit_object['parents']:
        for parent in commit_object['parents']:
            parent_obj = client.get_json(parent)
            remote_commit_sha1 = parent_obj['sha1']
            lines.append('parent ' + remote_commit_sha1)
    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(committer, committer_time))
    lines.append('')
    lines.append(commit_object['commit_message'])
    lines.append('')
    data = '\n'.join(lines).encode()
    header = '{} {}'.format('commit', len(data)).encode()
    full_data = header + b'\x00' + data

    path = os.path.join(repo_name, '.git', 'objects', commit_object['sha1'][:2], commit_object['sha1'][2:])
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_file(path, zlib.compress(full_data))

def read_commit_entries(commit_hash):
    """
    Reads all files which are stored by the commit with the given hash.
    Returns a dict of paths relative to the repository root with their hash.
    """
    commit_entries = {}
    # read commit
    obj_type, commit = read_object(commit_hash)
    assert obj_type == 'commit'
    objects = {commit_hash}
    lines = commit.decode().splitlines()

    # read tree hashes in
    tree = next(l[5:45] for l in lines if l.startswith('tree '))
    
    # read tree content
    entries = read_tree(tree)
    i = 0
    # and get all entries from the tree
    while i < len(entries):
        if entries[i][0] == GIT_TREE_MODE:
            sub_tree = read_tree(entries[i][2])
            for sub_entry in sub_tree:
                entries.append((
                    sub_entry[0],
                    '{}/{}'.format(entries[i][1], sub_entry[1]),
                    sub_entry[2],
                ))
            del entries[i]
        else:
            commit_entries[entries[i][1]] = entries[i][2]
            i += 1

    return commit_entries
