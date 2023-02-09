import binascii
import json
import os

import solcx
import web3
import websockets
from solcx.exceptions import SolcError
from web3 import Web3

from solcx import compile_standard


class ConnectionHost:
    def __init__(self, chain_link):
        self.chain_link = chain_link
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
    my_address = "0xa1eF58670368eCCB27EdC6609dea0fEFC5884f09"
    private_key = "0x5b3208286264f409e1873e3709d3138acf47f6cc733e74a6b47a040b50472fd8"

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

            if not os.path.exists("app/compiled_contracts"):
                os.makedirs("app/compiled_contracts")

            # Crea il file.json di ogni contratto deployato contenente l'abi di esso
            for contract in compiled_sol["contracts"][contract_name]:
                with open("app/compiled_contracts/" + contract + ".json", "w") as file:
                    json.dump(compiled_sol["contracts"][contract_name][contract]["abi"], file)

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
            print(e4)

    def deploy(self, bytecode, abi, url_shard="ws://127.0.0.1:8545"):
        try:
            w3 = ConnectionHost(url_shard).connect()
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
            print(f"Contract deployed to address: {receipt.contractAddress}")

            return receipt.contractAddress

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
        w3 = Web3(Web3.WebsocketProvider(self.chain_link)) # TODO: move all connection-related code outside of this class
        # Create the contract in Python
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        # Get the latest transaction
        nonce = w3.eth.getTransactionCount(self.my_address)  # get address from dotenv
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
    my_address = "0xa1eF58670368eCCB27EdC6609dea0fEFC5884f09"
    private_key = "0x5b3208286264f409e1873e3709d3138acf47f6cc733e74a6b47a040b50472fd8"

    # temp

    def __init__(self, contract_address, abi, chain_link="ws://127.0.0.1:8545"):
        self.w3 = ConnectionHost(chain_link).connect()
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

    def get_func(self, func_name):
        return self.contract.get_function_by_name(func_name)

    # func_name è il nome della funzione dello smart contract da chiamare, *param sono
    # i parametri (in numero variabile) da passare a tale funzione
    def call(self, func_name, *param):
        try:
            #func = self.contract.get_function_by_name(func_name)
            func = self.get_func(func_name)
            i = 0
            j = 0
            for elem in param:
                i = i + 1
                if elem is None:
                    j = j + 1
            if i != j:
                for obj in self.contract.abi:
                    if "name" in obj and obj["name"] == func_name and obj["stateMutability"] != "view":
                        transaction = func(*param).buildTransaction(
                            {
                                "chainId": self.w3.eth.chain_id,
                                "gasPrice": self.w3.eth.gas_price,
                                "from": self.my_address,
                                "nonce": self.w3.eth.getTransactionCount(self.my_address),
                            }
                        )
                        signed_transaction = self.w3.eth.account.sign_transaction(
                            transaction_dict=transaction, private_key=self.private_key
                        )
                        tx_greeting_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
                        # catcha gli eventi
                        #event = self.contract.events.XXX().processReceipt(tx_receipt)
                #value_returned = func(*param).call()
            else:
                for obj in self.contract.abi:
                    if "name" in obj and obj["name"] == func_name and obj["stateMutability"] != "view":
                        transaction = func().buildTransaction(
                            {
                                "chainId": self.w3.eth.chain_id,
                                "gasPrice": self.w3.eth.gas_price,
                                "from": self.my_address,
                                "nonce": self.w3.eth.getTransactionCount(self.my_address),
                            }
                        )
                        signed_transaction = self.w3.eth.account.sign_transaction(
                            transaction_dict=transaction, private_key=self.private_key
                        )
                        tx_greeting_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
                        # catcha gli eventi
                        #event = self.contract.events.XXX().processReceipt(tx_receipt)
                #value_returned = func().call()

            print("Function executed")
            return func

        except web3.exceptions.InvalidAddress:
            print("The address doesn't exist.")
        except ValueError as e1:
            print(e1)
            print("The method called doesn't exist.\n")
            print("Tip: check if the abi used is the correct one.")
        except TypeError:
            print("The params inserted aren't the same required by the function called.")
        except Exception as e:
            print(e)
            print("System error occurred.")
