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

What about the index file?
In all cases the index file remains the same.

# Switch branch