# Data Structure on IPFS

## Blob

```bash
{
    type: 'blob',
    content: '...',
    sha1: sha1_hash
}
```
The sha1 hash is needed in order to avoid recalulating it and have the possibility to compare with the local repository.

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
The sha1 hash is needed in order to avoid recalulating it and have the possibility to compare with the local repository.

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
The sha1 hash is needed in order to avoid recalulating it and have the possibility to compare with the local repository.