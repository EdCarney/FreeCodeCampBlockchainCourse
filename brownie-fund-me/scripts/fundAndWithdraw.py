from brownie import FundMe, accounts
from scripts.helpfulScripts import getAccount
from web3 import Web3


def fund():
    fundMe = FundMe[-1]
    account = getAccount()
    entranceFee = fundMe.getEntranceFee()
    priceOfEth = fundMe.getPrice()
    precision = fundMe.desiredPrecision()

    print(f"Number of decimals in return values is {precision}")
    print(f"The current entry fee is {entranceFee / 10**precision}")
    print(f"The current price is {priceOfEth / 10**precision}")

    minWeiToFund = Web3.toWei(entranceFee / 10 ** precision, unit="ether")

    print(f"Funding {minWeiToFund} Wei")
    fundMe.fund({"from": account, "value": minWeiToFund})


def withdraw():
    fundMe = FundMe[-1]
    account = getAccount()
    fundMe.withdraw({"from": account})


def main():
    fund()
    # withdraw()


# 2000_000000000000000000
# 0.002500000000000000
