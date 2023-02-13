import web3
import asyncio
import os
import json

from caller import Caller
from connection_host import ConnectionHost

class Checker():
    
    def __init__(self, caller, base_port, top_port):
        self.caller = caller
        self.poll_interval = float(os.environ.get("POLL_INTERVAL"))
        self.w3Shard = {}
        self.filters = {}
        self.reserved_deploys = {}

        for port in range(base_port, top_port):
            url = "ws://ganaches:" + str(port)
            self.w3Shard[url] = ConnectionHost(url).connect()
            self.filters[url] = self.w3Shard[url].eth.filter('latest')

    async def event_loop(self, deploy_filter):
        while True:
            for event in deploy_filter.get_new_entries():
                user = event.args.user
                shardUrl = str(event.args.shard)
                name = str(event.args.name)
                print("Event 'DeployReserved' received:\n    user={}\n    shard={}\n    name={}".format(
                            user, shardUrl, name
                        ))
                self.reserved_deploys[(user, shardUrl)] = name

            await asyncio.sleep(self.poll_interval)

    async def deploy_loop(self):
        while True:

            for shardUrl in self.w3Shard.keys():
                w3 = self.w3Shard[shardUrl]
                filter = self.filters[shardUrl]
                
                for blockHash in filter.get_new_entries():
                    num_tx = w3.eth.get_block_transaction_count(blockHash.hex())
                    for tx_index in range(num_tx):
                        transactionHash = w3.eth.get_transaction_by_block(blockHash.hex(), tx_index).hash
                        tx = w3.eth.get_transaction(transactionHash)
                        tx_rcp = w3.eth.get_transaction_receipt(transactionHash)
                        user = tx["from"]
                        to = tx["to"]
                        address = tx_rcp.contractAddress
                        status = tx_rcp.status

                        #print("Transaction:\n    contractAddress={}\n    status={}\n    to={}".format(
                        #    address, status, to
                        #))
                        
                        if address and status and not to and w3.eth.get_code(address):
                            print("Deploy found in transaction log:\n    user={}\n    shard={}\n    address={}".format(
                                user, shardUrl, address
                            ))

                            reserved = False
                            name = ""
                            
                            if (user, shardUrl) in self.reserved_deploys.keys():
                                name = self.reserved_deploys[(user, shardUrl)]
                                print("OK: deploy with name '{}' was previously reserved".format(name))
                                reserved = True
                                del self.reserved_deploys[(user, shardUrl)]
                            else:
                                print("Manager bypassed: deploy was not previously reserved")

                            self.caller.call("deployFound", user, shardUrl, name, address, reserved)
                        
                        if to and status and not w3.eth.get_code(to):
                                print("Potential delete found in transaction log:\n    user={}\n    shard={}\n    address={}".format(
                                user, shardUrl, to
                                ))
                                self.caller.call("deleteFound", shardUrl, to)

            
            await asyncio.sleep(self.poll_interval)

    def start(self):
        print("Checker listening...\n")
        deploy_filter = self.caller.contract.events.DeployReserved.createFilter(fromBlock='latest')
        #delete_filter = self.caller.contract.events.CheckDeleteRequest.createFilter(fromBlock='latest')
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(self.event_loop(deploy_filter), self.deploy_loop())
                )
        finally:
            loop.close()
            
def init(ORACLE_ADDRESS):
    URL = os.environ.get("URL")
    ADMIN_ADDRESS = os.environ.get("ADMIN_ADDRESS")
    ADMIN_PK = os.environ.get("ADMIN_PK")
    PORTS = int(os.environ.get("PORTS"))

    with open("abi/Oracle.json", "r") as file:
        oracle_abi = json.load(file)
        oracle_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, ORACLE_ADDRESS, oracle_abi)
        checker = Checker(oracle_caller, 10000, 10000 + PORTS)
        checker.start()