from compiler import Caller
from compiler import Deployer


def call(address: str, abi, func: str, param):
    caller = Caller(address, abi)
    try:
        function = caller.call(func, *param)
    except TypeError as e:
        function = caller.call(func, param)
        return function

    return function

def deploy():
    file = ""
    with open("app/compiled_contracts/Manager.json", "r") as f:
        file = f.read().__str__()
        file.replace("\"", "\\\"")

    manager_address = "0x3Ad438090D6CA3c26f2e4C4c2E7833066B87e709"
    try:
        """
        call(address=manager_address,
                          abi=file, func="addShard", param=("ws://127.0.0.1:8547", True))
        """

        func = Caller(manager_address, file).get_func("reserveDeploy")
        id, url = func().call()
        call(address=manager_address,
                                      abi=file, func="reserveDeploy", param=(None))

        """
        func2 = call(address=manager_address,
                           abi=file, func="deployMap", param=(id))
        struct = func2(id).call()
        """

        d = Deployer()
        bytecode, abi = d.compile("app/contract.sol")
        for elem in bytecode:
            address = d.deploy(bytecode=bytecode[elem], abi=abi[elem], url_shard=url)
            #addr = address[2:]
            #addr = bytes.fromhex(addr)
            call(address=manager_address,
                 abi=file, func="declareDeploy", param=(id, address, elem))

        print("")

    except Exception as e:
        print(e)
        raise SystemExit(1)