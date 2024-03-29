import os
from pathlib import Path
from web3 import Web3
from web3.exceptions import ValidationError, ContractLogicError
import requests

from call import Caller
from cliutils import signWithAddress
from compiler import compile, deploy
from prettytable import PrettyTable
from datetime import datetime

"""Specific exceptions"""
class DeployMapError(Exception):
    pass

class OnChain():
    manager_shard : str
    manager_abi: str
    manager_address: str
    manager: Caller

    def __init__(self):
        try:
            ganache_host = os.environ.get("GANACHE_HOST")
            base_port = int(os.environ.get("BASE_PORT"))
            self.manager_shard = f"ws://{ganache_host}:{base_port}"
            py_backend_host = os.environ.get("PY_BACKEND_HOST")
            api_port = os.environ.get("API_PORT")
            api_url  = f"http://{py_backend_host}:{api_port}"
            self.manager_abi = requests.get(f"{api_url}/manager_abi").text
            self.manager_abi.replace("\"", "\\\"")
            self.manager_address = requests.get(f"{api_url}/manager_addr").text
            self.manager = Caller(contract_address=self.manager_address, abi=self.manager_abi,
                              chain_link=self.manager_shard)
        except Exception as e:
            print("SYSTEM ERROR: Impossible to load configurations")
            print(f"{str(e)}")
            raise SystemExit(1)

          # .get_contract()

    def deploySC(self, path_file: str, addressGiven, private_key = None):
        msg = ''
        try:
            target = Path(path_file)
            if not target.exists():
                print("The target does not exist")
                #print("Tip: if you tried to insert a file name, you have to specify the correct format.")
            elif not target.is_dir():
                if target.suffix == ".sol":
                    bytecode, abi = compile(path_file)
                    if not private_key:
                        private_key = signWithAddress(addressGiven)
                    for elem in bytecode:
                        receipt = self.manager.signTransaction(
                            self.manager.contract.functions.reserveDeploy,
                            addressGiven,
                            tuple([elem]),
                            private_key
                        )
                        event = self.manager.contract.events.DeployUrl().processReceipt(receipt)
                        url = event[0].args["url"]
                        #print("The contract is ready to be deployed to the shard at the url: " + str(url))

                        deploy(bytecode=bytecode[elem], abi=abi[elem], url_shard=url, address=addressGiven,
                               key=private_key)
                        msg = "Contract deployed!"
                else:
                    msg = "Non valid input: impossible to find a deployable contract"

            else:
                msg = "Non valid input: impossible to find a deployable contract"

        except TypeError as e:
            msg = f"TypeERROR: {str(e)}"
        except IOError:
            msg = "ERROR: I/O error"
        except ValueError as e:
            msg = f"{str(e)}"
        finally:
            print(msg)
            return msg

    def setShardingAlgorithm(self, id_alg: int, my_address, key = None):
        msg = ""
        try:
            receipt = self.manager.signTransaction(
                self.manager.contract.functions.setAlg,
                my_address,
                tuple([id_alg]),
                key
            )
            event = self.manager.contract.events.ChangedAlgorithm().processReceipt(receipt)
            msg = "Sharding algorithm changed"
        except ValidationError:
            msg = "The method called hasn't been found or the type of parameters wasn't correct."
        except ContractLogicError as e:
            msg = "ERROR: " + e.args[0][70:]  # Acquisiamo il messaggio lanciato durante la revert
        finally:
            print(msg)
            return msg
        
    def setShardStatus(self, shard_id, status, my_address, key = None):
        msg = ""
        try:
            self.manager.signTransaction(
                self.manager.contract.functions.setShardStatus,
                my_address,
                (shard_id, status),
                key
            )
            msg = "Shard " + shard_id.__str__() + " is now " + ("enabled" if status else "disabled")
        except ValidationError:
            msg = "The method called hasn't been found or the type of parameters wasn't correct."
        except ContractLogicError as e1:
            msg = "ERROR: " + e1.args[0][70:]  # Acquisiamo il messaggio lanciato durante la revert
        finally:
            print(msg)
            return msg
        
    def showDeployMap(self):
        map = self.getDeployMap()
        try:
            pt = PrettyTable()
            pt.field_names = ["Id", "Shard Url", "Contract Address", "Name", "User Address", "Deploy Time", "Reserved"]
            for sc in map:
                pt.add_row(sc)
            return str(pt)
        except Exception as e:
            raise DeployMapError("Could not get contract list...")

    def getDeployMap(self):
        try:
            map = self.manager.contract.functions.getDeployMap().call()
            x_list = []
            for i, sc in enumerate([x for x in map if x[1]]):
                x = list(sc)
                x[0] = i
                x[2] = Web3.toChecksumAddress(x[2].hex())
                x[5] = datetime.fromtimestamp(x[5]).strftime("%d/%m/%Y, %H:%M:%S")
                x_list.append(x)
            return x_list
        except Exception:
            raise DeployMapError("Could not get contract list...")

    def showShardList(self, map):
        pt = PrettyTable()
        pt.field_names = ["Id","Shard Url", "Active", "Deployments"]
        for sc in map:
            pt.add_row(sc)
        return str(pt)

    def getShardList(self):
        map = self.manager.contract.functions.getShardList().call()
        return [[i] + list(sc) for i,sc in enumerate(map)]

    def getCurrentAlg(self):
        return self.manager.contract.functions.getCurrentAlg().call()