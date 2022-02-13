import os
from brownie import accounts, config, SimpleStorage, network


def deploySimpleStorage():
    # Method 1: can use this when local testing with ganache
    # account = accounts[0]

    # Method 2: create new account and load it
    # account = accounts.load("freecodecamp-account")

    # Method 3: use brownie-config to load env vars
    # account = accounts.add(os.getenv("PRIVATE_KEY"))
    # OR
    # account = accounts.add(config["wallets"]["from_key"])

    account = getAccount()
    simple_storage = SimpleStorage.deploy({"from": account})

    stored_value = simple_storage.retrieve()

    print("Value before update:", stored_value)

    transaction = simple_storage.store(15)
    transaction.wait(1)

    stored_value = simple_storage.retrieve()

    print("value after update:", stored_value)


def getAccount():
    if network.show_active() == "development":
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def main():
    deploySimpleStorage()
