import stat, sys

from git3Client.gitInternals.gitObject import read_object
from git3Client.gitInternals.gitTree import read_tree

def checkout(branch):
    print('Checkout to', branch)