
import binascii
import json
import re
from pathlib import Path

import solcx
import typer

from Log import Logger
from solcx.exceptions import SolcError

from compiler import Deployer, Caller

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
        password = typer.Option(default=None, prompt=True, confirmation_prompt=True, hide_input=True)
        if re.match(pattern="",
                    string=password) is None:  # "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
            # in fase di sviluppo libertà sulla scelta della password, la regex è pronta per:
            # almeno una lettera, un numero, un carattere speciale:@$!%*#?&, almeno 8 caratteri
            typer.echo("Error: Weak password \n"
                       " Minimum eight characters, at least one letter, one number and one special character")
            password = typer.Option(default=None, prompt=True, confirmation_prompt=True, hide_input=True)
        private_key: str = typer.Option(default=None, prompt=True, confirmation_prompt=True, hide_input=True)
        if re.fullmatch(pattern="^0x[0-9a-fA-F]{64}", string=private_key) is None:
            typer.echo("Error: Private key is not valid")
            private_key: str = typer.Option(default=None, prompt=True, confirmation_prompt=True, hide_input=True)
        logger = Logger(address)
        logger.register(private_key, password)
    except Exception as e:
        typer.echo("Something went wrong")  # TODO distinguere le casistiche
        exit(1)


def sign():
    # funzione di login per accedere alla chiave di un account registrato per validare uan transazione
    k = None
    try:
        typer.echo("Insert credentials for ETH account")
        logger = Logger(typer.prompt("Address "))
        k = logger.getKey(passwd=typer.prompt(hide_input=True, text=f"Password for {logger.getAddress()}"))
    except Exception:
        # TODO handling
        typer.echo("Login failed")
    return k


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
                d.deploy(bytecode=bytecode, abi=abi)
            except Exception:
                raise SystemExit(1)
        elif target.suffix == ".json" and abi == []:  #Il bytecode è scritto in json
            try:
                with open(path, "r") as file:
                    data = json.load(file)

                bytecode = {}
                abi = {}

                items = data["contracts"].keys()
                for item in items:
                    contracts = data["contracts"][item].keys()
                    for contract in contracts:
                        bytecode[contract] = data["contracts"][item][contract]["evm"]["bytecode"]["object"]
                        abi[contract] = data["contracts"][item][contract]["abi"]
                d = Deployer()
                d.deploy(bytecode=bytecode[contract], abi=abi[contract])
            except Exception:
                raise SystemExit(1)

        elif target.suffix == ".json" and abi != [] and Path(abi).suffix == ".json":
            try:
                with open(path, "r") as file:
                    bytecode = json.load(file)
                with open(abi, "r") as file2:
                    abi = json.load(file2)
                d = Deployer()
                d.deploy(bytecode=bytecode, abi=abi)
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
    caller.call(func, param)
    # Si puo pensare di semplificare quest'interazione aprendo un menu con i vari metodi e facendo scegliere il
    # metodo in un secondo momento


@app.command()
def help():
    initialize()
    # TODO: scrivere la guida ?


if __name__ == "__main__":
    app()
