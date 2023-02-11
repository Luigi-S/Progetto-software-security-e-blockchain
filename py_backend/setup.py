import os
from dotenv import load_dotenv

from deployer import Deployer
from caller import Caller
from checker import init

def main():
    URL = os.environ.get("URL")
    ADMIN_ADDRESS = os.environ.get("ADMIN_ADDRESS")
    ADMIN_PK = os.environ.get("ADMIN_PK")
    PORTS = int(os.environ.get("PORTS"))
    
    try:
        load_dotenv()
        manager_address = os.environ.get("MANAGER_ADDRESS")
        oracle_address = os.environ.get("ORACLE_ADDRESS")
    except Exception as e:
        print(e)

    deployer = Deployer(URL, ADMIN_ADDRESS, ADMIN_PK)

    manager_bytecode, manager_abi = deployer.compile("contracts/Manager.sol")
    oracle_bytecode, oracle_abi = deployer.compile("contracts/Oracle.sol")
    
    if not manager_address or not oracle_address:
        manager_address = deployer.deploy(manager_bytecode, manager_abi)
        oracle_address = deployer.deploy(oracle_bytecode, oracle_abi)
        
        oracle_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, oracle_address, oracle_abi)
        manager_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, manager_address, manager_abi)

        oracle_caller.call("setManager", manager_address)
        manager_caller.call("setOracle", oracle_address)

        for port in range(10000, 10000 + PORTS):
            url = "ws://ganaches:" + str(port)
            manager_caller.call("addShard", url, True)
        
        with open(".env", "w") as file:
            file.write("MANAGER_ADDRESS={}\nORACLE_ADDRESS={}".format(manager_address, oracle_address))
    
    init(oracle_address)

if __name__ == "__main__":
    main()