repository = None

class GitRepository:
    """Represents a Git repository.

    Attributes:
        repo_path (str): Absolute path to the repository.
    """

    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_repo_path(self):
        """Returns the absolute path to the repository.

        Returns:
            str: Absolute path to the repository.
        """
        return self.repo_path
