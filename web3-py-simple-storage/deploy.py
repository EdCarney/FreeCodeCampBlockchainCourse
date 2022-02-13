import string
from typing import Any, Dict
from solcx import compile_standard
from web3 import Web3
from dotenv import load_dotenv
import os
import json


def useLocalHost() -> bool:
    useLocalHost = os.getenv("USE_LOCAL_HOST").upper()
    if useLocalHost != "FALSE":
        return True
    return False


def createW3Instance() -> Web3:
    if useLocalHost():
        host = os.getenv("GANACHE_HOST")
    else:
        host = os.getenv("INFURA_HOST")

    print("Connecting to host", host)
    return Web3(Web3.HTTPProvider(host))


def getNonceValue(address: string) -> int:
    # use transaction count as the nonce for our private key
    return w3.eth.get_transaction_count(address)


def getTransactionDict() -> Dict:
    if useLocalHost():
        chain_id = int(os.getenv("LOCAL_CHAIN_ID"))
        my_address = os.getenv("LOCAL_BLOCKCHAIN_ADDRESS")
    else:
        chain_id = int(os.getenv("RINKEBY_CHAIN_ID"))
        my_address = os.getenv("METAMASK_BLOCKCHAIN_ADDRESS")

    nonce = getNonceValue(my_address)
    return {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }


def signAndSendTxn(transaction: Any) -> Any:
    if useLocalHost():
        private_key = os.getenv("LOCAL_PRIVATE_KEY")
    else:
        private_key = os.getenv("METAMASK_PRIVATE_KEY")

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile solidity code

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to host
w3 = createW3Instance()

# create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Build the Transaction
print("Deploying contract...")
transaction = SimpleStorage.constructor().buildTransaction(getTransactionDict())
tx_receipt = signAndSendTxn(transaction)
print("Contract deployed successfully")

# to work with a contract you need:
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> simulate making the call and getting a return; no state change; e.g. getting a value from a view
# Transact -> making a state change on the blockchain

# initial value of fav nunmber
print("Value before store:", simple_storage.functions.retrieve().call())

print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    getTransactionDict()
)
tx_receipt = signAndSendTxn(store_transaction)
print("Contract updated successfully")

print("Value after store:", simple_storage.functions.retrieve().call())
