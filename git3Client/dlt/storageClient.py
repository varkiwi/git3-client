import ipfshttpclient

from git3Client.config.config import IPFS_CONNECTION

client = None


def getStorageClient() -> ipfshttpclient.client.Client:
    """
    The getStorageClient function returns an ipfshttpclient object which can be used to upload and download
    files from ipfs.

    Returns:
        ipfshttpclient.client.Client: IPFS Http Client
    """
    global client
    if client is None:
        client = ipfshttpclient.connect(IPFS_CONNECTION)
    return client
