import difflib, os, re

from git3Client.dlt.contract import get_factory_contract

from git3Client.gitCommands.add import add
from git3Client.gitCommands.commit import commit

from git3Client.gitInternals.gitCommit import get_all_local_commits
from git3Client.gitInternals.gitObject import read_object, unpack_object
from git3Client.gitInternals.gitTree import get_subtree_entries

from git3Client.utils.utils import get_repo_root_path, get_active_branch_hash, read_repo_name, read_file, write_file, get_current_branch_name

def merge(source_branch):
    """
    Merges two branches. If the source_branch parameter is set, the source branch is merged into the current branch.
    If the parameter is not set, a merge from FETCH_HEAD is performed.
    """
    had_conflict = False
    repo_root_path = get_repo_root_path()
    # if no source branch for merge is give, we go through the FETCH_HEAD file
    if source_branch is None:
        fetch_head_path = os.path.join(repo_root_path, '.git/FETCH_HEAD')
        if not os.path.exists(fetch_head_path):
            print('Nothing to merge. Have you called fetch before?')
            return
        fetch_head_content = read_file(fetch_head_path).decode('utf-8')

        findings = re.findall('^([ABCDEFabcdef0-9]+)\s+branch (\w|\')+', fetch_head_content)
        if len(findings) == 0:
            remote_sha1 = None
        else:
            remote_sha1 = findings[0][0]
    else:
        # otherwise we are looking for the refs file first.
        source_branch_head_path = os.path.join(repo_root_path, '.git/refs/heads/', source_branch)
        if not os.path.exists(source_branch_head_path):
            # if the refs file does not exist, we are having a look if the packed-refs file exits
            # git doesn't use the FETCH_HEAD file when a branch name is given!
            packed_refs_path = os.path.join(repo_root_path, '.git/packed-refs')
            if not os.path.exists(packed_refs_path):
                # if not, we are printing an error message and return
                remote_sha1 = None
            # otherwise we read the packed-refs file
            packed_refs_content = read_file(packed_refs_path).decode('utf-8')
            # and read the commit hash
            findings = re.findall('([ABCDEFabcdef0-9]*) refs\/remotes\/origin\/{}'.format(source_branch), packed_refs_content)
            if len(findings) == 0:
                remote_sha1 = None
            else:
                remote_sha1 = findings[0]
        else:
            # if the file exists, we read the sha1 from it
            remote_sha1 = read_file(source_branch_head_path).decode('utf-8')

    if remote_sha1 is None:
        print('merge: {} - not something we can merge'.format(source_branch))
        exit(1)

    activeBranch = get_current_branch_name()
    local_sha1 = get_active_branch_hash()

    remote_sha1 = remote_sha1.strip()
    local_sha1 = local_sha1.strip()

    if remote_sha1 == local_sha1:
       return
    remote_commits = get_all_local_commits(remote_sha1)
    local_commits = get_all_local_commits(local_sha1)

    difference = set(local_commits) - set(remote_commits)
    
    if len(difference) == 0:
        #fast forward strategy
        path = os.path.join(repo_root_path, '.git/refs/heads/{}'.format(activeBranch))
        write_file(path, "{}\n".format(remote_sha1).encode())
        obj_type, commit_data = read_object(remote_sha1.strip())
        tree_sha1 = commit_data.decode().splitlines()[0][5:45]
        unpack_object(tree_sha1, repo_root_path, repo_root_path)
        return

    # non fast forward strategy
    intersection = set(local_commits).intersection(remote_commits)
    for commit_hash in remote_commits:
        if commit_hash in intersection:
            ancestor = commit_hash
            break

    # We need to find an ancestor and run 3-way merge on these files!
    # than we need to create a new tree and a commit object with 2 parents
    
    obj_type, ancestor_commit = read_object(ancestor)
    obj_type, a_commit = read_object(local_commits[0])
    obj_type, b_commit = read_object(remote_commits[0])
    # list for the 3 branches
    ancestor_entries = []
    a_entries = []
    b_entries = []
    # here we get a list in the following format [(filename, sha1), (filename, sha2), ...]
    get_subtree_entries(ancestor_commit.splitlines()[0][5:45].decode(), '', ancestor_entries)
    get_subtree_entries(a_commit.splitlines()[0][5:45].decode(), '', a_entries)
    get_subtree_entries(b_commit.splitlines()[0][5:45].decode(), '', b_entries)

    merge = {}
    # wo go through each list and use the filename as key and create a list of hashed
    for e in ancestor_entries:
        if e[0] not in merge:
            merge[e[0]] = [e[1]]

    for e in a_entries:
        if e[0] not in merge:
            merge[e[0]] = [None, e[1]]
        else:
            merge[e[0]].append(e[1])

    for e in b_entries:
        if e[0] not in merge:
            merge[e[0]] = [None, None, e[1]]
        else:
            merge[e[0]].append(e[1])

    # if all hashes are the same, there is nothing we have to do
    # In case the second and third entry are not None, but the first one is: I am not sure if this case actually is possible
    conflict_files = []
    for f in merge:
        if len(merge[f]) == 2 and merge[f][0] != merge[f][1]:
            # if there are only two entries, the remote branch does not have the file and we will add it to the repository
            obj_type, data = read_object(merge[f][1])
            path = os.path.join(repo_root_path, f)
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, data)
        elif merge[f][0] == None and merge[f][1] == None:
            # if there are three entries and the first two entries are none, the local repository does not have the file
            # so we add it.
            obj_type, data = read_object(merge[f][2])
            path = os.path.join(repo_root_path, f)
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
            write_file(path, data)
        elif len(set(merge[f])) == 3:
            # all entries are different, so 3-way merge
            # read the content of each file
            obj_type, base_data = read_object(merge[f][0])
            obj_type, local_data = read_object(merge[f][1])
            obj_type, remote_data = read_object(merge[f][2])
            #do the 3-way merge
            had_conflict, merged_lines = three_way_merge(
                base_data.decode().splitlines(),
                local_data.decode().splitlines(),
                remote_data.decode().splitlines(),
                "HEAD",
                merge[f][2]
            )
            # writing the merged lines into the file
            with open(os.path.join(repo_root_path, f), 'w') as file:
                for line in merged_lines:
                    file.write('{}\n'.format(line))
            if had_conflict:
                # adding file to list, so that we don't add it to the index
                conflict_files.append(f)
                path = os.path.join(repo_root_path, '.git/ORIG_HEAD')
                write_file(path, '{}\n'.format(local_sha1).encode())
                path = os.path.join(repo_root_path, '.git/MERGE_HEAD')
                write_file(path, '{}\n'.format(fetch_head[:40].decode()).encode())
                path = os.path.join(repo_root_path, '.git/MERGE_MODE')
                write_file(path, b'')
                path = os.path.join(repo_root_path, '.git/MERGE_MSG')
                if os.path.exists(path):
                    # append file name to conflict
                    with open(path, 'a') as f:
                        f.write('# \t{}'.format(f))
                else:
                    repo_name = read_repo_name()
                    if not repo_name.startswith('location:'):
                        # Need to check if the return is handled by the calling function
                        print('.git/name file has an error. Exiting...')
                        return False
                    tmp = repo_name.split('location:')[1].split(':')
                    network = tmp[0].strip()
                    user_key = tmp[1].strip()
                    git_factory = get_factory_contract(network)

                    repository = git_factory.functions.getRepository(user_key).call()
                    write_file(
                        path,
                        'Merge branch \'{}\' of {} into {}\n\n# Conflicts\n# \t{}\n'
                            .format(source_branch, repository[2], activeBranch, f).encode()
                    )

    # adding all the files to the index. TODO: can be more efficient if we add it to the previous loop
    files_to_add = []
    pwd = os.getcwd()
    os.chdir(repo_root_path)
    for path, subdirs, files in os.walk('.'):
        for name in files:
            # we don't want to add the files under .git to the index
            if not path.startswith('./.git') and name not in conflict_files:
                files_to_add.append(os.path.join(path, name)[2:])
    os.chdir(pwd)
    add(files_to_add)
    # creating a commit object with two parents
    if not had_conflict:
        commit('Merging {} into {}'.format(source_branch, activeBranch), parent1=local_commits[0], parent2=remote_commits[0])
    

