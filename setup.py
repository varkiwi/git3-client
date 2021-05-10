from setuptools import setup, find_packages
 
readme = open('README.md', 'r')
content = readme.read()
readme.close()

setup(
    name = "git3-client",
    packages = find_packages('.'),
    entry_points = {
        "console_scripts": ['git3=git3_client.git3:main']
    },
    version = "0.1.5",
    description = "Git3 Python client",
    long_description = content,
    long_description_content_type="text/markdown",
    author = "Jacek Varky",
    author_email = "jaca347@gmail.com",
    data_files=[('git3_client/artifacts/contracts/', [
        'git3_client/artifacts/contracts/GitFactory.sol/GitFactory.json',
        'git3_client/artifacts/contracts/GitRepository.sol/GitRepository.json',
        'git3_client/artifacts/contracts/facets/DiamondCutFacet.sol/DiamondCutFacet.json',
        'git3_client/artifacts/contracts/facets/DiamondLoupeFacet.sol/DiamondLoupeFacet.json',
        'git3_client/artifacts/contracts/facets/GitBranch.sol/GitBranch.json',
        'git3_client/artifacts/contracts/facets/GitIssues.sol/GitIssues.json',
        'git3_client/artifacts/contracts/facets/GitRepositoryManagement.sol/GitRepositoryManagement.json'
    ]),
    # ('git3_client/artifacts/contracts/facets', [
    #     'git3_client/artifacts/contracts/facets/DiamondCutFacet.sol/DiamondCutFacet.json',
    #     'git3_client/artifacts/contracts/facets/DiamondLoupeFacet.sol/DiamondLoupeFacet.json',
    #     'git3_client/artifacts/contracts/facets/GitBranch.sol/GitBranch.json',
    #     'git3_client/artifacts/contracts/facets/GitIssues.sol/GitIssues.json',
    #     'git3_client/artifacts/contracts/facets/GitRepositoryManagement.sol/GitRepositoryManagement.json'
    # ])
    ],
    install_requires=[
        'attrs==20.2.0',
        'base58==2.0.1',
        'bitarray==1.2.2',
        'certifi==2020.6.20',
        'chardet==3.0.4',
        'cytoolz==0.11.0',
        'eth-abi==2.1.1',
        'eth-account==0.5.4',
        'eth-hash==0.2.0',
        'eth-keyfile==0.5.1',
        'eth-keys==0.3.3',
        'eth-rlp==0.2.1',
        'eth-typing==2.2.2',
        'eth-utils==1.9.5',
        'hexbytes==0.2.1',
        'idna==2.10',
        'importlib-metadata==2.0.0',
        'importlib-resources==3.0.0',
        'ipfshttpclient==0.7.0a1',
        'jsonschema==3.2.0',
        'lru-dict==1.1.6',
        'multiaddr==0.0.9',
        'netaddr==0.8.0',
        'parsimonious==0.8.1',
        'protobuf==3.13.0',
        'pycryptodome==3.9.8',
        'pyrsistent==0.17.3',
        'requests==2.24.0',
        'rlp==2.0.0',
        'rusty-rlp==0.1.15',
        'six==1.15.0',
        'toolz==0.11.1',
        'typing-extensions==3.7.4.3',
        'urllib3==1.25.11',
        'varint==1.0.2',
        'web3==5.12.3',
        'websockets==8.1',
        'zipp==3.3.1',
      ],
    url = "https://github.com/jacekv/git3",
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)