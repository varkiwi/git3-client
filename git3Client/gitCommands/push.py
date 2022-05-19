from git3Client.dlt.repository import check_if_repo_created, push_commit, push_new_cid
from git3Client.dlt.repository import check_if_remote_ahead, get_remote_branch_hash
from git3Client.dlt.storageClient import getStorageClient

from git3Client.utils.utils import get_active_branch_hash, get_current_branch_name

def push():
    """Push current active branch to given git repo URL.""" 
    if not check_if_repo_created():
        print('Repository has not been registered yet. Use\n\n`git3 create`\n\nbefore you push')
        return
    
    active_branch_name = get_current_branch_name()

    local_sha1 = get_active_branch_hash()
    remote_database_cid = get_remote_branch_hash(active_branch_name)
    
    client = getStorageClient()
    # if remote_cid is none, nothing has been pushed yet.
    if remote_database_cid != None:
        # since there is already something pushed, we will have to get the remote cid
        remote_database = client.get_json(remote_database_cid)
        remote_commit_cid = remote_database['head_cid']
        remote_commit = client.get_json(remote_commit_cid)
        remote_sha1 = remote_commit['sha1']
    else:
        remote_commit_cid = None
        remote_sha1 = None
        # is going to contain all data in order to make loading the directory structure faster!
        remote_database = {
            'files': {}
        }

    remote_database['path'] = ['files']
    
    if local_sha1 == remote_sha1:
       print('Everything up-to-date')
       return
    elif check_if_remote_ahead(remote_sha1):
       print('Remote repository is ahead. Fetch and merge the changes first')
       return

    print('Pushing files to IPFS')
    branch_cid = push_commit(local_sha1, remote_sha1, remote_commit_cid, remote_database)
    remote_database['head_cid'] = branch_cid

    if branch_cid == remote_database_cid:
        print('Everything up-to-date')
    else:
        del remote_database['path']
        del remote_database['committer']
        del remote_database['currentCommitMessage']
        branch_cid = push_data_to_storage(remote_database)
        # branch_cid = client.add_json(remote_database)
        print('Going to write the CID into repository contract')
        push_new_cid(active_branch_name, branch_cid)

def push_data_to_storage(data):
    """This function also exists in git3Client.dlt.repository!!"""
    client = getStorageClient()
    time_to_sleep = 12
    while True:
        try:
            cid = client.add_json(data)
            break
        except:
            time.sleep(time_to_sleep)
            time_to_sleep += 2
            print(f'Due to too many requests, we will have to wait for {time_to_sleep} seconds')
    return cid