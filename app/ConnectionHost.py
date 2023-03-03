import websockets
from web3 import Web3


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


