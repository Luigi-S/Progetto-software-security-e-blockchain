import typer
from Log import Logger


def sign():
    # funzione di login per accedere alla chiave di un account registrato per validare uan transazione
    try:
        typer.echo("Insert credentials for ETH account")
        flag = True
        while flag:
            try:
                logger = Logger(typer.prompt("Address "))
                flag = False
            except Exception as e:
                typer.echo("Could not log")
                if e.args != ():
                    typer.echo(e.args[0])
        while True:
            try:
                key = logger.getKey(passwd=typer.prompt(hide_input=True, text=f"Password for {logger.getAddress()}"))
                return logger.getAddress(), key
            except Exception as e:
                # fornire minor informazione possibile -> ridurre canali collaterali
                typer.echo("Wrong password")
    except Exception as e:
        # handling da migliorare.
        typer.echo("Login failed")
        if e.args != ():
            typer.echo(e.args[0])
        exit(1)


def show_methods(abi):
    k = 0
    for c in abi:
        typer.echo("METHOD " + str(k) + ": " + c["name"] + " <=> TYPE: " + c["stateMutability"])
        k += 1
        message = "INPUTS: "
        for i in range(len(c["inputs"])):
            message += (c["inputs"][i]["name"] if (c["inputs"][i]["name"] != "") else "_") + " : " + c["inputs"][i][
                "type"] + " - "
        typer.echo(message)
        message = "OUTPUTS: "
        for j in range(len(c["outputs"])):
            message += c["outputs"][j]["type"] + " - "
        typer.echo(message)
        typer.echo("       -----------")


def select_method(abi):
    method_i = typer.prompt(text="Which method do you wish to call? ")
    while not (method_i.isdigit() and (int(method_i) in range(len(abi)))):
        typer.echo("You were supposed to select by id...")
        method_i = typer.prompt(text="Which method do you wish to call? ")
    c = abi[int(method_i)]
    typer.echo("Method" + method_i + ": " + c["name"])
    return method_i


def insert_args(inputs):
    while True:
        args = ()
        for i in range(len(inputs)):
            input_type = int if inputs[i]["type"].__contains__("int") else \
                bool if inputs[i]["type"].__contains__("bool") else \
                    str  # if inputs[i]["type"].__contains__("string")
            a = typer.prompt(
                text=(inputs[i]["name"] if (inputs[i]["name"] != "") else "_") + " : " + inputs[i]["type"],
                type=input_type
            )
            args += (a,)
        try:
            return args
        except TypeError as e:
            raise Exception("Error occurred: malformed input\n" + e.args[0])

def get_contract(deploy_map):

    for i in range(len(deploy_map)):
        typer.echo(str(i)+") - " + deploy_map[i].name + " - shard : " + str(deploy_map[i].shardId))
    while True:
        index = typer.prompt("Insert a valid index for a contract", type=int)
        try:
            return deploy_map[index].chainUrl, deploy_map[index].addr
        except ValueError:
            typer.echo("Invalid index selected")
