from web3 import Web3
from connection_host import ConnectionHost

class Caller():
    
    def __init__(self, chain_link, d_address, d_pk, contract_address, abi):
        
        self.w3 = ConnectionHost(chain_link).connect()
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        self.chain_id = self.w3.eth.chain_id
        self.d_address = d_address
        self.d_pk = d_pk

    def call(self,  func_name, *args):
        try:
            func = self.contract.get_function_by_name(func_name)
            transaction = func(*args).buildTransaction(
                {
                    "chainId": self.chain_id,
                    "gasPrice": self.w3.eth.gas_price,
                    "from": self.d_address,
                    "nonce": self.w3.eth.getTransactionCount(self.d_address),
                    #"to" : self.contract.address
                }
            )
            signed_transaction = self.w3.eth.account.sign_transaction(
                transaction, private_key=self.d_pk
            )
            tx_greeting_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)                                                            # <-(tqdm)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
            #TODO: exception handling di ogni genere
        except Exception as e:
            print(type(e))
            print(e)