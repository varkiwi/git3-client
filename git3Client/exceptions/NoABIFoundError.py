class NoABIFound(Exception):
    """
    Exception raised for not finding the abi of a smart contract.

    Attributes:
        message -- Error message
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message