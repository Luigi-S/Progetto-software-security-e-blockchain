import re
import os
from dotenv import dotenv_values
from eth_account import Account
from ast import literal_eval


class Logger:
    def __init__(self, address):
        self.penv_path = os.path.realpath(os.path.dirname(__file__)) + "/../pwd.env"
        if re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=address) is not None:
            self._address = address
        else:
            raise Exception("Invalid address")
        self._map = dotenv_values(self.penv_path, verbose=False)

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
            if self._address in self._map.keys():
                self._map[self._address] = encrypted
                txt = ""
                for k in self._map.keys():
                    txt += f"{k}={self._map[k]}\n"
                with open(self.penv_path, "w") as f:
                    f.write(txt)
            else:
                with open(self.penv_path, "a") as f:
                    f.write(f"{self._address}={encrypted}\n")
        except IOError:
            raise Exception("Could not store account")
        except Exception as e:
            raise Exception("Registation failed", e.args)
