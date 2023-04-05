import asyncio
import os

from connection_host import ConnectionHost

class Checker():
    
    def __init__(self, caller, base_port, top_port, ganache_host):
        self.caller = caller
        self.poll_interval = float(os.environ.get("POLL_INTERVAL"))
        self.w3_shard = {}
        self.filters = {}
        self.reserved_deploys = {}
        self.deploy_filter = self.caller.contract.events.DeployReserved.createFilter(fromBlock='latest')
        #host = "0.0.0.0"
        for port in range(base_port+1, top_port):
            url = f"ws://{ganache_host}:{str(port)}"
            #rev_url = url.replace(ganache_host, host)
            self.w3_shard[url] = ConnectionHost(url).connect()
            self.filters[url] = self.w3_shard[url].eth.filter('latest')
        
    def check_reserved(self):
        for event in self.deploy_filter.get_new_entries():
            user = event.args.user
            shard_url = str(event.args.shard)
            name = str(event.args.name)
            print(f"Event 'DeployReserved' received:\n    user={user}\n    shard={shard_url}\n    name={name}")
            self.reserved_deploys[(user, shard_url)] = name

    async def deploy_loop(self):
        while True:
            try:        
                for shard_url in self.w3_shard.keys():
                    w3 = self.w3_shard[shard_url]
                    _filter = self.filters[shard_url]
                    
                    for block_hash in _filter.get_new_entries():
                        num_tx = w3.eth.get_block_transaction_count(block_hash.hex())
                        timestamp = w3.eth.get_block(block_hash.hex()).timestamp
                        for tx_index in range(num_tx):
                            transaction_hash = w3.eth.get_transaction_by_block(block_hash.hex(), tx_index).hash
                            tx = w3.eth.get_transaction(transaction_hash)
                            tx_rcp = w3.eth.get_transaction_receipt(transaction_hash)
                            user = tx["from"]
                            to = tx["to"]
                            address = tx_rcp.contractAddress
                            status = tx_rcp.status
                            
                            if address and status and not to and w3.eth.get_code(address):
                                print( f"Deploy found in transaction log:\n    user={user}\n    shard={shard_url}\n    address={address}    \ntimestamp={timestamp}")

                                reserved = False
                                name = ""
                                
                                self.check_reserved()
                                if (user, shard_url) in self.reserved_deploys.keys():
                                    name = self.reserved_deploys[(user, shard_url)]
                                    print(f"OK: deploy with name '{name}' was previously reserved")
                                    reserved = True
                                    del self.reserved_deploys[(user, shard_url)]
                                else:
                                    print("Manager bypassed: deploy was not previously reserved")

                                self.caller.call("deployFound", user, shard_url, name, address, reserved, timestamp)
                            
                            if to and status and not w3.eth.get_code(to):
                                print(f"Potential delete found in transaction log:\n    user={user}\n    shard={shard_url}\n    address={to}    \ntimestamp={timestamp}")
                                self.caller.call("deleteFound", shard_url, to)
            except Exception as e:
                print(f"Error [checker]: error occured in deploy loop\n{str(type(e))} {str(e)}")

            await asyncio.sleep(self.poll_interval)

    def start(self):
        print("Checker listening...\n")
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                asyncio.gather(self.deploy_loop())
                )
        finally:
            loop.close()