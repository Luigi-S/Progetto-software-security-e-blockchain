import binascii
import json
import os
from solcx import compile_standard
import solcx

from connection_host import ConnectionHost

class Deployer():

    def __init__(self, chain_link, d_address, d_pk):
        self.solc_version = os.environ.get("SOLC_VERSION")
        self.w3 = ConnectionHost(chain_link).connect()
        self.chain_id = self.w3.eth.chain_id
        self.d_address = d_address
        self.d_pk = d_pk

    def compile(self, contract_path):
        ret_abi = None
        ret_bytecode = None
        
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
                solc_version=self.solc_version,
            )

            # many contracts can be in a single .sol file
            
            bytecode = {}
            abi = {}
            contracts = compiled_sol["contracts"][contract_name].keys()
            for contract in contracts:
                bytecode[contract] = compiled_sol["contracts"][contract_name][contract]["evm"]["bytecode"]["object"]
                abi[contract] = json.loads(
                    compiled_sol["contracts"][contract_name][contract]["metadata"]
                )["output"]["abi"]
            
            ret_bytecode = bytecode[list(compiled_sol["contracts"][contract_name].keys())[0]]
            ret_abi = abi[list(compiled_sol["contracts"][contract_name].keys())[0]]

            abi_pathname = "abi/" + contract_name.replace(".sol", ".json")
            
            with open(abi_pathname, "w") as file:
                json.dump(ret_abi, file)

        except solcx.exceptions.SolcError:
            print("File .sol isn't syntactically correct.")
        except binascii.Error:
            print("File does not contain a valid bytecode.")
        except UnboundLocalError as e:
            print(e)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)
        
        return ret_bytecode, ret_abi

    def deploy(self, bytecode, abi):
        try:
            contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
            nonce = self.w3.eth.getTransactionCount(self.d_address)
            transaction = contract.constructor().buildTransaction(
                {
                    "chainId": self.chain_id,
                    "gasPrice": self.w3.eth.gas_price,
                    "from": self.d_address,
                    "nonce": nonce,
                }
            )
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.d_pk)
            transaction_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
            print(f"Contract deployed to address: {receipt.contractAddress}")
            return receipt.contractAddress
        except binascii.Error:
            print("File does not contain a valid bytecode.")
        except KeyError as e:
            print(e)
        except UnboundLocalError as e:
            print(e)
        except TypeError as e:
            print(e)
        except Exception as e:
            print(e)