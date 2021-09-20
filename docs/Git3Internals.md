# Data Structure on IPFS

## Blob

```bash
{
    type: 'blob',
    content: '...',
    sha1: sha1_hash
}
```
The sha1 hash is needed in order to avoid recalculating it and have the possibility to compare with the local repository.

## Tree

```bash
{
    type: 'tree',
    entries: [
        {
            mode: mode_int,
            name: filename,
            CID: blob_cid
        },
        ...
    ],
    name: dir_name,
    sha1: sha1_hash
}
```
The sha1 hash is needed in order to avoid recalculating it and have the possibility to compare with the local repository.

## Commit

```bash
{
    type: 'commit',
    tree: tree_cid,
    parents: [parent1_cid, parent2_cid, ...],
    author: {
        name: author_name,
        email: author_email,
        date_seconds: timestamp,
        date_timestamp: timezone
    },
    committer: {
        name: committer_name,
        email: committer_email,
        date_seconds: timestamp,
        date_timestamp: timezone
    },
    commit_message: message,
    sha1: sha1_hash
}
```
The sha1 hash is needed in order to avoid recalculating it and have the possibility to compare with the local repository.

# Database
To push the blob, tree, and commit json to IPFS is no problem. THe problem starts if you want to traverse those
in order to get the current directory structure and which commit message belongs to which file. This turns out to
be very tedious on the frontend side.

Therefore, we introduce a database. This is a json, which represents the file structure of the repository and is pushed
to IPFS. The cid is pushed to the Smart Contract, to make it for clients easier to reconstruct the file structure of the
repository. The database contains a link to the youngest commit, so it is possible to go through the entire chain
of commits, trees and blobs, and verify the information. 

Here is the structure of the database:
```json
{
   "files":{
      "README.md":{
         "commit_message":"Message",
         "commit_time":"Timestamp in seconds",
         "mode":33188, # file
         "name":"README.md",
         "sha1":"SHA1 of file"
      },
      "subdir":{
         "commit_message":"Message",
         "commit_time":"Timestamp in seconds",
         "files":{
            # contains files stored in this directory
         },
         "mode":16384, # directory
         "name":"subdir",
         "sha1":"SHA1 of folder"
      }
   },
   "head_cid":"CID to youngest commit in IPFS"
}
```