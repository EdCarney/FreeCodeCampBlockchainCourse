from brownie import FundMe, MockV3Aggregator, network, config
from scripts.helpfulScripts import getAccount, deployMocks, isTestEnv


def deployFundMe():
    account = getAccount()

    # need to pass price feed address to FundMe contract
    # if on persistent network (e.g. Rinkeby) use associated address,
    # otherwise deploy mocks
    if not isTestEnv():
        priceFeedAddress = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]
    else:
        deployMocks()
        priceFeedAddress = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
        priceFeedAddress,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )

    print(f"Contract deployed to {fund_me.address}")
    return fund_me


def main():
    deployFundMe()
