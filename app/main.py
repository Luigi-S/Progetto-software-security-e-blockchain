import json
import re
import getpass
from click import Abort
from web3.datastructures import AttributeDict
from onchain import OnChain
from Log import Logger
from call import Caller
from cliutils import show_methods, select_method, get_contract, signWithAdress, get_methods
from consolemenu import *
from consolemenu.items import *

title = """
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
def login():
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
        except KeyboardInterrupt as e:
            flag = False
            print("Login exited")
            return None
        except Exception as e:
            if e.args != ():
                print(e.args[0])
    try:
        signWithAdress(address)
        title = "User " + address

        loginMenu = ConsoleMenu(title, "Select a function ", exit_option_text="Logout")


        deployItem = FunctionItem("Deploy",function=deployMenu, args=[str(address)], should_exit=False)
        getMap = FunctionItem("Get Deploy Map", function=getMapMenu, should_exit=False)
        callItem = FunctionItem("Call", function=callMenu, args=[str(address)], should_exit=False)

        # Menu Admin
        adminMenu = ConsoleMenu("Admin functions")
        shardingAlgItem = FunctionItem("Set Sharding Algorithm", function=changeShardingAlg, args=[str(address)],
                                       should_exit=False)
        shardStatusItem = FunctionItem("Set Shard Status", function=setShardStatus, args=[str(address)],
                                       should_exit=False)
        adminMenu.append_item(shardingAlgItem)
        adminMenu.append_item(shardStatusItem)
        adminMenu_item = SubmenuItem("Admin Submenu", submenu=adminMenu)
        adminMenu_item.set_menu(loginMenu)

        # UNA VOLTA FATTO IL LOGIN FA SCEGLIERE
        # DEPLOY (FILE SOL)

        # Once we're done creating them, we just add the items to the menu
        loginMenu.append_item(deployItem)
        loginMenu.append_item(getMap)
        loginMenu.append_item(callItem)
        loginMenu.append_item(adminMenu_item)

    # Finally, we call show to show the menu and allow the user to interact
        loginMenu.show()
    except KeyboardInterrupt as e:
        print("Login failed")

def deployMenu(user:str):
    on_chain = OnChain()
    print("Insert path: ")
    path = input()
    on_chain.deploySC(path, user)
    input("Press enter to continue")

# funzione a buon punto, manca exception handling, e reimpostare le regex finito lo sviluppo
def register():
    # TODO dettagliare meglio le richieste su password alla fine
    #initialize()
    print("Registering an account")
    try:
        address = str(input("Insert your address (starting with 0x and 40 characters long) "))
        while re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=address) is None:
            print("Error: Address is not valid")
            address = str(input())

        password = str(getpass.getpass("Insert your password (minimum eight characters, at least one letter, one number and one special character) "))
        if re.match(pattern="",
                    string=password) is None:  # "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
            # in fase di sviluppo libertà sulla scelta della password, la regex è pronta per:
            # almeno una lettera, un numero, un carattere speciale:@$!%*#?&, almeno 8 caratteri
            print("Error: Weak password \n"
                       " Minimum eight characters, at least one letter, one number and one special character")
            password = str(getpass.getpass("Insert your password (minimum eight characters, at least one letter, one number and one special character) "))
        private_key = str(getpass.getpass("Insert your private key (starting with 0x and 64 characters long) "))
        if re.fullmatch(pattern="^0x[0-9a-fA-F]{64}", string=private_key) is None:
            print("Error: Private key is not valid")
            private_key = str(input("Private key: "))
        logger = Logger(address)
        logger.register(private_key, password)
        print("Account registered!")
    except Abort:
        print("Closing...")
        # TODO valutare su quali azioni fare rollback
        print("Hello")
    except Exception as e:
        print("Something went wrong")  # TODO distinguere le casistiche
        print(e.args)
    finally:
        input("Press enter to continue")


def call(my_address):
    try:
        map = OnChain().getDeployMap()
        OnChain().showDeployMap()
        chain_link, contract_address = get_contract(map)
    except Exception as e:
        print(e.__class__)
        print(e)
        print("Exiting...")
    flag = True
    while flag:
        abi_path = input("Path to ABI ")
        try:
            with open(abi_path) as f:
                data = f.read()
            abi = json.loads(data)
            flag = False
        except IOError:
            print("Could not access ABI file")
        except json.decoder.JSONDecodeError:
            print("File is not a JSON")
    try:
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
            confirm = input('[c]Confirm or [v]Void: ')
            if confirm.strip().lower() == 'c':
                go_on = True
            if confirm.strip().lower() == 'v':
                go_on = False
    except Exception as e:
        print(e.__class__)
        print(e)
        print("Exiting...")

def callMenu(address):
    try:
        call(address)
    except Exception as e:
        print(e.args)
        print("Error on call (general)...")
    finally:
        input("Press enter to continue")

def getMapMenu():
    on_chain = OnChain()
    on_chain.showDeployMap()
    input("Press enter to continue")

def changeShardingAlg(address):
    on_chain = OnChain()
    flag = True
    while flag:
        try:
            print("Insert sharding algorithm id: ")
            id_alg = int(input())
            flag = False
        except ValueError:
            print("Error: Insert a valid integer")
    on_chain.setShardingAlgorithm(int(id_alg), address)
    input("Press enter to continue")

def setShardStatus(address):
    on_chain = OnChain()
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
    on_chain.setShardStatus(int(id_shard), bool(status), address)
    input("Press enter to continue")

if __name__ == "__main__":
    # Create the menu
    menu = ConsoleMenu(title, "Progetto Software Security & Blockchain")

    # A FunctionItem runs a Python function when selected
    registrazione = FunctionItem("Register", register)
    login = FunctionItem("Login", login)

    # Once we're done creating them, we just add the items to the menu
    menu.append_item(registrazione)
    menu.append_item(login)

    # Finally, we call show to show the menu and allow the user to interact
    menu.show()
