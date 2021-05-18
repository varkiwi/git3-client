class NoRepositoryError(Exception):
    """
    Exception raised for not finding a .git folder.

    Attributes:
        message -- Error message
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message