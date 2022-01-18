from git3Client.gitInternals.gitIndex import get_status_workspace

def status():
    """Show status of working copy."""
    changed, new, deleted = get_status_workspace()
    if changed:
        print('changed files:')
        for path in changed:
            print('   ', path)
    if new:
        print('new files:')
        for path in new:
            print('   ', path)
    if deleted:
        print('deleted files:')
        for path in deleted:
            print('   ', path)