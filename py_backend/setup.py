import solcx
import os
import json
from web3 import Web3
import web3
from dotenv import load_dotenv

from deployer import Deployer
from caller import Caller

def main():
    load_dotenv()
    URL = os.environ.get("URL")
    ADMIN_ADDRESS = os.environ.get("ADMIN_ADDRESS")
    ADMIN_PK = os.environ.get("ADMIN_PK")
    #BASE_PORT = os.environ.get("BASE_PORT")
    #TOP_PORT = os.environ.get("TOP_PORT")

    deployer = Deployer(URL, ADMIN_ADDRESS, ADMIN_PK)

    manager_bytecode, manager_abi = deployer.compile("contracts/Manager.sol")
    manager_address = deployer.deploy(manager_bytecode, manager_abi)

    oracle_bytecode, oracle_abi = deployer.compile("contracts/Oracle.sol")
    oracle_address = deployer.deploy(oracle_bytecode, oracle_abi)

    oracle_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, oracle_address, oracle_abi)
    manager_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, manager_address, manager_abi)

    oracle_caller.call("setManager", manager_address)
    manager_caller.call("setOracle", oracle_address)

    for port in range(10000, 10004):
        url = "ws://127.0.0.1:" + str(port)
        manager_caller.call("addShard", url, True)
    
    with open(".env", "a") as file:
        file.write("\nORACLE_ADDRESS=" + oracle_address)

if __name__ == "__main__":
    main()