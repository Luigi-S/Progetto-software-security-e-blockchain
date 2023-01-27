# MAPPING INPUTs
"""
-l --log
-d --deploy
-c --call
...?
-m --map
"""

# TYPER

import argparse
import binascii
import json
import os
from pathlib import Path

import solcx
import typer
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

"""
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--log", action="store_true")
parser.add_argument("-d", "--deploy", action="store_true")
parser.add_argument("-c", "--call", action="store_true")
parser.add_argument("path", nargs='?', default=False)
parser.add_argument("bytecode", nargs='?', default=False)
parser.add_argument("abi", nargs='?', default=False)
parser.add_argument("address", nargs='?', default=False)
parser.add_argument("func", nargs='?', default=False)
parser.add_argument("param", nargs='?', default=False)
args = parser.parse_args()
"""
@app.command()
def log():
    print(title)
    # bisogna farsi passare address e chiave privata, eviterei di utilizzare parametri direttamente
    pass

@app.command()
def compile_deploy(bytecode: str, abi):
    _deploy(path=bytecode, abi=abi)

@app.command()
def deploy(path: str):
    _deploy(path=path, abi=[])


def _deploy(path: str, abi):
    print(title)
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
            except solcx.exceptions.SolcError as e:
                print("ERROR: the file .sol isn't syntactically correct.")
            except binascii.Error as e1:
                print("ERROR: the file doesn't contains a valid bytecode.")
                print(e1)
            except UnboundLocalError as e2:  # se la compilazione del bytecode non va a buon fine, "bytecode" non è inizializzata
                print("")
            except TypeError as e3:
                print(e3)
            except Exception as e4:
                print("ERROR: system error occurred.")

        elif target.suffix == ".json":  #Il bytecode è scritto in json
            with open(path, "r") as file:
                #bytecode = file.read()
                data = json.load(file)
                #bytecode = data["contracts"]["prova.sol"]["Prova"]["evm"]["bytecode"]
                #abi = data["contracts"]["prova.sol"]["Prova"]["abi"]

            #contract_name = os.path.basename(path)
            bytecode = {}
            abi = {}
            try:
                items = data["contracts"].keys()
                for item in items:
                    contracts = data["contracts"][item].keys()
                    for contract in contracts:
                        bytecode[contract] = data["contracts"][item][contract]["evm"]["bytecode"]["object"]
                        abi[contract] = data["contracts"][item][contract]["abi"]
                d = Deployer()
                d.deploy(bytecode=bytecode[contract], abi=abi[contract])
            except binascii.Error as e:
                print("ERROR: the file doesn't contains a valid bytecode.")
                #print(e)
            except KeyError as e2:
                print("ERROR: the file doesn't contains a valid bytecode.")
            except UnboundLocalError:  # se la compilazione del bytecode non va a buon fine, "bytecode" non è inizializzata
                print("")
            except TypeError as e3:
                print(e3)
            except Exception as e4:
                print("ERROR: system error occurred.")
                #print(e4)

        else:
            print("Non valid input: impossible to find a deployable contract.")
            raise SystemExit(1)

    else:
        print("Non valid input: impossible to find a deployable contract.")
        raise SystemExit(1)

@app.command()
def call(address: str, abi, func: str, param):
    print(title)
    # TODO: controllare che l'address sia valido, se possibile
    caller = Caller(address, abi)
    caller.call(func, param)
    # Si puo pensare di semplificare quest'interazione aprendo un menu con i vari metodi e facendo scegliere il
    # metodo in un secondo momento

@app.command()
def help():
    print(title)
    print("""B-B complete guide:
    1) Use your keyboard""")  # TODO: scrivere la guida

if __name__ == "__main__":
    app()
