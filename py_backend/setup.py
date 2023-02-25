import os
from dotenv import load_dotenv
from web3 import Web3
from eth_keys import keys
import codecs
import json

from deployer import Deployer
from caller import Caller
from checker import Checker

def main():
    
    try:
        ADMIN_ADDRESS = os.environ.get("ADMIN_ADDRESS")
        ADMIN_PK = os.environ.get("ADMIN_PK")
        decoder = codecs.getdecoder("hex_codec")
        privk = ADMIN_PK.removeprefix("0x")
        private_key_bytes = decoder(privk)[0]
        pk = keys.PrivateKey(private_key_bytes).public_key
        hash = Web3.sha3(hexstr=str(pk))
        calc_address = Web3.toChecksumAddress(Web3.toHex(hash[-20:]))
        address = Web3.toChecksumAddress(ADMIN_ADDRESS)
        
        if calc_address != address:
            raise ValueError("admin account is invalid")
        
        PORTS = int(os.environ.get("PORTS"))
        BASE_PORT =  int(os.environ.get("BASE_PORT"))
        if PORTS < 2 or PORTS > 10:
            raise ValueError("number of ports must be between 2 and 10")
        if BASE_PORT < 1025 or BASE_PORT + PORTS > 65535:
            raise ValueError("used ports must be between 1025 and 65535")
        
        URL = os.environ.get("URL")

        load_dotenv()
        manager_address = os.environ.get("MANAGER_ADDRESS")
        oracle_address = os.environ.get("ORACLE_ADDRESS")
        
        if not Web3.isChecksumAddress(manager_address) or not Web3.isChecksumAddress(oracle_address):
            print("Warning [setup]: manager or oracle address are invalid")
            manager_address = None
            oracle_address = None

        deployer = Deployer(URL, ADMIN_ADDRESS, ADMIN_PK)

        manager_bytecode, manager_abi = deployer.compile("contracts/Manager.sol")
        oracle_bytecode, oracle_abi = deployer.compile("contracts/Oracle.sol")
        
        if not manager_address or not oracle_address:
            print("Proceeding deploying new manager and new oracle contracts...")
            manager_address = deployer.deploy(manager_bytecode, manager_abi)
            manager_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, manager_address, manager_abi)
            oracle_address = deployer.deploy(oracle_bytecode, oracle_abi)
            oracle_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, oracle_address, oracle_abi)
                
            oracle_caller.call("setManager", manager_address)
            manager_caller.call("setOracle", oracle_address)

            for port in range(BASE_PORT, BASE_PORT + PORTS):
                url = "ws://ganaches:" + str(port)
                manager_caller.call("addShard", url, True)
            
            with open(".env", "w") as file:
                file.write("URL={}\nMANAGER_ADDRESS={}\nORACLE_ADDRESS={}".format(URL, manager_address, oracle_address))
        else:
            manager_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, manager_address, manager_abi)
            oracle_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, oracle_address, oracle_abi)
        
        manager_owner = manager_caller.contract.get_function_by_name("owner")().call()
        oracle_owner = oracle_caller.contract.get_function_by_name("owner")().call()
        if ADMIN_ADDRESS != manager_owner or ADMIN_ADDRESS != oracle_owner:
            raise ValueError("provided account is not admin")
        
        with open("abi/Oracle.json", "r") as file:
            oracle_abi = json.load(file)
            oracle_caller = Caller(URL, ADMIN_ADDRESS, ADMIN_PK, oracle_address, oracle_abi)
            checker = Checker(oracle_caller, BASE_PORT, BASE_PORT + PORTS)
            checker.start()
    
    except Exception as e:
        print("Error [setup]: " + str(type(e)) + " " + str(e))
        exit(1)

if __name__ == "__main__":
    main()