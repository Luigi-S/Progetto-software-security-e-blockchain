import json

from web3.contract import Contract
from pathlib import Path

from compiler import Caller
from compiler import Deployer

class OnChain():

    manager_shard = "ws://127.0.0.1:8545"
    manager_abi: str
    manager_address = "0x5b1869D9A4C187F2EAa108f3062412ecf0526b24"
    contract: Contract

    def __init__(self):
        with open("py_backend/.env") as f:
            manager_address = f.readline().__str__()
            manager_address = manager_address[16:]
            print(manager_address)
            #self.manager_address = manager_address

        with open("app/compiled_contracts/Manager.json", "r") as f:
            self.manager_abi = f.read().__str__()
            self.manager_abi.replace("\"", "\\\"")

        self.contract = Caller(contract_address=self.manager_address, abi=self.manager_abi, chain_link=self.manager_shard).get_contract()

    def call(self, address: str, abi, func: str, param, chain_link):
        caller = Caller(address, abi, chain_link)
        try:
            tx_receipt = caller.call(func, *param)
            return tx_receipt
        except TypeError as e:
            try:
                tx_receipt = caller.call(func, param)
                return tx_receipt
            except Exception:
                print("Something went wrong :(")

    def deploySC(self, path_file: str, abi=None):
        try:
            target = Path(path_file)
            if not target.exists():
                print("The target directory doesn't exist.\n")
                print("Tip: if you tried to insert a file name, you have to specify the correct format.")
                raise SystemExit(1)
            elif not target.is_dir():
                if target.suffix == ".sol":
                    func = Caller(self.manager_address, self.manager_abi, self.manager_shard).get_func("reserveDeploy")
                    id, url = func().call()
                    tx_receipt = self.call(address=self.manager_address, abi=self.manager_abi,
                              func="reserveDeploy", param=(None), chain_link=self.manager_shard)
                    event = self.contract.events.DeployReserved().processReceipt(tx_receipt)
                    print("The contract n." + str(event[0].args["id"]) + " is ready to be deployed to the shard number "
                          + str(event[0].args["shardId"]) + " at the url: " + str(event[0].args["shard"]))

                    d = Deployer()
                    bytecode, abi = d.compile(path_file)
                    for elem in bytecode:
                        address = d.deploy(bytecode=bytecode[elem], abi=abi[elem], url_shard=url)
                        tx_receipt2 = self.call(address=self.manager_address, abi=self.manager_abi,
                                  func="declareDeploy", param=(id, address, elem), chain_link=self.manager_shard)
                        event2 = self.contract.events.DeployDeclared().processReceipt(tx_receipt2)
                        print("The contract n." + str(event2[0].args["id"]) + " named \"" + str(event2[0].args["name"])
                              + "\" with the address '" + str(event2[0].args["addr"])
                              + " has been deployed to the shard number "
                              + str(event2[0].args["shardId"]) + " at the url: " + str(event2[0].args["shard"]))

                # DA SISTEMARE
                elif target.suffix == ".json" and abi is not None and Path(abi).suffix == ".json":
                    try:
                        with open(path_file, "r") as file:
                            bytecode = json.load(file)
                        with open(abi, "r") as file2:
                            abi = json.load(file2)
                        d = Deployer()
                        d.deploy(bytecode=bytecode["object"], abi=abi)
                    except Exception as e:
                        print(e.__class__)
                        raise SystemExit(1)

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

    def deleteSC(self, abi, id_SC, address, url_shard):
        try:
            self.call(address=address, abi=abi, func="destroy", param=(None), chain_link=url_shard)
            print("Smart contract successfully deleted.")

            tx_receipt = self.call(address=self.manager_address, abi=self.manager_abi,
                                    func="declareDel", param=(id_SC), chain_link=self.manager_shard)
            event = self.contract.events.DeleteDeclared().processReceipt(tx_receipt)
            print("The contract n." + str(event[0].args["id"]) + " named \"" + str(event[0].args["name"])
                  + "\" with the address '" + str(event[0].args["addr"])
                  + " has been deleted from the shard number "
                  + str(event[0].args["shardId"]) + " at the url: " + str(event[0].args["shard"]))

        except Exception as e:
            print(e)
            raise SystemExit(1)

    def setShardingAlgorithm(self, id_alg: int):
        try:
            tx_receipt = self.call(address=self.manager_address, abi=self.manager_abi,
                                   func="setAlg", param=(id_alg), chain_link=self.manager_shard)
            event = self.contract.events.ChangedAlgorithm().processReceipt(tx_receipt)
            print("Sharding algorithm changed to: " + str(event[0].args["newAlg"]))
        except Exception as e:
            #print(e)
            raise SystemExit(1)

    def setShardStatus(self, shard_id: int, status: bool):
        try:
            self.call(address=self.manager_address, abi=self.manager_abi,
                      func="setShardStatus", param=(shard_id, status), chain_link=self.manager_shard)
        except Exception as e:
            # print(e)
            raise SystemExit(1)

    def getDeployMap(self):
        try:
            self.call(address=self.manager_address, abi=self.manager_abi,
                      func="getDeployMap", param=(), chain_link=self.manager_shard)
        except Exception as e:
            raise Exception("Could not get contract list...")
