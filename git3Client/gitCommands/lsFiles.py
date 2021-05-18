from git3Client.gitInternals.gitIndex import read_index

def ls_files(details=False):
    """Print list of files in index (including mode, SHA-1, and stage number
    if "details" is True).
    """
    for entry in read_index():
        if details:
            stage = (entry.flags >> 12) & 3
            print('{:6o} {} {:}\t{}'.format(
                    entry.mode, entry.sha1.hex(), stage, entry.path))
        else:
            print(entry.path)