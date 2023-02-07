from web3 import Web3
import web3
import asyncio
import os
from dotenv import load_dotenv
import json

from caller import Caller

class Checker():
    
    def __init__(self, caller, base_port, top_port):
        self.caller = caller
        self.poll_interval = float(os.environ.get("POLL_INTERVAL"))
        self.w3Shard = {}
        self.filters = {}
        self.deploys = {}

        for port in range(base_port, top_port):
            url = "ws://127.0.0.1:" + str(port)
            self.w3Shard[url] = Web3(Web3.WebsocketProvider(url))
            self.filters[url] = self.w3Shard[url].eth.filter({"fromBlock" : "latest"})
            self.deploys[url] = []

    async def event_loop(self, deploy_filter, delete_filter):
        while True:
            for CheckDeployRequest in deploy_filter.get_new_entries():
                self.handle_request(CheckDeployRequest, True)
            
            for CheckDeleteRequest in delete_filter.get_new_entries():
                self.handle_request(CheckDeleteRequest)
            
            await asyncio.sleep(self.poll_interval)


    def start(self):
        print("Checker listening\n")
        deploy_filter = self.caller.contract.events.CheckDeployRequest.createFilter(fromBlock='latest')
        delete_filter = self.caller.contract.events.CheckDeleteRequest.createFilter(fromBlock='latest')
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(self.event_loop(deploy_filter, delete_filter))
                )
        finally:
            loop.close()

    def handle_request(self, event, isDeploy = False):
        deployId = int(event.args.id)
        shardUrl = str(event.args.shard)
        address = event.args.addr
        user = event.args.user
        print("{} event received!\nChecking request:\n    deployId={}\n    shardUrl={}\n    user={}\n    address={}".format(
            "Deploy" if isDeploy else "Delete", deployId, shardUrl, user, address))

        result = False

        try:
            for x in self.filters[shardUrl].get_new_entries():
                tx = self.w3Shard[shardUrl].eth.get_transaction(x.transactionHash)
                tx_rcp = self.w3Shard[shardUrl].eth.get_transaction_receipt(x.transactionHash)
                
                cand_user = tx["from"]
                to = tx["to"]
                cand_address = tx_rcp.contractAddress
                status = tx_rcp.status
                
                if cand_address and to is None and status:
                    cand_address = bytes.fromhex(cand_address.replace("0x",""))
                    print("Deploy found in transaction log:\n    user={}\n    address={}".format(
                        cand_user, cand_address
                    ))
                    self.deploys[shardUrl].append((cand_user, cand_address))
            
            if isDeploy:
                try:
                    self.deploys[shardUrl].remove((user, address))
                    tx_exists = True
                    print("Deploy transaction exists!")
                except ValueError:
                    tx_exists = False
                    print("Deploy transaction does not exist...")
            else:
                tx_exists = True

            code_exists = True if self.w3Shard[shardUrl].eth.get_code(address) else False
            
            if code_exists:
                print("Contract code exists!")
            else:
                print("Contract code does not exist...")
            
            result = not( (tx_exists and code_exists) ^ isDeploy)
            if result:
                print("{} confirmed!".format("Deploy" if isDeploy else "Delete"))
            else:
                print("{} not confirmed...".format("Deploy" if isDeploy else "Delete"))
            print("__________________________________\n")
        except web3.exceptions.InvalidAddress:
            print("Invalid address")
        except Exception as e:
            print(type(e))
            print(e)
        finally:
            if isDeploy:
                self.caller.call("deployChecked", deployId, result)
            else:
                self.caller.call("deleteChecked", deployId, result)


def main():
    load_dotenv()
    URL = os.environ.get("URL")
    ADMIN_ADDRESS = os.environ.get("ADMIN_ADDRESS")
    ADMIN_PK = os.environ.get("ADMIN_PK")
    ORACLE_ADDRESS = os.environ.get("ORACLE_ADDRESS")
    
    with open("abi/Oracle.json", "r") as file:
        oracle_abi = json.load(file)
        oracle_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, ORACLE_ADDRESS, oracle_abi)
        checker = Checker(oracle_caller, 10000, 10004)
        checker.start()

if __name__ == "__main__":
    main()