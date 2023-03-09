from time import sleep
import websockets
from web3 import Web3

class ConnectionHost:

    TIMEOUT = 10
    ATTEMPTS = 3
    SLEEP = 1

    def __init__(self, chain_link):
        self.chain_link = chain_link

    def connect(self):
        web3 = None
        for _ in range(self.ATTEMPTS):
            try:
                web3 = Web3(Web3.WebsocketProvider(self.chain_link))
            except TimeoutError:
                print("Timeout error")
            except websockets.exceptions.InvalidURI:
                print("Invalid URI")
            if web3.isConnected():
                print(f"WebSocket connected at url {self.chain_link} !")
                break
            sleep(self.SLEEP)
        return web3