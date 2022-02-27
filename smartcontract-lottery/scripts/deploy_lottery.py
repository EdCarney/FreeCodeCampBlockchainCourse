from tracemalloc import start
from brownie import Lottery, Contract, network, config
from scripts.helpfulScripts import getAccount, getContract, fundWithLink
import time

lottery: Contract = None


def deploy_lottery() -> Contract:
    global lottery
    account = getAccount()
    lottery = Lottery.deploy(
        getContract("eth_usd_price_feed").address,
        getContract("vrf_coordinator").address,
        getContract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!")
    return lottery


def start_lottery() -> None:
    account = getAccount()
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Lottery is started!")


def enter_lottery() -> None:
    account = getAccount()
    value = lottery.getEntranceFee() + 100000000
    enter_tx = lottery.enter({"from": account, "value": value})
    enter_tx.wait(1)
    print("You entered the lottery!")


def end_lottery() -> None:
    account = getAccount()
    # need to fund the contract before
    # ending the lottery
    funding_tx = fundWithLink(lottery.address)
    funding_tx.wait(1)
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    print("Lottery ended!")
    time.sleep(60)
    print(f"{lottery.mostRecentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
