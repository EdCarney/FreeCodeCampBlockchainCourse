from scripts.helpfulScripts import getAccount, isTestEnv
from scripts.deploy import deployFundMe
from web3 import Web3
from brownie import accounts, exceptions
import pytest


def test_can_fund_and_withdraw():
    account = getAccount()
    fundMe = deployFundMe()
    entranceFeeInEth = fundMe.getEntranceFee()
    numberDecimals = fundMe.desiredPrecision()
    entranceFeeInWei = (
        Web3.toWei(entranceFeeInEth / 10 ** numberDecimals, unit="ether") + 100
    )

    tx1 = fundMe.fund({"from": account, "value": entranceFeeInWei})
    tx1.wait(1)
    amountAfterFunding = fundMe.addressToAmountFunded(account.address)

    tx2 = fundMe.withdraw({"from": account})
    tx2.wait(1)
    amountAfterWithdraw = fundMe.addressToAmountFunded(account.address)

    assert amountAfterFunding == entranceFeeInWei
    assert amountAfterWithdraw == 0


def test_only_owner_can_withdraw():
    if not isTestEnv():
        pytest.skip("Test is only for local testing")

    fundMe = deployFundMe()
    badActor = accounts.add()

    with pytest.raises(exceptions.VirtualMachineError):
        fundMe.withdraw({"from": badActor})
