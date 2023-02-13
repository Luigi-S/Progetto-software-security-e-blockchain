import re
from dotenv import dotenv_values
from eth_account import Account
from ast import literal_eval


class Logger:
    def __init__(self, address):
        if re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=address) is not None:
            self._address = address
        else:
            raise Exception("Invalid address")
        self._map = dotenv_values(".env", verbose=False)

    def getAddress(self):
        return self._address

    def getKey(self, passwd):
        try:
            x = literal_eval(self._map[self._address])
            return Account.decrypt(x, password=passwd).hex()
        except KeyError:
            raise Exception("Address not registered on this device")

    def register(self, key, passwd):
        try:
            encrypted = Account.encrypt(key, passwd)
            with open(".env", "a") as f:
                f.write(f"{self._address}={encrypted}\n")
        except IOError:
            raise Exception("Could not store account")
        except Exception as e:
            raise Exception("Registation failed", e.args)
