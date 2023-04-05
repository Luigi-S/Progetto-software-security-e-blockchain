import os
import codecs
import json
import sys
from dotenv import load_dotenv
from web3 import Web3
from eth_keys import keys

from deployer import Deployer
from caller import Caller
from checker import Checker

def address_matches_key(address, key):
    decoder = codecs.getdecoder("hex_codec")
    privk = key.removeprefix("0x")
    private_key_bytes = decoder(privk)[0]
    pk = keys.PrivateKey(private_key_bytes).public_key
    pk_hash = Web3.sha3(hexstr=str(pk))
    calc_address = Web3.toChecksumAddress(Web3.toHex(pk_hash[-20:]))
    address = Web3.toChecksumAddress(address)
    return calc_address == address

def ports_are_ok(ports, base_port):
    ports_ok = 2 <= ports <= 10
    port_range_valid = base_port >= 1025 and (base_port + ports) <= 65535
    return ports_ok and port_range_valid

def main():
    
    try:
        ADMIN_ADDRESS = os.environ.get("ADMIN_ADDRESS")
        ADMIN_PK = os.environ.get("ADMIN_PK")
        if not address_matches_key(ADMIN_ADDRESS, ADMIN_PK):
            raise ValueError("admin account is invalid: address does not match private key")
        
        PORTS = int(os.environ.get("PORTS"))
        BASE_PORT =  int(os.environ.get("BASE_PORT"))
        
        if not ports_are_ok(PORTS, BASE_PORT):
            raise ValueError("ports are not valid")
        
        #HOST = os.environ.get("HOST")
        GANACHE_HOST = os.environ.get("GANACHE_HOST")
        URL = f"ws://{GANACHE_HOST}:{BASE_PORT}" 
        #HOST_URL = URL.replace(GANACHE_HOST, HOST)

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

            for port in range(BASE_PORT+1, BASE_PORT + PORTS):
                url = f"ws://{GANACHE_HOST}:{str(port)}"
                manager_caller.call("addShard", url, True)
            
            with open(".env", "w") as file:
                file.write(f"MANAGER_ADDRESS={manager_address}\nORACLE_ADDRESS={oracle_address}")
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
            checker = Checker(oracle_caller, BASE_PORT, BASE_PORT + PORTS, GANACHE_HOST)
        
        os.system("python api.py &")

        checker.start()

    except Exception as e:
        print(f"Error [setup]: {str(type(e))}  {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()