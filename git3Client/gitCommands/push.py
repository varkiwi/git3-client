import ipfshttpclient

from git3Client.dlt.repository import check_if_repo_created, push_commit, push_new_cid

from git3Client.utils.utils import get_local_master_hash
from git3Client.dlt.repository import check_if_remote_ahead, get_remote_master_hash

IPFS_CONNECTION = '/dns4/ipfs.infura.io/tcp/5001/https'
client = ipfshttpclient.connect(IPFS_CONNECTION)

def push():
    """Push master branch to given git repo URL.""" 
    if not check_if_repo_created():
        print('Repository has not been registered yet. Use\n\n`git3 create`\n\nbefore you push')
        return
    local_sha1 = get_local_master_hash()
    remote_cid = get_remote_master_hash()
    if remote_cid != None:
        # since there is already something pushed, we will have to get the remote cid
        remote_commit = client.get_json(remote_cid)
        remote_sha1 = remote_commit['sha1']
    else:
        remote_sha1 = None

    if local_sha1 == remote_sha1:
       print('Everything up-to-date')
       return
    elif check_if_remote_ahead(remote_sha1):
       print('Remote repository is ahead. Pull the changes first')
       return
    print('Pushing files to IPFS')
    master_cid = push_commit(local_sha1, remote_sha1, remote_cid)
    print('Master_cid: ', master_cid)
    if master_cid == remote_cid:
        print('Everything up-to-date')
    else:
        print('Going to write the CID into repository contract')
        push_new_cid(master_cid)