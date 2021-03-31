from git3_client.dlt.user import get_user_dlt_address

def getAddress():
    """
    Prints users address on the console
    """
    # private_key = get_private_key()
    # acct = Account.privateKeyToAccount(private_key)
    return get_user_dlt_address()
    # print('Your address is: {}'.format(address))