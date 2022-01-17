import difflib

from git3Client.gitInternals.gitCommit import find_commit_objects
from git3Client.gitInternals.gitIndex import get_status_workspace, read_index
from git3Client.gitInternals.gitObject import read_object

from git3Client.utils.utils import read_file, get_active_branch_hash

def diff(staged):
    """Show diff of files changed (between index and working copy)."""
    if staged:
        # Shows difference between index file and HEAD commit
        # read files from index
        entries_by_path = {e.path: e for e in read_index()}
        # read files from top most commit
        local_sha1 = get_active_branch_hash()
        print('local sha1', local_sha1)
        commits = find_commit_objects(local_sha1)
        print('Commits', commits)
    else:
        # Show difference between working tree and index file
        changed, _, deleted = get_status_workspace()
        # gets all entries from the index file and puts those into a dict
        # the path is the key and IndexEntry is the value
        entries_by_path = {e.path: e for e in read_index()}

        changed.extend(deleted)

        for i, path in enumerate(changed):
            sha1 = entries_by_path[path].sha1.hex()
            obj_type, data = read_object(sha1)

            assert obj_type == 'blob'

            # content from file which is stored in .git/objects/
            index_lines = data.decode().splitlines()
            
            try:
                # content from file which is stored in the working directory
                working_lines = read_file(path).decode().splitlines()
                work_tree_path = path
            except FileNotFoundError:
                # when this part is triggered, it means that the file has been 
                # deleted from the working tree
                working_lines = []
                work_tree_path = '/dev/null'

            
            diff_lines = difflib.unified_diff(
                    index_lines, working_lines,
                    '{} (index)'.format(path),
                    '{} (working copy)'.format(work_tree_path),
                    lineterm='')
            for line in diff_lines:
                print(line)
            if i < len(changed) - 1:
                print('-' * 70)