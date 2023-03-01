import binascii
import json
import os

import solcx
import websockets
from solcx.exceptions import SolcError
from web3 import Web3

from solcx import compile_standard

from cliutils import sign


class ConnectionHost:
    def __init__(self, chain_link):
        self.chain_link = chain_link

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
        except Exception as e:
            print(e.args)


class Deployer:
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

    def deploy(self, bytecode, abi, url_shard="ws://127.0.0.1:10000"):
        try:
            w3 = ConnectionHost(url_shard).connect()
            # Create the contract in Python
            contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            # Get the latest transaction
            address, key = sign()
            nonce = w3.eth.getTransactionCount(address)
            # Submit the transaction that deploys the contract
            transaction = contract.constructor().buildTransaction(
                {
                    "chainId": w3.eth.chain_id,
                    "gasPrice": w3.eth.gas_price,
                    "from": address,
                    "nonce": nonce,
                }
            )
            # Sign the transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=key)
            print("Deploying Contract...")
            transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            # Wait for the transaction to be mined, and get the transaction receipt
            receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
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
