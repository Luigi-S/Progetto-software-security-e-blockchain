import binascii
import json
import os

import solcx
import websockets
from solcx.exceptions import SolcError
from web3 import Web3

from solcx import compile_standard


class ConnectionHost:
    def __init__(self):
        self.chain_link = "ws://localhost:10002"
        self.chain_id = 1337

    def connect(self):
        try:
            web3 = Web3(Web3.WebsocketProvider(self.chain_link))
            return web3
        except TimeoutError as e1:
            print("ERROR - timeout error:")
            print(e1)
        except websockets.exceptions.InvalidURI as e2:
            print("ERROR - invalid URI:")
            print(e2)


class Deployer():
    # temp
    my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
    private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"

    # temp
    @staticmethod
    # TODO: handle failed compilation
    def compile(contract_path):
        try:
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

            # Crea il file.json di ogni contratto deployato contenente l'abi di esso
            for contract in compiled_sol["contracts"][contract_name]:
                with open("contracts/compiled/" + contract + ".json", "w") as file:
                    json.dump(compiled_sol["contracts"][contract_name][contract]["abi"], file)

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

            return bytecode, abi

            # provvisorio v
            # return bytecode[list(compiled_sol["contracts"][contract_name].keys())[0]], abi[list(compiled_sol["contracts"][contract_name].keys())[0]]

        except solcx.exceptions.SolcError as e:
            print("ERROR: the file .sol isn't syntactically correct.")
        except binascii.Error as e1:
            print("ERROR: the file doesn't contains a valid bytecode.")
            print(e1)
        except UnboundLocalError as e2:  # se la compilazione del bytecode non va a buon fine, "bytecode" non è inizializzata
            print("")
        except TypeError as e3:
            print(e3)
        except Exception as e4:
            print("ERROR: system error occurred.")

    def deploy(self, bytecode, abi):
        try:
            w3 = ConnectionHost().connect()
            # Create the contract in Python
            contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            # Get the latest transaction
            nonce = w3.eth.getTransactionCount(self.my_address)  # get address from dotenv
            # Submit the transaction that deploys the contract
            transaction = contract.constructor().buildTransaction(
                {
                    "chainId": w3.eth.chain_id,
                    "gasPrice": w3.eth.gas_price,
                    "from": self.my_address,
                    "nonce": nonce,
                }
            )
            # Sign the transaction
            signed_txn = w3.eth.account.sign_transaction(transaction,
                                                         private_key=self.private_key)  # get private key from dotenv
            print("Deploying Contract...")
            print("[=", end='')  # TODO: change to tqdm or similar
            # Send it!
            transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print("==", end='')
            # Wait for the transaction to be mined, and get the transaction receipt
            receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
            print("=]")
            print(
                f"Contract deployed to address: {receipt.contractAddress}")  # TODO: optionally, move all user communication to cli
        except binascii.Error as e:
            print("ERROR: the file doesn't contains a valid bytecode or abi.")
        except KeyError as e2:
            print("ERROR: the file doesn't contains a valid bytecode or abi.")
            print(e2)
        except UnboundLocalError:  # se la compilazione del bytecode non va a buon fine, "bytecode" non è inizializzata
            print("")
        except TypeError as e3:
            print(e3)
        except Exception as e4:
            print("ERROR: system error occurred.")
            print(e4)


class Caller():
    # temp
    my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
    private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"

    # temp

    def __init__(self, contract_address, abi):
        self.w3 = ConnectionHost().connect()
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

    def call(self, func_name, *param):
        func = self.contract.get_function_by_name(func_name)
        i = 0
        j = 0
        for elem in param:
            i = i + 1
            if elem is None:
                j = j + 1
        if i != j:
            transaction = func(*param).buildTransaction(
                {
                    "chainId": self.w3.eth.chain_id,
                    "gasPrice": self.w3.eth.gas_price,
                    "from": self.my_address,
                    "nonce": self.w3.eth.getTransactionCount(self.my_address),
                }
            )
            value_returned = func(*param).call()
        else:
            transaction = func().buildTransaction(
                {
                    "chainId": self.w3.eth.chain_id,
                    "gasPrice": self.w3.eth.gas_price,
                    "from": self.my_address,
                    "nonce": self.w3.eth.getTransactionCount(self.my_address),
                }
            )
            value_returned = func().call()
        signed_transaction = self.w3.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=self.private_key
        )
        tx_greeting_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        print("Calling the contract... ")  # <-(tqdm)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
        print("Function executed\n")
        # print(tx_receipt)
        # TODO: exception handling di ogni genere
