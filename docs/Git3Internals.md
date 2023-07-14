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

# Branching
The `.git` directory contains a file called `HEAD`. This file contains the following text: `ref: refs/heads/[branchName]`.
This means that the current branch is `[branchName]`.
The file in `refs/heads/[branchName]` contains the SHA1  of the commit, which is the head of the branch.

`git` offers two commands:
```bash
git checkout <existing_branch>

git checkout -b <new_branch>
```

## Checkout
```bash
git checkout <non_existing_branch>
error: pathspec <non_existing_branch> did not match any file(s) known to git
```
```bash
git checkout -b <existing_branch>
fatal: A branch named <existing_branch> already exists.
```

## Branch
```bash
git branch
```
returns a list of all branches.

```bash
git branch <branchname>
```
creates a new branch but does not switch to it. Creating a new branch means that a new file is created (`./git/refs/heads/<branchna,e>`) is created. The content of the currently active branch (reference in `.git/HEAD`) is written to this file.

If a branch with the same name already exists, the following error is printed: `fatal: A branch named <branchname> already exists.`

If a new repository has been created and there is no file in `.git/refs/heads/` the following error is printed: `fatal: Not a valid object name: '<branchname>'.`

## Switch
Switch to a specified branch. The working tree and the index are updated to match the branch. All new commits will be added to the tip of this branch.


## Checkout Remote Branch on Git

In some cases, you may be interested in checking out remote branches from your distant repository.

In order to switch to a remote branch, make sure to fetch your remote branch with “git fetch” first. You can then switch to it by executing “git checkout” with the “-t” option and the name of the branch.

```bash
git fetch

git checkout -t <remote_name>/<branch_name>
```
