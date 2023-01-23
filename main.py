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
from pathlib import Path
import typer

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
        print("The target directory doesn't exist")
        raise SystemExit(1)
    elif not target.is_dir():
        if target.suffix == ".sol":
            bytecode, abi = Deployer.compile(path)  # final version with Path
        elif target.suffix == ".bytecodesopdjaoij":  # TODO: check arguments, QUAL é il FORMATO DEL BYTECODE???
            with open(path, "r") as file:
                bytecode = file.read()
            abi = abi
        else:
            print("Non valid input: impossibile trovare un contratto deployable")
            raise SystemExit(1)
        d = Deployer()
        d.deploy(bytecode=bytecode, abi=abi)
    else:
        print("Non valid input: impossibile trovare un contratto deployable")
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
