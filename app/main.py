"""Various imports"""
import json
import re
import getpass
from click import Abort
from web3.datastructures import AttributeDict
from onchain import OnChain, DeployMapError
from Log import Logger, RegistationFailed, InvalidAddress
from call import Caller
from cliutils import show_methods, select_method, get_contract, signWithAdress, get_methods
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem

TITLE = """
     _______         _______  
    |       \       |       \ 
    | $$$$$$$\      | $$$$$$$\\
    | $$__/ $$      | $$__/ $$
    | $$    $$      | $$    $$
    | $$$$$$$\      | $$$$$$$\\
    | $$__/ $$      | $$__/ $$
    | $$    $$      | $$    $$
     \$$$$$$$        \$$$$$$$ 
        --BLOCK BALANCER--
"""

ON_CHAIN = OnChain()

def login():
    """Login menu."""
    flag = True
    while flag:
        try:
            print("Insert address (insert \"e\" to exit): ")
            address = input()
            if address == 'e' or address == 'E':
                flag = False
                raise KeyboardInterrupt
            Logger(address)
            flag = False
        except KeyboardInterrupt:
            flag = False
            print("Login exited")
            return None
        except InvalidAddress:
            print("Invalid address")
    try:
        signWithAdress(address)
        title = "User " + address

        login_menu = ConsoleMenu(title, "Select a function ", exit_option_text="Logout")
        deploy_item = FunctionItem("Deploy",function=deploy_menu, args=[str(address)], should_exit=False)
        get_map = FunctionItem("Get Deploy Map", function=get_map_menu, should_exit=False)
        call_item = FunctionItem("Call", function=call_menu, args=[str(address)], should_exit=False)

        # Menu Admin
        admin_menu = ConsoleMenu("Admin functions")
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
    except KeyboardInterrupt:
        print("Login failed")

def deploy_menu(user:str):
    """Deploy menu."""
    print("Insert path (file .sol): ")
    path = input()
    ON_CHAIN.deploySC(path, user)
    input("Press enter to continue")

# funzione a buon punto, manca exception handling, e reimpostare le regex finito lo sviluppo
def register():
    # TODO dettagliare meglio le richieste su password alla fine
    print("Registering an account")
    try:
        address = str(input("Insert your address (starting with 0x and 40 characters long) "))
        while re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=address) is None:
            print("Error: Address is not valid")
            address = str(input("Insert your address (starting with 0x and 40 characters long) "))

        password = str(getpass.getpass("Insert your password (minimum eight characters, at least one letter, one number and one special character) "))
        # almeno una lettera, un numero, un carattere speciale:@$!%*#?&, almeno 8 caratteri
        if re.match(pattern="^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$",
                    string=password) is None:
            print("Error: Weak password \n"
                       " Minimum eight characters, at least one letter, one number and one special character")
            password = str(getpass.getpass("Insert your password (minimum eight characters, at least one letter, one number and one special character) "))
        private_key = str(getpass.getpass("Insert your private key (starting with 0x and 64 characters long) "))
        if re.fullmatch(pattern="^0x[0-9a-fA-F]{64}", string=private_key) is None:
            print("Error: Private key is not valid")
            private_key = str(getpass.getpass("Private key: "))
        logger = Logger(address)
        logger.register(private_key, password)
        print("Account registered!")
    except Abort:
        print("Closing...")
        # TODO valutare su quali azioni fare rollback
        print("Hello")
    except RegistationFailed:
        print("Registration failed")
    finally:
        input("Press enter to continue")


def call(my_address):
    try:
        map = ON_CHAIN.getDeployMap()
        ON_CHAIN.showDeployMap()
        chain_link, contract_address = get_contract(map)
        flag = True
        while flag:
            abi_path = input("Path to ABI ")
            with open(abi_path) as f:
                data = f.read()
            abi = json.loads(data)
            flag = False
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
            print()
            flag = True
            while flag:
                confirm = input('[c]ontinue on call or [b]ack main menu: ')
                if confirm.strip().lower() == 'c':
                    go_on = True
                    flag = False
                if confirm.strip().lower() == 'b':
                    go_on = False
                    flag = False
    except IOError:
        print("Could not access ABI file")
    except json.decoder.JSONDecodeError:
        print("File is not a JSON")
    except Exception as e:
        print(e.__class__)
        print(e)

def call_menu(address):
    try:
        call(address)
    except Exception as e:
        print(e.args)
        print("Error on call (general)...")
    finally:
        input("Press enter to continue")

def get_map_menu():
    try:
        ON_CHAIN.showDeployMap()
    except DeployMapError as e:
        print("Error on getting deploy map...")
    finally:
        input("Press enter to continue")

def changeShardingAlg(address):
    flag = True
    while flag:
        try:
            print("Insert sharding algorithm id: ")
            id_alg = int(input())
            flag = False
        except ValueError:
            print("Error: Insert a valid integer")
    ON_CHAIN.setShardingAlgorithm(int(id_alg), address)
    input("Press enter to continue")

def setShardStatus(address):
    flag = True
    while flag:
        try:
            print("Insert shard id: ")
            id_shard = int(input())
            flag = False
        except ValueError:
            print("Error: Insert a valid integer")
    flag = True
    while flag:
        try:
            print("Insert shard status (0 for false, 1 for true): ")
            status = int(input())  # Fare in modo che si acquisisca solo 0 o 1
            if status != 0 and status != 1:
                raise Exception("Error: Insert a valid value")
            flag = False
        except Exception as e:
            print(e)
    ON_CHAIN.setShardStatus(int(id_shard), bool(status), address)
    input("Press enter to continue")

if __name__ == "__main__":
    # Create the menu
    menu = ConsoleMenu(TITLE, "Progetto Software Security & Blockchain")

    # A FunctionItem runs a Python function when selected
    registrazione = FunctionItem("Register", register)
    login = FunctionItem("Login", login)

    # Once we're done creating them, we just add the items to the menu
    menu.append_item(registrazione)
    menu.append_item(login)

    # Finally, we call show to show the menu and allow the user to interact
    menu.show()
