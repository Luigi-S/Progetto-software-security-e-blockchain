import json
import os
from parser import ParserError

from solcx.exceptions import SolcError
from web3 import Web3

from solcx import compile_standard, install_solc

class Deployer():
    #temp
    chain_link = "ws://127.0.0.1:8545"
    chain_id = 1337
    my_address = "0xa1eF58670368eCCB27EdC6609dea0fEFC5884f09"
    private_key = "0x5b3208286264f409e1873e3709d3138acf47f6cc733e74a6b47a040b50472fd8"
    #temp


    @staticmethod
    # TODO: handle failed compilation
    def compile(contract_path):
        contract_name = os.path.basename(contract_path)
        with open(contract_path, "r") as file:
            simple_storage_file = file.read()
        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {contract_name: {"content": simple_storage_file}},
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                        }
                    }
                },
            },
        )

        with open("compiled_code.json", "w") as file:
            json.dump(compiled_sol, file)

        # many contracts can be in a single .sol file
        bytecode = {}
        abi = {}
        contracts = compiled_sol["contracts"][contract_name].keys()
        for contract in contracts:
            bytecode[contract] = compiled_sol["contracts"][contract_name][contract]["evm"]["bytecode"]["object"]
            abi[contract] = json.loads(
                compiled_sol["contracts"][contract_name][contract]["metadata"]
            )["output"]["abi"]
        # provvisorio v
        return bytecode[list(compiled_sol["contracts"][contract_name].keys())[0]], abi[list(compiled_sol["contracts"][contract_name].keys())[0]]

    def deploy(self, bytecode, abi):
        w3 = Web3(Web3.WebsocketProvider(self.chain_link)) # TODO: move all connection-related code outside of this class
        # Create the contract in Python
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        # Get the latest transaction
        nonce = w3.eth.getTransactionCount(self.my_address) # get address from dotenv
        # Submit the transaction that deploys the contract
        transaction = contract.constructor().buildTransaction(
            {
                "chainId": self.chain_id,
                "gasPrice": w3.eth.gas_price,
                "from": self.my_address,
                "nonce": nonce,
            }
        )
        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=self.private_key) # get private key from dotenv
        print("Deploying Contract...")
        print("[=", end='') #TODO: change to tqdm or similar
        # Send it!
        transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print("==", end='')
        # Wait for the transaction to be mined, and get the transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
        print("=]")
        print(f"Contract deployed to address: {receipt.contractAddress}") # TODO: optionally, move all user communication to cli


class Caller():
    # temp
    chain_link = "ws://127.0.0.1:8545"
    chain_id = 1337
    my_address = "0xa1eF58670368eCCB27EdC6609dea0fEFC5884f09"
    private_key = "0x5b3208286264f409e1873e3709d3138acf47f6cc733e74a6b47a040b50472fd8"
    # temp

    def __init__(self, contract_address, abi):
        self.w3 = Web3(
            Web3.WebsocketProvider(self.chain_link))  # TODO: move all connection-related code outside of this class
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

    def call(self,  func_name, param):
        func = self.contract.get_function_by_name(func_name)
        transaction = func(param).buildTransaction(
            {
                "chainId": self.chain_id,
                "gasPrice": self.w3.eth.gas_price,
                "from": self.my_address,
                "nonce": self.w3.eth.getTransactionCount(self.my_address),
            }
        )
        signed_transaction = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        tx_greeting_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        print("Calling the contract... ")                                                               # <-(tqdm)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
        print("Function executed")
        #TODO: exception handling di ogni genere
