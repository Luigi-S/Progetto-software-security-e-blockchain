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
#app = typer.Typer()

def login():
    flag = True
    while flag:
        try:
            print("Insert address: ")
            address = input()
            logger = Logger(address)
            flag = False
        except Exception as e:
            if e.args != ():
                print(e.args[0])
    signWithAdress(address)
    title = "welcome " + address
    print(address)
    subMenu = ConsoleMenu(title, "Seleziona una funzione", exit_option_text = "Logout")

    on_chain = OnChain()

    # A FunctionItem runs a Python function when selected
    #deployItem = FunctionItem("Deploy", deploy)
    deployItem = FunctionItem("Deploy",function=deployMenu, args=[str(address)], should_exit=False)
    getMap = FunctionItem("Get Deploy Map", function=on_chain.showDeployMap, should_exit=False)
    callItem = FunctionItem("Call", function=call, args=[str(address)], should_exit=False)
    # UNA VOLTA FATTO IL LOGIN FA SCEGLIERE
    # DEPLOY (FILE SOL)

    # Once we're done creating them, we just add the items to the menu
    subMenu.append_item(deployItem)
    subMenu.append_item(getMap)
    subMenu.append_item(callItem)

    # Finally, we call show to show the menu and allow the user to interact
    subMenu.show()

def deployMenu(user:str):
    on_chain = OnChain()
    print("Insert path: ")
    path = input()
    on_chain.deploySC(path, user)

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

        password = str(input("Insert your password (minimum eight characters, at least one letter, one number and one special character) "))
        if re.match(pattern="",
                    string=password) is None:  # "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
            # in fase di sviluppo libertà sulla scelta della password, la regex è pronta per:
            # almeno una lettera, un numero, un carattere speciale:@$!%*#?&, almeno 8 caratteri
            print("Error: Weak password \n"
                       " Minimum eight characters, at least one letter, one number and one special character")
            password = str(getpass.getpass())
        private_key = str(input("Insert your private key (starting with 0x and 64 characters long) "))
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
        # typer.echo(e.with_traceback()) # - developement
        exit(1)


def call(my_address):
    try:
        map = OnChain().getDeployMap()
        OnChain().showDeployMap(map)
        chain_link, contract_address = get_contract(map)
    except Exception as e:
        print(e.args)
        print("Exiting...")
        exit(1)
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
        print(e.args[0])
        print("Exiting...")
        exit(1)


if __name__ == "__main__":
    # Create the menu
    menu = ConsoleMenu(title, "Progetto Software Security & Blockchain")

    # A FunctionItem runs a Python function when selected
    registrazione = FunctionItem("Register", register)
    login = FunctionItem("Login", login)

    #submenu = SelectionMenu(["item1", "item2", "item3"], title="Selection Menu", subtitle="These menu items return to the previous menu")

    # Create the menu item that opens the Selection submenu
    #submenu_item = SubmenuItem("Submenu item", submenu=submenu)
    #submenu_item.set_menu(menu)
    #UNA VOLTA FATTO IL LOGIN FA SCEGLIERE
    #DEPLOY (FILE SOL)


    # Once we're done creating them, we just add the items to the menu
    menu.append_item(registrazione)
    menu.append_item(login)
    #menu.append_item(submenu_item)

    # Finally, we call show to show the menu and allow the user to interact
    menu.show()
