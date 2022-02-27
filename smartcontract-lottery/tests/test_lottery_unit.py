from brownie import Lottery, accounts, network, config, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpfulScripts import (
    DECMIALS,
    STARTING_PRICE,
    fundWithLink,
    getAccount,
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
    tx = entrance_fee = lottery.getEntranceFee()
    tx.wait(1)

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
