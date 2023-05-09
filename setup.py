from setuptools import setup, find_packages

readme = open('README.md', 'r')
content = readme.read()
readme.close()

setup(
    name = "git3Client",
    packages = find_packages('.', exclude=("tests",)),
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "git3 = git3Client.__main__:run",
        ]
    },
    data_files=[
        ('contractAbi', [
            'git3Client/artifacts/contracts/repo_facets/GitBranch.sol/GitBranch.json',
            'git3Client/artifacts/contracts/factory_facets/RepositoryManagement.sol/RepositoryManagement.json',
            ])
    ],
    version = "0.2.6",
    description = "Git3 Python client",
    long_description = content,
    long_description_content_type="text/markdown",
    author = "Jacek Varky",
    author_email = "jaca347@gmail.com",
    install_requires=[
        'aiohttp==3.8.1',
        'aiosignal==1.2.0',
        'async-timeout==4.0.2',
        'attrs==20.2.0',
        'base58==2.0.1',
        'bitarray==1.2.2',
        'bleach==5.0.0',
        'certifi==2020.6.20',
        'cffi==1.15.0',
        'chardet==3.0.4',
        'charset-normalizer==2.0.12',
        'commonmark==0.9.1',
        'cryptography==36.0.2',
        'cytoolz==0.12.1',
        'docutils==0.18.1',
        'eth-abi==2.1.1',
        'eth-account==0.5.5',
        'eth-hash==0.2.0',
        'eth-keyfile==0.5.1',
        'eth-keys==0.3.3',
        'eth-rlp==0.2.1',
        'eth-typing==2.2.2',
        'eth-utils==1.9.5',
        'frozenlist==1.3.0',
        'hexbytes==0.2.1',
        'idna==2.10',
        'importlib-metadata==4.0.1',
        'importlib-resources==3.0.0',
        'ipfshttpclient==0.8.0a2',
        'jsonschema==3.2.0',
        'keyring==23.5.0',
        'lru-dict==1.1.6',
        'multiaddr==0.0.9',
        'multidict==6.0.2',
        'netaddr==0.8.0',
        'parsimonious==0.8.1',
        'pkginfo==1.8.2',
        'protobuf==3.13.0',
        'pycparser==2.21',
        'pycryptodome==3.9.8',
        'Pygments==2.11.2',
        'pyrsistent==0.17.3',
        'readme-renderer==34.0',
        'requests==2.27.1',
        'requests-toolbelt==0.9.1',
        'rfc3986==2.0.0',
        'rich==12.2.0',
        'rlp==2.0.0',
        'six==1.15.0',
        'toolz==0.11.1',
        'twine==4.0.0',
        'typing_extensions==4.2.0',
        'urllib3==1.26.9',
        'varint==1.0.2',
        'web3==5.23.1',
        'webencodings==0.5.1',
        'websockets==9.1',
        'yarl==1.7.2',
        'zipp==3.3.1',
      ],
    url = "https://github.com/varkiwi/git3-client",
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)