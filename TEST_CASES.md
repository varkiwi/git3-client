I am going to collect some test cases here, so that I can implement those at a later point in time.

# Create new branch
Create a new branch.

    1. Create empty repository, create a file with content.

        a. git checkout -b [name] should work. The HEAD file should be updated but no refs/heads/[name] file should be created.

        b. git branch [name] should not work and print the following error message: `fatal: Not a valid object name: 'oldBranchName'`


    2. Create empty repository, add (git3 add) a file with content to the repository.

        a. git checkout -b [name] - behaves the same as in 1.a.
        b. git branch [name] - behaves the same as in 1.b.


    3. Create empty repository, add a file with content to the repository. After adding the file to the index, add some more content to the file.

        a. git checkout -b [name] - behaves the same as in 1.a.
        b. git branch [name] - behaves the same as in 1.b.


    4. Create empty repository, add a file with content to the repository and commit it.

        a. git checkout -b [name] - Creates a new branch. This means, that a new file is created (`./git/refs/heads/<branchname>`) The content of the currently active branch (reference in `.git/HEAD`) is written to this file. The .git/HEAD file is updated to reference to the newly created file .git/refs/heads/<branchname>. Content in the file remains the same.

        b. git branch [name] - Creates a new branch. This means, that a new file is created (`./git/refs/heads/<branchname>`) The content of the currently active branch (reference in `.git/HEAD`) is written to this file. The .git/HEAD file is not updated.


    5. Create empty repository, add a file with content to the repository and commit it. After committing the file add some more content to the file.

        a. git checkout -b [name] - Creates a new branch. This means, that a new file is created (`./git/refs/heads/<branchname>`) The content of the currently active branch (reference in `.git/HEAD`) is written to this file. The .git/HEAD file is updated to reference to the newly created file .git/refs/heads/<branchname>. Content in the file remains the same.
    
        b. git branch [name] - Creates a new branch. This means, that a new file is created (`./git/refs/heads/<branchname>`) The content of the currently active branch (reference in `.git/HEAD`) is written to this file. The .git/HEAD file is not updated.
    
    
    6. Have a repository, create a file with content, git add and commit. Switch branch. Add content to file, git add and commit. Now try to create a new branch using the originals branch name.
        
        a. git checkout -b [original name] - Returns an error: `fatal: A branch names '[original name]' already exists.`

        b. git branch [original name] - Returns an error: `fatal: A branch named '[original name]' already exists.`



What about the index file?
In all cases the index file remains the same.

# Switch branch

    1. Have a repository, create a file with content, git add and commit. Switch branch. Add content to file. Switch to old branch.

        a. git checkout [original name] - Content in the file remains the same. Sha1sum of index remains the same.
    
    2. Have a repository, create a file with content, git add and commit. Switch branch. Add content to file and git add. Switch to old branch.

        a. git checkout [original name] - Content in the file remains the same. Yet, the sha1sum changes, on both branches.

    3. Have a repository, create a file with content, git add and commit. Switch branch. Add content to file, git add and commit. Switch to old branch.

        a. git checkout [original name] - The content which has been added on the second branch is removed, when the branch is switched to the first branch. The index file also changes. It seems that the index file is also updated when switching branches. Only in this case. In all the other cases the index file stays the same.
    

    4. Have a repository with two branches. One is ahead of the other one and is active. Switch to the first branch.

        a. git checkout [first branch] - Sha1 has of the index file is different. So there is a difference in the content of the index files between those branches. Content which has been added to the branch ahead is not in the first branch.


    5. Have a repository with two branches. One is ahead of the other one and is active. Add content to file and switch to the first branch. 

        a. git checkout [first branch] - This is the error message which gets displayed:
        
        error: Your local changes to the following files would be overwritten by checkout:
            test.txt
        Please commit your changes or stash them before you switch branches.
        Aborting

        I ran git diff and it tells me the difference between the working tree and the index file. Since there is a difference, I assume that the reason why I get this error message.


    
    6. Have a repository with two branches. One is ahead of the other one and is active. Add content to file and git add the content. Switch to the first branch. 

        a. git checkout [first branch] - This is the error message which gets displayed:
        
        error: Your local changes to the following files would be overwritten by checkout:
            test.txt
        Please commit your changes or stash them before you switch branches.
        Aborting

        I ran git diff --staged and it tells me the difference between the index file and the HEAD. Since there is a difference, I assume that the reason why I get this error message.

    
    7. Have a repository with two branches. One is ahead of the other one and is active. Add content to file and git commit the content. Switch to the first branch. 

        a. git checkout [first branch] - Switch works. All good.

    Observation: Whenever I am switching a branch and the hash of the ref files is the same, the content of the file is the same.
    Once there is a difference, the content of the file is different. When the hash in the ref files is different, the files in the repository are updated to reflect the content of that branch. 