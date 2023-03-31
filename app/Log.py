import re
import os
import codecs

from dotenv import dotenv_values
from eth_account import Account
from ast import literal_eval
from web3 import Web3
from eth_keys import keys

"""Specific exceptions"""
class InvalidAddress(Exception):
    pass
class RegistrationFailed(Exception):
    pass


class Logger:

    def __init__(self, address):
        self.penv_path = os.path.realpath(os.path.dirname(__file__)) + "/../pwd.env"
        if re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=address) is not None:
            self._address = address
        else:
            raise InvalidAddress("Address is not valid")
        self._map = dotenv_values(self.penv_path, verbose=False)

    def getAddress(self):
        return self._address

    def getKey(self, passwd):
        try:
            x = literal_eval(self._map[self._address])
            return Account.decrypt(x, password=passwd).hex()
        except KeyError:
            # possibilmente cambiare, messaggio misleading, nome eccezione anche
            raise RegistrationFailed("Address not registered on this device")
        except ValueError:
            raise RegistrationFailed("Password does not match")

    def address_matches_key(self, key):
        decoder = codecs.getdecoder("hex_codec")
        privk = key.removeprefix("0x")
        private_key_bytes = decoder(privk)[0]
        pk = keys.PrivateKey(private_key_bytes).public_key
        hash = Web3.sha3(hexstr=str(pk))
        calc_address = Web3.toChecksumAddress(Web3.toHex(hash[-20:]))
        return calc_address == self._address
            
    def register(self, key, passwd):
        try:
            if self.address_matches_key(key):
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
            else:
                raise RegistrationFailed("Address does not match private key")
        except IOError:
            print("I/O error")
        except Exception as err:
            raise RegistrationFailed from err
