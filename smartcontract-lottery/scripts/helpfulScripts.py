from brownie import (
    network,
    config,
    accounts,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
)
from eth_account import Account

FORKED_LOCAL_ENVS = ["mainnet-forked", "mainnet-forked-dev"]
LOCAL_BLOCKCHAIN_ENVS = ["development", "ganache-local"]
DECMIALS = 8
STARTING_PRICE = 2000 * 10 ** DECMIALS

contractToMock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def isTestEnv() -> bool:
    return network.show_active() in LOCAL_BLOCKCHAIN_ENVS


def isForkedEnv() -> bool:
    return network.show_active() in FORKED_LOCAL_ENVS


def getAccount(index=None, id=None) -> Account:
    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    elif isTestEnv() or isForkedEnv():
        return accounts[0]
    else:
        accounts.add(config["wallets"]["from_key"])


def getContract(contractName: str) -> Contract:
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploay a mock version of that contract,
    and return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contractType = contractToMock[contractName]
    if isTestEnv():
        deployMocks(contractType)
        # get the latest instance of the contract type
        contract = contractType[-1]
    else:
        contractAddress = config["networks"][network.show_active()][contractName]
        # create a new contract instance from an address and ABI
        contract = Contract.from_abi(
            contractType._name, contractAddress, contractType.abi
        )
    return contract


def deployMocks(contractType) -> None:
    print(f"The active network is {network.show_active()}")

    if len(contractType) > 0:
        print("Using existing mocks!")
        return

    account = getAccount()
    print("Deploying new mocks...")
    fromDict = {"from": account}
    MockV3Aggregator.deploy(DECMIALS, STARTING_PRICE, fromDict)
    link_token = LinkToken.deploy(fromDict)
    VRFCoordinatorMock.deploy(link_token, fromDict)
    print("Mocks deployed!")


def fundWithLink(
    contractAddress: str,
    account: Account = None,
    linkToken: Contract | None = None,
    amount: int = 10 ** 17,
):
    account = account if account else getAccount()
    linkToken = linkToken if linkToken else getContract("link_token")
    transfer_tx = linkToken.transfer(contractAddress, amount, {"from": account})

    # we could do this instead, where we get a contract instance
    # with the address and the interface we are going to use
    # linkTokenContract = interface.LinkTokenInterface(linkToken.address)
    # transfer_tx = linkTokenContract.transfer(contractAddress, amount, {"from": account})

    transfer_tx.wait(1)
    print("Funded lottery contract!")
    return transfer_tx
