from cliutils import insert_args, sign
from compiler import ConnectionHost


class Caller2:
    def __init__(self, chain_link, contract_address, abi):
        try:
            self.w3 = ConnectionHost(chain_link).connect()
            self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        except ValueError:
            raise Exception("File does not contain an ABI")

    def get_abi(self):
        return self.contract.functions.abi

    def method_call(self, method_i):
        # spostare in file o classe apposita...
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
            my_address, private_key = sign()
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
            self.w3.eth.wait_for_transaction_receipt(transaction_hash)
            return "Transaction correctly sent"
        else:
            args = insert_args(inputs)
            return func.__call__(*args).call()
