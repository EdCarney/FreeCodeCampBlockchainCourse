from brownie import exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpfulScripts import (
    DECMIALS,
    STARTING_PRICE,
    fundWithLink,
    getAccount,
    getContract,
    isTestEnv,
)
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if not isTestEnv():
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()

    # Act
    # entrance fee in ETH
    entrance_fee = lottery.getEntranceFee()

    lotteryFeeInUsd = lottery.usdEntranceFee()
    mockAggregatorEthPriceInUsd = STARTING_PRICE / (10 ** DECMIALS)
    expected_entrace_fee = lotteryFeeInUsd / mockAggregatorEthPriceInUsd

    # Assert
    assert expected_entrace_fee == entrance_fee


def test_cant_enter_unless_started():
    if not isTestEnv():
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()

    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": getAccount(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    if not isTestEnv():
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()
    account = getAccount()

    # Act
    lottery.startLottery({"from": account})
    tx = lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    tx.wait(1)

    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    if not isTestEnv():
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()
    account = getAccount()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fundWithLink(lottery.address)
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if not isTestEnv():
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()
    account = getAccount()

    # Act
    lottery.startLottery({"from": account})

    # enter lottery with multiple people
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": getAccount(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": getAccount(index=2), "value": lottery.getEntranceFee()})

    # fund contract with LINK to allow call to LINK node
    fundWithLink(lottery.address)

    # end lottery, then get the request ID for the request to the LINK
    # node from the event that we emit to the blockchain
    tx = lottery.endLottery({"from": account})
    request_id = tx.events["RequestedRandomness"]["requestId"]

    # use this request ID to call the callBackWithRandomness function on
    # the VRF node with some 'random' number that is returned to our
    # lottery contract; note we know 777 % 3 = 0 so our account should
    # be the winner as it was the first in the lottery
    PSEUDO_RANDOM_NUM = 777
    getContract("vrf_coordinator").callBackWithRandomness(
        request_id, PSEUDO_RANDOM_NUM, lottery.address, {"from": account}
    )

    # Assert
    starting_account_balance = account.balance()
    lottery_balance = lottery.balance()

    assert lottery.mostRecentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_account_balance + lottery_balance
