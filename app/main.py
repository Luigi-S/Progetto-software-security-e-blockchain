import json
import os
import re
from pathlib import Path

import typer
from click import Abort
from web3 import Web3

import onchain

from Log import Logger
from call import Caller2

from compiler import Deployer, Caller

from cliutils import show_methods, select_method, insert_args

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
app = typer.Typer()


def initialize():
    # metodo per inizializzare l'esecuzione, e mostrare il prompt iniziale
    typer.echo(title)


# funzione a buon punto, manca exception handling, e reimpostare le regex finito lo sviluppo
@app.command()
def register():
    # TODO dettagliare meglio le richieste su password, eventualmente anche per address,
    #  che sono eseguite anche da eth_account
    initialize()
    typer.echo("Registering an account")
    try:
        address = typer.prompt(text="Address ")
        while re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=address) is None:
            typer.echo("Error: Address is not valid")
            address = typer.prompt(text="Address ")
        password = typer.prompt(confirmation_prompt=True, hide_input=True, text="Password ")
        if re.match(pattern="",
                    string=password) is None:  # "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
            # in fase di sviluppo libertà sulla scelta della password, la regex è pronta per:
            # almeno una lettera, un numero, un carattere speciale:@$!%*#?&, almeno 8 caratteri
            typer.echo("Error: Weak password \n"
                       " Minimum eight characters, at least one letter, one number and one special character")
            password = typer.prompt(confirmation_prompt=True, hide_input=True, text="Password ")
        private_key = typer.prompt(confirmation_prompt=True, hide_input=True, text="Private Key ")
        if re.fullmatch(pattern="^0x[0-9a-fA-F]{64}", string=private_key) is None:
            typer.echo("Error: Private key is not valid")
            private_key = typer.prompt(confirmation_prompt=True, hide_input=True, text="Private Key ")
        logger = Logger(address)
        logger.register(private_key, password)
    except Abort:
        typer.echo("Closing...")
        # TODO valutare su quali azioni fare rollback
        typer.echo("Hello")
    except Exception as e:
        typer.echo("Something went wrong")  # TODO distinguere le casistiche
        typer.echo(e.args)
        # typer.echo(e.with_traceback()) # - developement
        exit(1)


@app.command()
def initial_deploy():
    initialize()
    path = "app/contracts/on_chain_manager/onChain.sol"
    target = Path(path)
    if not target.exists():
        print("Cannot find the on chain manager file.sol")
        raise SystemExit(1)
    elif not target.is_dir():
        try:
            bytecode, abi = Deployer.compile(path)  # final version with Path
            d = Deployer()
            d.deploy(bytecode=bytecode["Manager"], abi=abi["Manager"])
            d.deploy(bytecode=bytecode["Oracle"], abi=abi["Oracle"])

            file = ""
            with open("app/compiled_contracts/Manager.json", "r") as f:
                file = f.read().__str__()
                file.replace("\"", "\\\"")

            file2 = ""
            with open("app/compiled_contracts/Oracle.json", "r") as f:
                file2 = f.read().__str__()
                file2.replace("\"", "\\\"")

            call(address="0x3Ad438090D6CA3c26f2e4C4c2E7833066B87e709",
                 abi=file, func="addShard", param=("ws://127.0.0.1:8545", True))

            #oracle_address = bytes.fromhex("3Ec9745c7Bc93024e4EA3BaC26B89172D92C4c26")
            oracle_address = tuple(["0x3Ec9745c7Bc93024e4EA3BaC26B89172D92C4c26"])
            call(address="0x3Ad438090D6CA3c26f2e4C4c2E7833066B87e709",
                 abi=file, func="setOracle", param=oracle_address)

            manager_address = tuple(["0x3Ad438090D6CA3c26f2e4C4c2E7833066B87e709"])
            call(address="0x3Ec9745c7Bc93024e4EA3BaC26B89172D92C4c26",
                 abi=file2, func="setManager", param=manager_address)
        except Exception as e:
            print(e)
            raise SystemExit(1)


@app.command()
def compile_deploy(bytecode: str, abi):
    _deploy(path=bytecode, abi=abi)


@app.command()
def deploy(path: str):
    _deploy(path=path, abi=[])


def _deploy(path: str, abi):
    initialize()
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
                    d.deploy(bytecode=bytecode[elem], abi=abi[elem])
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
                d.deploy(bytecode=bytecode["object"], abi=abi)
            except Exception as e:
                print(e.__class__)
                raise SystemExit(1)

        else:
            print("Non valid input: impossible to find a deployable contract.")
            raise SystemExit(1)

    else:
        print("Non valid input: impossible to find a deployable contract.")
        raise SystemExit(1)


@app.command()
def call(address: str, abi, func: str, param):
    initialize()
    # TODO: controllare che l'address sia valido, se possibile
    caller = Caller(address, abi)
    try:
        caller.call(func, *param)
    except TypeError as e:
        caller.call(func, param)
    # Si puo pensare di semplificare quest'interazione aprendo un menu con i vari metodi e facendo scegliere il
    # metodo in un secondo momento


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

@app.command()
def prova_deploy():
    onchain.deploy()


@app.command()
def help():
    initialize()
    # TODO: scrivere la guida ?


####CALL
@app.command()
def call2():
    chain_link = typer.prompt(text="Link to the chain ")
    contract_address = typer.prompt(text="Contract address ")
    while re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=contract_address) is None:
        typer.echo("Error: Address is not valid")
        contract_address = typer.prompt(text="Contract address ")
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
        caller = Caller2(chain_link, contract_address, abi)
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
    app()
