# GIT 3

The idea behind Git3 is to combine the power of git and blockchain: Storing code in a decentralized manner and receive payments without the need of a third party.

Each repository is represented by a smart contract, which stores all managing information and receives the payments, like tips or bounties for issues.

The content of the repository is stored on IPFS using a data structure, very similar to git's internal objects. 

In order to be able to use git3, a git3 client is created, which is similar to git. This makes the switch to git3 easier.

## Private key
In order to be able to use the git3 client, a private key for the Matic network is required. There are two possibilities:
  1. You generate an account in MetaMask and export the private key and create a pem file
  2. You use openssl in your terminal to generate a key

### Private key using openssl
In order to generate a new private key use the following command:
```bash
ssh-keygen -t ecdsa -b 256 -m pem
```
Once you run the command, two files are generated. The file with the `.pub` extension contains the public key and the file without an extension the private key.

If you want to export the key and import it in MetaMask, use 
```bash
openssl ec -outform der -in private_key_file | hd
```
This command takes the file containing the private key, which is in the PEM format and outputs it in the DER format. Your output should look like this:
```
00000000  30 77 02 01 01 04 20 XX  XX XX XX XX XX XX XX XX  |0w.... L.-.8&..P|
00000010  XX XX XX XX XX XX XX XX  XX XX XX XX XX XX XX XX  |.ctx.!.l...x5bXY|
00000020  XX XX XX XX XX XX XX a0  0a 06 08 2a 86 48 ce 3d  |......(....*.H.=|
...
```
The `0x20` at position 6 says, that the following data is 32 bytes long and this is our generated private key, here represented as XX. Copy this key into MetaMask and you are good to go :)

Better tooling is still required :)

### Git config file
The git3 client needs to know the author's name, email address and where to find the private key. Therefore you can use either the global `.gitconfig` file or a config file stored in the repository in the `.git` folder.

#### Gitconfig
Here is how the contant of the `~/.gitconfig` file looks like
```bash
[user]
        email = author email
        name = author name
        IdentityFile = path to private key in pem format
```
Set the values according to your needs.

#### Repository config
If you want to use a different configuration for each repository, just add a `config` file into the `.git/` in your repository and add the same entries as in the `~/.gitconfig` file.

# Git Commands

## Git init
To create a new local repository, you have to call `git3 init [name]`
You can either provide a name for the repository or just call it without a name. In case you don't provide a name, the repository is initialized in the current directory you are in.

## Git add
To add a file to your repository, just use `git3 add file_name`

## Git commit 
In order to commit your current repository, just use `git3 commit -m "Message you want to add"`

## Git push
If you want to push your repository, just use `git3 push .`

In order to be able to push, a smart contract is required. If you haven't registered your repository yet, use `git3 create`

## Git create
In order to have a remote repository, you have to register your repository. Use the `git3 create` command. It sends a transaction to the factory contract, which deployes a new smart contract for your repository. Once this is done, you are able to push your repository.

## Git fetch
In order to download the remote state, use `git3 fetch`.

## Git merge
If you want to merge the state after doing a fetch, just use `git3 merge`. It will take the reference from the fetch.



## The very first mainnet repo

User address: `0x0539E6a1093a359C5720d053DB5e3D277F1762B6`
Repository name: `firstMainNetRepo`