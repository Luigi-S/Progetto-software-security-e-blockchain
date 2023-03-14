import os
import warnings

import web3
from dotenv import load_dotenv
from pathlib import Path

from web3 import Web3
from web3.exceptions import ValidationError, ContractLogicError

from call import Caller
from cliutils import signWithAdress
from compiler import compile, deploy
from prettytable import PrettyTable
from datetime import datetime

"""Specific exceptions"""
class DeployMapError(Exception):
    pass

class OnChain():
    manager_shard = "ws://127.0.0.1:10000"
    manager_abi: str
    manager_address: str
    manager: Caller

    def __init__(self):
        try:
            load_dotenv(os.path.realpath(os.path.dirname(__file__)) + "/../py_backend/.env")
            self.manager_address = os.environ.get("MANAGER_ADDRESS")
        except:
            print("SYSTEM ERROR: Impossible to find file ./py_backend/.env")
            raise SystemExit(1)

        try:
            with open(os.path.realpath(os.path.dirname(__file__)) + "/../py_backend/abi/Manager.json", "r") as f:
                self.manager_abi = f.read().__str__()
                self.manager_abi.replace("\"", "\\\"")
        except:
            print("SYSTEM ERROR: Impossible to find file Manager.json")
            raise SystemExit(1)

        self.manager = Caller(contract_address=self.manager_address, abi=self.manager_abi,
                              chain_link=self.manager_shard)  # .get_contract()

    def deploySC(self, path_file: str, addressGiven):
        private_key = signWithAdress(addressGiven)
        try:
            target = Path(path_file)
            if not target.exists():
                print("The target directory doesn't exist.\n")
                print("Tip: if you tried to insert a file name, you have to specify the correct format.")
            elif not target.is_dir():
                if target.suffix == ".sol":
                    bytecode, abi = compile(path_file)

                    for elem in bytecode:
                        receipt = self.manager.signTransactionKey(
                            self.manager.contract.functions.reserveDeploy,
                            addressGiven,
                            private_key,
                            tuple([elem])
                        )
                        warnings.filterwarnings("ignore")
                        event = self.manager.contract.events.DeployUrl().processReceipt(receipt)
                        url = event[0].args["url"]
                        print("The contract is ready to be deployed to the shard at the url: " + str(url))

                        deploy(bytecode=bytecode[elem], abi=abi[elem], url_shard=url, address=addressGiven,
                               key=private_key)
                else:
                    print("Non valid input: impossible to find a deployable contract.")

            else:
                print("Non valid input: impossible to find a deployable contract.")

        except TypeError:
            print("The used account has a private key that doesn't correspond to the public key")
        except Exception as e:
            print(e.__class__)
            print(e)

    def setShardingAlgorithm(self, id_alg: int, my_address):
        try:
            receipt = self.manager.signTransaction(
                self.manager.contract.functions.setAlg,
                my_address,
                tuple([id_alg])
            )
            event = self.manager.contract.events.ChangedAlgorithm().processReceipt(receipt)
            print("Sharding algorithm changed to: " + str(event[0].args["newAlg"]))
        except ValidationError:
            print("The method called hasn't been found or the type of parameters wasn't correct.")
        except ContractLogicError as e1:
            print("ERROR: " + e1.args[0][70:])  # Acquisiamo il messaggio lanciato durante la revert
        except Exception as e:
            print(e.__class__)
            print(e)

    def setShardStatus(self, shard_id: int, status: bool, my_address):
        try:
            self.manager.signTransaction(
                self.manager.contract.functions.setShardStatus,
                my_address,
                (shard_id, status)
            )
            print("Shard n. " + shard_id.__str__() + " has now the status \"" + status.__str__() + "\"")
        except ValidationError:
            print("The method called hasn't been found or the type of parameters wasn't correct.")
        except ContractLogicError as e1:
            print("ERROR: " + e1.args[0][70:])  # Acquisiamo il messaggio lanciato durante la revert
        except Exception as e:
            print(e.__class__)
            print(e)

    def showDeployMap(self):
        map = self.getDeployMap()
        try:
            pt = PrettyTable()
            pt.field_names = ["Id", "Shard Url", "Contract Address", "Name", "User Address", "Deploy Time", "Reserved"]
            for sc in map:
                pt.add_row(sc)
            print(pt)
        except Exception as e:
            raise DeployMapError("Could not get contract list...")

    def getDeployMap(self):
        try:
            map = self.manager.contract.functions.getDeployMap().call()
            x_list = []
            for i, sc in enumerate(map):
                x = list(sc)
                x[0] = i
                x[2] = Web3.toChecksumAddress(x[2].hex())
                x[5] = datetime.fromtimestamp(x[5]).strftime("%d/%m/%Y, %H:%M:%S")
                x_list.append(x)
            return x_list
        except Exception as e:
            raise DeployMapError("Could not get contract list...")
