WEB3_STORAGE_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDI4MDIxNEYzM0FGNTU5NEI3NzRlMzY1NzZmYzQ2MmQzNTFjQzM1MjIiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2NjIwOTUyMzE2MTEsIm5hbWUiOiJnaXQzLWNsaWVudCJ9.-J0UcNpJr72TELcuJdUZaIyp7T4mmZ__QDyegpGUEqE'

import requests
import json

test_file = {
    'type': 'blob',
    'data': 'test',
    'something': 'else'
}

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
            return json.loads(response.text)

web3Storage = Web3Storage(WEB3_STORAGE_API_KEY)

cid = web3Storage.upload_json(test_file)
print("CID:", cid)
data = web3Storage.get_data(cid['cid'])
print(data)
print(data['data'])