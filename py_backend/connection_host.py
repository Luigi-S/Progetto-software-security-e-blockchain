import websockets
from web3 import Web3
from time import sleep

class ConnectionHost:

    TIMEOUT = 10
    ATTEMPTS = 3
    SLEEP = 1

    def __init__(self, chain_link):
        self.chain_link = chain_link

    def connect(self):
        
        for _ in range(self.ATTEMPTS):
            try:
                web3 = Web3(Web3.WebsocketProvider(self.chain_link))
            except TimeoutError as e1:
                print("ERROR - timeout error:")
                print(e1)
            except websockets.exceptions.InvalidURI as e2:
                print("ERROR - invalid URI:")
                print(e2)
            if web3.isConnected():
                print("WebSocket connected at url {} !".format(self.chain_link))
                return web3
            sleep(self.SLEEP)