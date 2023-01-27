from io import StringIO

from dotenv import load_dotenv, dotenv_values
from eth_account import Account


class Logger:
    def __init__(self, address):
        self._address = address
        self._map = dotenv_values(".env")

    def getAddress(self):
        return self._address

    def getKey(self, passwd):
        try:
            return Account.decrypt(self._map[self._address], password=passwd)
        except KeyError as e:
            raise Exception("Address not registered on this device")

    def register(self, key, passwd):
        try:
            encrypted = Account.encrypt(key, passwd)
            config = StringIO(f"{self._address}={encrypted}")
            load_dotenv(stream=config)
        except Exception:
            # distinguere eccezioni?
            raise Exception("Registation failed")
