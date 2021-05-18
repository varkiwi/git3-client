from eth_account import Account

from git3Client.utils.utils import get_private_key

def get_user_dlt_address():
    print('Getting users web3 address')
    private_key = get_private_key()
    acct = Account.privateKeyToAccount(private_key)
    return acct.address