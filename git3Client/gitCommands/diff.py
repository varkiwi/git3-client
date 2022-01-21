import difflib

from git3Client.gitInternals.gitCommit import find_commit_objects, read_commit_entries
from git3Client.gitInternals.gitIndex import get_status_workspace, get_status_commit, read_index
from git3Client.gitInternals.gitObject import read_object

from git3Client.utils.utils import read_file, get_active_branch_hash

def diff(staged):
    """Show diff of files changed (between index and working copy)."""
    # checks if there is a diff between index and HEAD
    if staged:
        # we don't use deleted for now, since we don't have git3 rm command
        changed, new, deleted = get_status_commit()

        entries_by_path = {e.path: e for e in read_index()}
        local_sha1 = get_active_branch_hash()
        commit_entries = read_commit_entries(local_sha1)

        changed.extend(new)

        for i, path in enumerate(changed):
            sha1 = entries_by_path[path].sha1.hex()
            obj_type, data = read_object(sha1)

            assert obj_type == 'blob'
            # content from file which is stored in .git/objects/
            index_lines = data.decode().splitlines()

            # if the path is not in the commit_entries dict, it means, that it is 
            # available in the index but has not been committed yet
            if path in commit_entries:
                commit_path = path
                sha1 = commit_entries[path]
                obj_type, data = read_object(sha1)

                assert obj_type == 'blob'
                # content from file which is stored in .git/objects/
                commit_lines = data.decode().splitlines()
            else:
                commit_path = '/dev/null'
                commit_lines = ''

            diff_lines = difflib.unified_diff(
                    commit_lines, index_lines,
                    '{} (commit)'.format(commit_path),
                    '{} (index)'.format(path),
                    lineterm='')
            for line in diff_lines:
                print(line)
            if i < len(changed) - 1:
                print('-' * 70)
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