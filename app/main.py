import json
import re
from pathlib import Path
import getpass

from onchain import OnChain

import typer
from click import Abort

from onchain import OnChain
from Log import Logger
<<<<<<< Updated upstream
from call import Caller
from compiler import Deployer
from cliutils import show_methods, select_method, get_contract
=======
from call import Caller2

from compiler import Deployer, Caller

from cliutils import show_methods, select_method, get_contract, sign

from consolemenu import *
from consolemenu.items import *
>>>>>>> Stashed changes

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
    user = sign()
    title = "welcome " + user[0]
    print(user[0])
    subMenu = ConsoleMenu(title, "Seleziona una funzione", exit_option_text = "Logout")

    # A FunctionItem runs a Python function when selected
    #deployItem = FunctionItem("Deploy", deploy)
    deployItem = FunctionItem("Deploy",function=deployMenu, args=[str(user[0])], should_exit=False)
    getMap = FunctionItem("Get Deploy Map", function=OnChain().getDeployMap, should_exit=False)
    # UNA VOLTA FATTO IL LOGIN FA SCEGLIERE
    # DEPLOY (FILE SOL)

    # Once we're done creating them, we just add the items to the menu
    subMenu.append_item(deployItem)
    subMenu.append_item(getMap)

    # Finally, we call show to show the menu and allow the user to interact
    subMenu.show()

def deployMenu(user:str):
    print("Insert path: ")
    path = input()
    deploy(path, user)
def initialize():
    # metodo per inizializzare l'esecuzione, e mostrare il prompt iniziale
    typer.echo(title)


# funzione a buon punto, manca exception handling, e reimpostare le regex finito lo sviluppo
#@app.command()
def register():
    # TODO dettagliare meglio le richieste su password alla fine
    initialize()
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
<<<<<<< Updated upstream
        typer.echo("Something went wrong")
        typer.echo(e.args[0])
=======
        print("Something went wrong")  # TODO distinguere le casistiche
        print(e.args)
        # typer.echo(e.with_traceback()) # - developement
>>>>>>> Stashed changes
        exit(1)

#@app.command()
def compile_deploy(bytecode: str, abi):
    _deploy(path=bytecode, abi=abi)


#@app.command()
def deploy(path: str, address: str = None):
    _deploy(address=address, path=path, abi=[])

# DA SPOSTARE IN onchain.py
def _deploy(path: str, address: str, abi):
    #initialize()
    target = Path(path)
    if not target.exists():
        print("The target directory doesn't exist.\n")
        print("Tip: if you tried to insert a file name, you have to specify the correct format.")
        raise SystemExit(1)
    elif not target.is_dir():
        if target.suffix == ".sol":
            try:
                bytecode, abi = Deployer.compile(path)  # final version with Path
                d = Deployer()
                for elem in bytecode:
                    d.deploy(addressGiven=address, bytecode=bytecode[elem], abi=abi[elem])
            except Exception:
                raise SystemExit(1)

        # DA SISTEMARE
        elif target.suffix == ".json" and abi != [] and Path(abi).suffix == ".json":
            try:
                with open(path, "r") as file:
                    bytecode = json.load(file)
                with open(abi, "r") as file2:
                    abi = json.load(file2)
                d = Deployer()
                d.deploy(addressGiven=address, bytecode=bytecode["object"], abi=abi)
            except Exception as e:
                print(e.__class__)
                raise SystemExit(1)

        else:
            print("Non valid input: impossible to find a deployable contract.")
            raise SystemExit(1)

    else:
        print("Non valid input: impossible to find a deployable contract.")
        raise SystemExit(1)

<<<<<<< Updated upstream

# DA ELIMINARE
@app.command()
def prova():
    file = ""
    with open("app/compiled_contracts/Contratto.json", "r") as f:
        file = f.read().__str__()
        file.replace("\"", "\\\"")

    try:
        call(address="0x001De561C23cd1caFcBA2F8BE97D3C350f2EEb45", abi=file, func="addStudente", param=("Gig", 69))
    except Exception as e:
        print(e.__class__)
        raise SystemExit(1)

# DA ELIMINARE
@app.command()
def prova_deploy():
    o = OnChain()
    #o.deploySC(path_file="app/contract.sol")
    #o.setShardingAlgorithm(0)
    #o.setShardStatus(0, True)
    with open("app/compiled_contracts/Contratto.json", "r") as f:
        file = f.read().__str__()
        file.replace("\"", "\\\"")
    o.getDeployMap()
    #o.deleteSC(abi=file, id_SC=1, address="0x5E0AcA7cDb7f74BCc776A18B64ed4b2c52569788", url_shard="ws://127.0.0.1:8545")
    #o.call(address="0x2166FF23b1168e13609ebDE5181f0dF63D0b3E29", abi=file, chain_link="ws://127.0.0.1:8545", func="store", param=(777))


@app.command()
=======
# DA ELIMINARE
#@app.command()
def call(address: str, abi, func: str, param):
    initialize()
    # TODO: controllare che l'address sia valido, se possibile
    caller = Caller(address, abi, "ws://127.0.0.1:8545")
    try:
        caller.call(func, *param)
    except TypeError as e:
        caller.call(func, param)
    # Si puo pensare di semplificare quest'interazione aprendo un menu con i vari metodi e facendo scegliere il
    # metodo in un secondo momento

#@app.command()
>>>>>>> Stashed changes
def help():
    initialize()
    # TODO: scrivere la guida ?


<<<<<<< Updated upstream
@app.command()
def call():
=======
####CALL
#@app.command()
def call2():
    #chain_link = typer.prompt(text="Link to the chain ")
    #contract_address = typer.prompt(text="Contract address ")
>>>>>>> Stashed changes
    try:
        chain_link, contract_address = get_contract(OnChain().getDeployMap())
    except Exception as e:
        typer.echo(e.args)
        typer.echo("Exiting...")
        exit(1)
    flag = True
    while flag:
        abi_path = typer.prompt(text="Path to ABI ")
        try:
            with open(abi_path) as f:
                data = f.read()
            abi = json.loads(data)
            flag = False
        except IOError:
            typer.echo("Could not access ABI file")
        except json.decoder.JSONDecodeError:
            typer.echo("File is not a JSON")
    try:
        caller = Caller(chain_link=chain_link, contract_address=contract_address, abi=abi)
        show_methods(abi=caller.get_abi())
        go_on = True
        while go_on:
            typer.echo(caller.method_call(select_method(abi)))
            typer.echo()
            go_on = typer.confirm("Do you want to keep working with this contract?")
    except Exception as e:
        typer.echo(e.args[0])
        typer.echo("Exiting...")
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
