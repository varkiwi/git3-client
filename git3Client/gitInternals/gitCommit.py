import os, zlib
import ipfshttpclient

from .gitObject import read_object
from .gitTree import find_tree_objects, unpack_files_of_tree

from git3Client.utils.utils import write_file

IPFS_CONNECTION = '/dns4/ipfs.infura.io/tcp/5001/https'
client = ipfshttpclient.connect(IPFS_CONNECTION)

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
    all_commits = []
    parents = []
    #local_sha1 = get_local_master_hash()
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
    tree = client.get_json(commit_object['tree'])
    unpack_files_of_tree(repo_name, repo_name, tree, unpack_blobs)

def write_commit(commit_object, repo_name):
    author = '{} {}'.format(commit_object['author']['name'], commit_object['author']['email'])
    author_time = '{} {}'.format(commit_object['author']['date_seconds'], commit_object['author']['date_timestamp'])

    committer = '{} {}'.format(commit_object['committer']['name'], commit_object['committer']['email'])
    committer_time = '{} {}'.format(commit_object['committer']['date_seconds'], commit_object['committer']['date_timestamp'])
    lines = []
    
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
