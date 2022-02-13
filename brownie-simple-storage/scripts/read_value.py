from brownie import SimpleStorage, accounts, config


def readContract():
    # this gets the address of the latest deployment
    # of SimpleStorage that we've made
    simple_storage = SimpleStorage[-1]

    # recall we need to know ABI and address
    # brownie knows both of these already
    print(simple_storage.retrieve())


def main():
    readContract()