def drop_inline_diffs(diff):
    r = []
    for t in diff:
        if not t.startswith('?'):
            r.append(t)
    return r

def three_way_merge(x, a, b, conflict_commit_one, conflict_commit_two):
    dxa = difflib.Differ()
    dxb = difflib.Differ()
    xa = drop_inline_diffs(dxa.compare(x, a))
    xb = drop_inline_diffs(dxb.compare(x, b))

    m = []
    index_a = 0
    index_b = 0
    had_conflict = 0

    while (index_a < len(xa)) and (index_b < len(xb)):
        # no changes or adds on both sides
        if (xa[index_a] == xb[index_b] and
            (xa[index_a].startswith('  ') or xa[index_a].startswith('+ '))):
            m.append(xa[index_a][2:])
            index_a += 1
            index_b += 1
            continue

        # removing matching lines from one or both sides
        if ((xa[index_a][2:] == xb[index_b][2:])
            and (xa[index_a].startswith('- ') or xb[index_b].startswith('- '))):
            index_a += 1
            index_b += 1
            continue

        # adding lines in A
        if xa[index_a].startswith('+ ') and xb[index_b].startswith('  '):
            m.append(xa[index_a][2:])
            index_a += 1
            continue

        # adding line in B
        if xb[index_b].startswith('+ ') and xa[index_a].startswith('  '):
            m.append(xb[index_b][2:])
            index_b += 1
            continue

        # conflict - list both A and B, similar to GNU's diff3
        m.append("\n<<<<<<< {}\n".format(conflict_commit_one))
        while (index_a < len(xa)) and not xa[index_a].startswith('  '):
            m.append(xa[index_a][2:])
            index_a += 1
        m.append("\n=======\n")
        while (index_b < len(xb)) and not xb[index_b].startswith('  '):
            m.append(xb[index_b][2:])
            index_b += 1
        m.append("\n>>>>>>> {}\n".format(conflict_commit_two))
        had_conflict = 1

    # append remining lines - there will be only either A or B
    for i in range(len(xa) - index_a):
        m.append(xa[index_a + i][2:])
    for i in range(len(xb) - index_b):
        m.append(xb[index_b + i][2:])

    return had_conflict, m