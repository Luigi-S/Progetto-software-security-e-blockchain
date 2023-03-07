import socket

from web3.exceptions import InvalidAddress

from ConnectionHost import ConnectionHost
from cliutils import insert_args, signWithAdress


class Caller:
    def __init__(self, chain_link, contract_address, abi):
        try:
            self.w3 = ConnectionHost(chain_link).connect()
            self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        except ValueError:
            raise Exception("File does not contain an ABI")

    def get_abi(self):
        return self.contract.functions.abi

    def method_call(self, method_i, address):
        try:
            c = self.get_abi()[int(method_i)]
            string_args = "("
            inputs = c["inputs"]
            for i in range(len(inputs)):
                string_args += inputs[i]["type"]
                if i != len(inputs)-1: string_args += ","
            string_args += ")"
            func = self.contract.get_function_by_signature(c["name"] + string_args)
            method_type = c["stateMutability"]
            if method_type != "pure" and method_type != "view" and method_type != "constant":
                args = insert_args(inputs)
                return self.signTransaction(func, address, args)
            else:
                args = insert_args(inputs)
                return func.__call__(*args).call()
        except InvalidAddress:
            print("The address doesn't exist.")
        except ValueError as e1:
            if isinstance(e1.args[0], dict):
                print(e1.args[0]['message'])   # not enough funds
                print("Exiting...")
                exit(1)
            elif e1.args[0].find("execution reverted") != -1:
                # se viene catchato un ValueError potrebbe essere perchè il metodo
                # dello SC non esiste o perchè esiste ma lancia una revert
                print("ERROR: " + e1.args[0][70:])  # Acquisiamo il messaggio lanciato durante la revert
                exit(1)
            else:
                print("The method called doesn't exist.\n")
                print("Tip: check if the abi used is the correct one.")
                exit(1)
        except TypeError:
            print("The params inserted aren't the same required by the function called.")
            exit(1)
        except socket.gaierror:
            print("System error occurred with socket.")
        except Exception as e:
            print(e)
            print(e.__class__)
            print("ERROR: System error occurred.")
            exit(1)

    def signTransaction(self, func, my_address, args=()):
        private_key = signWithAdress(my_address)
        transaction = func(*args).buildTransaction({
            "chainId": self.w3.eth.chain_id,
            "gasPrice": self.w3.eth.gas_price,  # stima il costo con una call
            "from": my_address,
            "nonce": self.w3.eth.getTransactionCount(my_address),
        })
        signed = self.w3.eth.account.sign_transaction(
            transaction, private_key=private_key
        )
        transaction_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return receipt
    def signTransactionKey(self, func, my_address, key, args=()):
        transaction = func(*args).buildTransaction({
            "chainId": self.w3.eth.chain_id,
            "gasPrice": self.w3.eth.gas_price,  # stima il costo con una call
            "from": my_address,
            "nonce": self.w3.eth.getTransactionCount(my_address),
        })
        signed = self.w3.eth.account.sign_transaction(
            transaction, private_key=key
        )
        transaction_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return receipt


