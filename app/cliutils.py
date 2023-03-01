from Log import Logger


def sign():
    # funzione di login per accedere alla chiave di un account registrato per validare uan transazione
    try:
        print("Insert credentials for ETH account")
        flag = True
        while flag:
            try:
                logger = Logger(input("Address "))
                flag = False
            except Exception as e:
                print("Could not log")
                if e.args != ():
                    print(e.args[0])
        while True:
            try:
                key = logger.getKey(passwd=input("Password for " + str(logger.getAddress()) + " "))
                return logger.getAddress(), key
            except Exception as e:
<<<<<<< Updated upstream
                # fornire minor informazione possibile -> ridurre canali collaterali
                typer.echo("Wrong password")
=======
                print("Wrong password")
                print(e)
>>>>>>> Stashed changes
    except Exception as e:
        # handling da migliorare.
        print("Login failed")
        if e.args != ():
            print(e.args[0])
        exit(1)

def signWithAdress(address):
    # funzione di login per accedere alla chiave di un account registrato per validare uan transazione
    try:
        flag = True
        while flag:
            try:
                logger = Logger(address)
                flag = False
            except Exception as e:
                print("Could not log")
                if e.args != ():
                    print(e.args[0])
        while True:
            try:
                key = logger.getKey(passwd=input("Password for " + str(logger.getAddress()) + " "))
                return logger.getAddress(), key
            except Exception as e:
                print("Wrong password")
                print(e)
    except Exception as e:
        # handling da migliorare.
        print("Login failed")
        if e.args != ():
            print(e.args[0])
        exit(1)
def show_methods(abi):
    k = 0
    for c in abi:
<<<<<<< Updated upstream
        typer.echo("METHOD " + str(k) + ": " + c["name"] + " <=> TYPE: " + c["stateMutability"])
=======
        print("METHOD " + k.__str__() + ": " + c["name"] + " <=> TYPE: " + c["stateMutability"])
>>>>>>> Stashed changes
        k += 1
        message = "INPUTS: "
        for i in range(len(c["inputs"])):
            message += (c["inputs"][i]["name"] if (c["inputs"][i]["name"] != "") else "_") + " : " + c["inputs"][i][
                "type"] + " - "
        print(message)
        message = "OUTPUTS: "
        for j in range(len(c["outputs"])):
            message += c["outputs"][j]["type"] + " - "
        print(message)
        print("       -----------")


def select_method(abi):
    method_i = input("Which method do you wish to call? ")
    while not (method_i.isdigit() and (int(method_i) in range(len(abi)))):
        print("You were supposed to select by id...")
        method_i = input("Which method do you wish to call? ")
    c = abi[int(method_i)]
    print("Method" + method_i + ": " + c["name"])
    return method_i


def insert_args(inputs):
    while True:
        args = ()
        for i in range(len(inputs)):
            input_type = int if inputs[i]["type"].__contains__("int") else \
                bool if inputs[i]["type"].__contains__("bool") else \
                    str  # if inputs[i]["type"].__contains__("string")
            a = input(
                (inputs[i]["name"] if (inputs[i]["name"] != "") else "_") + " : " + inputs[i]["type"]
            )
            args += (a,)
        try:
            return args
        except TypeError as e:
            raise Exception("Error occurred: malformed input\n" + e.args[0])

def get_contract(deploy_map):

    for i in range(len(deploy_map)):
        print(str(i)+") - " + deploy_map[i].name + " - shard : " + str(deploy_map[i].shardId))
    while True:
        index = int(input("Insert a valid index for a contract"))
        try:
            return deploy_map[index].chainUrl, deploy_map[index].addr
        except ValueError:
            print("Invalid index selected")
