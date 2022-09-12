import ipfshttpclient
import json
import requests

from git3Client.config.config import WEB3_STORAGE_API_KEY

client = None

def getStorageClient():
    """
    The getStorageClient function returns an Web3Storage object which can be used to upload and download
    files from ipfs.

    Returns:
        Web3Storage
    """
    global client
    if client is None:
        client = Web3Storage(WEB3_STORAGE_API_KEY)
    return client


class Web3Storage:
    upload_endpoint = "https://api.web3.storage/"
    retrieve_endpoint = ".ipfs.w3s.link"

    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def upload_json(self, json_data: dict) -> dict:
        response = requests.post(f"{self.upload_endpoint}upload", json = json_data, headers=self.headers)
        if response.status_code == 200:
            return json.loads(response.text)

    def get_data(self, cid: str):
        response = requests.get(f"https://{cid}{self.retrieve_endpoint}")
        if response.status_code == 200:
            return response.text

    def get_json(self, cid: str):
        response = requests.get(f"https://{cid}{self.retrieve_endpoint}")
        if response.status_code == 200:
            # this solution has to be temporary until we write proper code
            data = json.loads(response.text)
            return data
