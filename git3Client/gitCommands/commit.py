import os, time

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.gitInternals.gitIndex import read_index
from git3Client.gitInternals.gitObject import hash_object
from git3Client.gitInternals.gitTree import write_tree

from git3Client.utils.utils import get_active_branch_hash, get_repo_root_path, get_value_from_config_file, read_file, write_file, get_current_branch_name

def commit(message: str, author: str = None, parent1: str = None, parent2: str = None) -> str :
    """
    Commit the current state of the index to active branch with given message.
    Returns the hash of the commit object.

    Parameters:
        message (str): The message for the commit.
        author (str): The author of the commit.
        parent1 (str): The first parent of the commit.
        parent2 (str): The second parent of the commit.
    
    Returns:
        Return hash of commit object.
    """
    try:
        index = read_index()
        # we are working on write tree
        tree =  hash_object(b''.join(write_tree(index)), 'tree')
    except NoRepositoryError as nre:
        print(nre)
        exit(1)
 
    if parent1 == None:
        # even the get_active_branch_hash throws a NoRepositoryError
        # we don't have to catch it, since we are doing it already further up in the code
        # If there is no repository, we won't reach this code here anyways.
        parent = get_active_branch_hash()
    else:
        parent = parent1

    # check if there is a MERGE_HEAD file. If there is, parent2 is set to the sha1 hash
    merge_head_path = os.path.join(get_repo_root_path(), '.git', 'MERGE_HEAD')

    if os.path.exists(merge_head_path):
        parent2 = read_file(merge_head_path).decode().strip()

    if author is None:
        # get_value_from_config_file throws a NoRepositoryError
        # but the same as above, we don't have to catch it
        user_name = get_value_from_config_file('name')
        user_email = get_value_from_config_file('email')
            
        author = '{} <{}>'.format(user_name, user_email)

    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone

    author_time = '{} {}{:02}{:02}'.format(
            timestamp,
            '+' if utc_offset > 0 else '-',
            abs(utc_offset) // 3600,
            (abs(utc_offset) // 60) % 60)

    lines = ['tree ' + tree]
    if parent:
        lines.append('parent ' + parent)
    if parent2 != None:
        lines.append('parent ' + parent2)
    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(author, author_time))
    lines.append('')
    lines.append(message)
    lines.append('')
    data = '\n'.join(lines).encode()
    sha1 = hash_object(data, 'commit')

    repo_root_path = get_repo_root_path()
    activeBranch = get_current_branch_name()
    
    branch_path = os.path.join(repo_root_path, '.git', 'refs', 'heads', activeBranch)
    write_file(branch_path, (sha1 + '\n').encode())

    # remove the merge files from the .git directory if committed
    if parent2 != None and os.path.exists(merge_head_path):
        os.remove(merge_head_path)
        merge_mode_path = merge_head_path.replace('MERGE_HEAD', 'MERGE_MODE')
        os.remove(merge_mode_path)
        merge_msg_path = merge_head_path.replace('MERGE_HEAD', 'MERGE_MSG')
        os.remove(merge_msg_path)
    
    #TODO: git returns the number of files added and changed. Would be good too
    print('[{} {}] {}'.format(activeBranch, sha1[:7], message))
    print('Author: {}'.format(author))
    return sha1