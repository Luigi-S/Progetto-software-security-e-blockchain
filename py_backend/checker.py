import asyncio
import os

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
            rev_url = url.replace("ganaches", "127.0.0.1")
            self.w3Shard[rev_url] = ConnectionHost(url).connect()
            self.filters[rev_url] = self.w3Shard[rev_url].eth.filter('latest')
        
    def check_reserved(self):
            for event in self.deploy_filter.get_new_entries():
                user = event.args.user
                shardUrl = str(event.args.shard)
                name = str(event.args.name)
                print("Event 'DeployReserved' received:\n    user={}\n    shard={}\n    name={}".format(
                            user, shardUrl, name
                        ))
                self.reserved_deploys[(user, shardUrl)] = name

    async def deploy_loop(self):
        while True:
            try:        
                for shardUrl in self.w3Shard.keys():
                    w3 = self.w3Shard[shardUrl]
                    filter = self.filters[shardUrl]
                    
                    for blockHash in filter.get_new_entries():
                        num_tx = w3.eth.get_block_transaction_count(blockHash.hex())
                        timestamp = w3.eth.get_block(blockHash.hex()).timestamp
                        for tx_index in range(num_tx):
                            transactionHash = w3.eth.get_transaction_by_block(blockHash.hex(), tx_index).hash
                            tx = w3.eth.get_transaction(transactionHash)
                            tx_rcp = w3.eth.get_transaction_receipt(transactionHash)
                            user = tx["from"]
                            to = tx["to"]
                            address = tx_rcp.contractAddress
                            status = tx_rcp.status

                            #logging here?
                            #print("Transaction:\n    contractAddress={}\n    status={}\n    to={}".format(
                            #    address, status, to
                            #))
                            
                            if address and status and not to and w3.eth.get_code(address):
                                print("Deploy found in transaction log:\n    user={}\n    shard={}\n    address={}    \ntimestamp={}".format(
                                    user, shardUrl, address, timestamp
                                ))

                                reserved = False
                                name = ""
                                
                                self.check_reserved()
                                if (user, shardUrl) in self.reserved_deploys.keys():
                                    name = self.reserved_deploys[(user, shardUrl)]
                                    print("OK: deploy with name '{}' was previously reserved".format(name))
                                    reserved = True
                                    del self.reserved_deploys[(user, shardUrl)]
                                else:
                                    print("Manager bypassed: deploy was not previously reserved")

                                self.caller.call("deployFound", user, shardUrl, name, address, reserved, timestamp)
                            
                            if to and status and not w3.eth.get_code(to):
                                    print("Potential delete found in transaction log:\n    user={}\n    shard={}\n    address={}    \ntimestamp={}".format(
                                    user, shardUrl, to, timestamp
                                    ))
                                    self.caller.call("deleteFound", shardUrl, to)
            except Exception as e:
                print("Error [checker]: error occured in deploy loop\n" + str(type(e)) + " " + str(e))

            await asyncio.sleep(self.poll_interval)

    def start(self):
        print("Checker listening...\n")
        try:
            self.deploy_filter = self.caller.contract.events.DeployReserved.createFilter(fromBlock='latest')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                asyncio.gather(self.deploy_loop())
                )
        finally:
            loop.close()