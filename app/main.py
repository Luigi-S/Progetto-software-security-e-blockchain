"""Various imports"""
import re
from web3.datastructures import AttributeDict
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
from consolemenu.items import SubmenuItem, FunctionItem
import warnings

from onchain import OnChain, DeployMapError
from Log import Logger, RegistrationFailed, InvalidAddress
from call import Caller
from cliutils import show_methods, select_method, get_contract, get_abi, signWithAddress, get_methods, esc_input, hidden_esc_input
from cliutils import SConsoleMenu

TITLE = """
         ______         _______  
        |       \       |       \ 
        | $$$$$$$\      | $$$$$$$\\
        | $$__/ $$      | $$__/ $$
        | $$    $$      | $$    $$
        | $$$$$$$\      | $$$$$$$\\
        | $$__/ $$      | $$__/ $$
        | $$    $$      | $$    $$
        \ $$$$$$$/      \ $$$$$$$/
         
            --BLOCK BALANCER--
"""

ON_CHAIN = OnChain()

def login():
    """Login menu."""
    msg = ""
    try:
        while True:
            try:
                address = esc_input("Insert your address")
                Logger(address)
                signWithAddress(address)
                title = "User " + address
                login_menu = SConsoleMenu(title, "Select a function ", exit_option_text="Logout")
                deploy_item = FunctionItem("Deploy",function=deploy_menu, args=[str(address)], should_exit=False)
                get_map = FunctionItem("Get Deploy Map", function=get_map_menu, should_exit=False)
                call_item = FunctionItem("Call", function=call_menu, args=[str(address)], should_exit=False)

                # Menu Admin
                admin_menu = SConsoleMenu("Admin functions")
                sharding_alg_item = FunctionItem("Set Sharding Algorithm", function=changeShardingAlg, args=[str(address)],
                                            should_exit=False)
                shard_status_item = FunctionItem("Set Shard Status", function=setShardStatus, args=[str(address)],
                                            should_exit=False)
                admin_menu.append_item(sharding_alg_item)
                admin_menu.append_item(shard_status_item)
                admin_menu_item = SubmenuItem("Admin Submenu", submenu=admin_menu)
                admin_menu_item.set_menu(login_menu)

                # Once we're done creating them, we just add the items to the menu
                login_menu.append_item(deploy_item)
                login_menu.append_item(get_map)
                login_menu.append_item(call_item)
                login_menu.append_item(admin_menu_item)

                # Finally, we call show to show the menu and allow the user to interact
                login_menu.show()
                msg = "Login successful!"
                break
            except InvalidAddress:
                print("Invalid address")
    
    except KeyboardInterrupt:
        msg = "Login failed"
    except Exception as e:
        msg = f"{str(e)}"

    return msg

def deploy_menu(user:str):
    """Deploy menu."""
    msg = ""
    try:
        while not bool(msg):
            path = esc_input("Insert file .sol path")
            msg = ON_CHAIN.deploySC(path, user)
    except KeyboardInterrupt:
        msg = "Deployment aborted"
    except Exception as e:
        msg = f"{str(e)}"
    finally:
        return msg

def register():
    msg = ""
    try:
        while True:
            address = str(esc_input("Insert your address"))
            if Web3.isAddress(address):
                break
            print("Error: Address is not valid")
        while True:
            password = str(hidden_esc_input(f"Insert password for {address} (min 8 characters, at least 1 letter, 1 digit and 1 special)"))
            if re.match(pattern="^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", string=password):
                break
            else: 
                print("Error: Weak password")
        logger = Logger(address)
        while True:
            private_key = str(hidden_esc_input("Insert private key"))
            try:
                logger.register(private_key, password)
                msg = "Account successfully registered!"
                break
            except RegistrationFailed:
                print("Error: Wrong account")
            except Exception as e:
                 print(f"{str(e)}")
    except KeyboardInterrupt as e:
        msg = "Registration failed"
    except Exception as e:
        msg = f"{str(e)}"
    finally:
        return msg

def call(my_address):
    msg = ""
    map = ON_CHAIN.getDeployMap()
    print(ON_CHAIN.showDeployMap())
    chain_link, contract_address = get_contract(map)
    abi = get_abi()
    caller = Caller(chain_link=chain_link, contract_address=contract_address, abi=abi)
    methods = get_methods(abi)
    show_methods(methods)
    go_on = True
    while go_on:
        res = caller.method_call(select_method(methods), my_address)
        if isinstance(res, AttributeDict) and "status" in res.keys():
            if res.status == 1:
                print("Transaction has been correctly sent")
            else:
                print("Transaction has been reverted...")
                print("Tip: check your connection to the network and the account balance")
        else:
            print(res)
        flag = True
        while flag:
            confirm = input('[c]ontinue on call or [q]uit: ')
            if confirm.strip().lower() == 'c':
                go_on = True
                flag = False
            if confirm.strip().lower() == 'q':
                go_on = False
                flag = False

    return msg

def call_menu(address):
    msg = ""
    try:
        msg = call(address)
    except BadFunctionCallOutput:
        msg = "Could not transact with/call contract function"
    except KeyboardInterrupt as e:
        msg = "Method call interrupted"
    except Exception as e:
        msg = f"{str(e)}"
    finally:
        return msg

def get_map_menu():
    msg = ""
    try:
        msg = ON_CHAIN.showDeployMap()
    except DeployMapError:
        msg = "Error on getting deploy map"
    except Exception as e:
        msg = f"{str(e)}"
    finally:
        return msg

def changeShardingAlg(address):
    msg = ""
    try:
        cur_alg = ON_CHAIN.getCurrentAlg()
        print(f"Current Algorithm is {'Round Robin' if cur_alg == 0 else 'Min Deploys'}")
        while True:
            try:
                id_alg = int(esc_input("Insert sharding algorithm id (0=Round Robin,1=Min Deploys)"))
                if id_alg not in [0,1]:
                    raise ValueError
                msg = ON_CHAIN.setShardingAlgorithm(int(id_alg), address)
                break
            except ValueError:
                print("Error: Insert a valid integer")
    except KeyboardInterrupt:
        msg = "Sharding algorithm unchanged"
    except Exception as e:
        msg = f"{str(e)}"
    finally:
        return msg

def setShardStatus(address):
    msg = ''
    try:
        map = ON_CHAIN.getShardList()
        print(ON_CHAIN.showShardList(map))
        while True:
            try:
                id_shard = int(esc_input("Insert shard id"))
                if id_shard < 0 or id_shard >= len(map):
                    raise IndexError
                break
            except ValueError:
                print("Error: Insert a valid integer")
            except IndexError:
                print("Index out of range")
        
        while True:
            try:
                status = int(esc_input("Insert shard status (1=Enabled, 0=Disabled)"))
                if status not in [0,1]:
                    raise ValueError("Error: Insert a valid value")
                msg = ON_CHAIN.setShardStatus(int(id_shard), bool(status), address)
                break
            except ValueError as e:
                print(e)
    except KeyboardInterrupt as e:
        msg = "Shard status unchanged"
    #except ValueError as e:
    #    msg = f"{dict(str(e)).get('message')}"
    except Exception as e:
        msg = f"{str(e)}"
    finally:
        return msg

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    # Create the menu
    menu = SConsoleMenu(TITLE, "Progetto Software Security & Blockchain")

    # A FunctionItem runs a Python function when selected
    registrazione = FunctionItem("Register", register)
    _login = FunctionItem("Login", login)

    # Once we're done creating them, we just add the items to the menu
    menu.append_item(registrazione)
    menu.append_item(_login)

    # Finally, we call show to show the menu and allow the user to interact
    menu.show()