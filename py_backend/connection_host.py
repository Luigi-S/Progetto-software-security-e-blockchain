import web3
import websockets
from solcx.exceptions import SolcError
from web3 import Web3
from time import sleep

class ConnectionHost:

    MAX_ATTEMPTS = 5
    WAIT_TIME = 1

    def __init__(self, chain_link):
        self.chain_link = chain_link

    def get_w3(self):
        try:
            web3 = Web3(Web3.WebsocketProvider(self.chain_link))
            if web3.isConnected():
                return web3
        except TimeoutError as e1:
            print("ERROR - timeout error:")
            print(e1)
        except websockets.exceptions.InvalidURI as e2:
            print("ERROR - invalid URI:")
            print(e2)
    
    def connect(self):
        w3 = self.get_w3()
        att = 0
        
        while att < self.MAX_ATTEMPTS and not w3 :
            print("WebSocket not connected at url {}. Retrying...".format(self.chain_link))
            sleep(self.WAIT_TIME)
            w3 = self.get_w3()
            att += 1
        
        if w3:
            print("WebSocket connected at url {} !".format(self.chain_link))
            return w3
        else:
            print("No remaining connection attempt")