from brownie import MockV3Aggregator, network, config, accounts
from web3 import Web3

FORKED_LOCAL_ENVS = ["mainnet-forked", "mainnet-forked-dev"]
LOCAL_BLOCKCHAIN_ENVS = ["development", "ganache-local"]
DECMIALS = 8
STARTING_PRICE = 2000 * 10 ** DECMIALS


def isTestEnv() -> bool:
    return network.show_active() in LOCAL_BLOCKCHAIN_ENVS


def isForkedEnv() -> bool:
    return network.show_active() in FORKED_LOCAL_ENVS


def getAccount():
    if isTestEnv() or isForkedEnv():
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def deployMocks():
    print(f"The active network is {network.show_active()}")
    if len(MockV3Aggregator) == 0:
        print("Deploying new mocks...")
        MockV3Aggregator.deploy(DECMIALS, STARTING_PRICE, {"from": getAccount()})
        print("Mocks deployed")
    else:
        print("Using existing mocks")
