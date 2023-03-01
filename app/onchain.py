import os

from dotenv import load_dotenv
from pathlib import Path

from app.call import Caller
from compiler import Deployer

class OnChain():

    manager_shard = "ws://127.0.0.1:10000"
    manager_abi: str
    manager_address: str
    manager: Caller

    def __init__(self):
        load_dotenv("py_backend/.env")
        self.manager_address = os.environ.get("MANAGER_ADDRESS")

        with open("py_backend/abi/Manager.json", "r") as f:
            self.manager_abi = f.read().__str__()
            self.manager_abi.replace("\"", "\\\"")

        self.manager = Caller(contract_address=self.manager_address, abi=self.manager_abi, chain_link=self.manager_shard) #.get_contract()


    def call(self, address: str, abi, func: str, param, chain_link):
        caller = Caller(contract_address=address, abi=abi, chain_link=chain_link)
        try:
            tx_receipt = caller.signTransaction(func, *param)
            return tx_receipt
        except TypeError as e:
            try:
                tx_receipt = caller.call(func, param)
                return tx_receipt
            except Exception:
                print("Something went wrong :(")

    def deploySC(self, path_file: str, nome_sc: str = ""):
        try:
            target = Path(path_file)
            if not target.exists():
                print("The target directory doesn't exist.\n")
                print("Tip: if you tried to insert a file name, you have to specify the correct format.")
                raise SystemExit(1)
            elif not target.is_dir():
                if target.suffix == ".sol":
                    #func = Caller(self.manager_address, self.manager_abi, self.manager_shard).get_func("reserveDeploy")
                    receipt = self.manager.signTransaction(
                        self.manager.contract.functions.reserveDeploy,
                        [nome_sc]
                    )
                    event = self.manager.contract.events.DeployReserved().processReceipt(receipt)
                    url = event[0].args["url"]
                    print("The contract is ready to be deployed to the shard at the url: " + str(url))

                    bytecode, abi = Deployer.compile(path_file)
                    d = Deployer()
                    for elem in bytecode:
                        d.deploy(bytecode=bytecode[elem], abi=abi[elem], url_shard=url)

                else:
                    print("Non valid input: impossible to find a deployable contract.")
                    raise SystemExit(1)

            else:
                print("Non valid input: impossible to find a deployable contract.")
                raise SystemExit(1)

        except Exception as e:
            print(e)
            raise SystemExit(1)

    #def findSC(self):
        #Verifica se lo SC è deployato in qualche shard e in tale caso chiama deleteSC() passando indirizzo SC e url_shard

    def deleteSC(self, abi, address, url_shard):
        try:
            caller = Caller(contract_address=address, abi=abi, chain_link=url_shard)
            caller.signTransaction(caller.contract.functions.destroy())
            print("Smart contract successfully deleted.")
        except AttributeError:
            print("Smart contract is not deletable")
            exit(1)
        except Exception as e:
            print(e)
            raise SystemExit(1)

    def setShardingAlgorithm(self, id_alg: int):
        try:
            receipt = self.manager.signTransaction(
                self.manager.contract.functions.reserveDeploy,
                (id_alg)
            )
            event = self.manager.contract.events.ChangedAlgorithm().processReceipt(receipt)
            print("Sharding algorithm changed to: " + str(event[0].args["newAlg"]))
        except Exception as e:
            #print(e)
            raise SystemExit(1)

    def setShardStatus(self, shard_id: int, status: bool):
        try:
            self.manager.signTransaction(
                self.manager.contract.functions.setShardStatus,
                (shard_id, status)
            )
        except Exception as e:
            # print(e)
            raise SystemExit(1)

    def getDeployMap(self):
        try:
            print(self.manager.contract.functions.getDeployMap().call())
        except Exception as e:
            raise Exception("Could not get contract list...")
