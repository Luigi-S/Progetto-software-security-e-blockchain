from Log import Logger
from prettytable import PrettyTable
import  getpass

def sign():
    # funzione di login per accedere alla chiave di un account registrato per validare una transazione
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
                key = logger.getKey(passwd=getpass.getpass(prompt="Password for " + str(logger.getAddress()) + " "))
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


def signWithAdress(address):
    # funzione di login per accedere alla chiave di un account registrato per validare una transazione
    try:
        while True:
            try:
                logger = Logger(address)
                password = getpass.getpass(prompt="Password for " + str(logger.getAddress()) + "(insert \"e\" to exit): ")
                if password == "e" or password == "E":
                    raise KeyboardInterrupt
                key = logger.getKey(passwd=password)
                return key
            except Exception as e:
                print("Wrong password")
    except Exception as e:
        # handling da migliorare.
        print("Login failed")
        if e.args != ():
            print(e.args[0])
        exit(1)


def show_methods(methods):
    pt = PrettyTable()
    pt.field_names = ["Id", "Method Sign", "Output", "Type"]
    for m in methods:
        pt.add_row(m[:-1])
    print(pt)

def get_methods(abi):
    count = 0
    true_count = 0    
    x_list = []
    for c in abi:
        if c.get("type") == "function":
            type = c["stateMutability"]
            method_sign = c["name"] + "( "
            for i in range(len(c["inputs"])):
                method_sign += (c["inputs"][i]["name"] if (c["inputs"][i]["name"] != "") else "_") + " : " + c["inputs"][i][
                    "type"] + ", "
            method_sign += ")"
            method_sign = method_sign.replace(", )",  ")")
            output = ""
            for j in range(len(c["outputs"])):
                output += c["outputs"][j]["type"] + ", "
            output += " "
            output = output.replace(",  ", "")
            x_list.append([count, method_sign, output, type, true_count])
            count += 1
        true_count += 1
    
    return x_list

def select_method(methods):
    while True:
        try:
            index = int(input("Which method do you wish to call? "))
            if index < 0:
                raise IndexError
            return methods[index][-1]
        except ValueError:
            print("Invalid index selected")
        except IndexError as e:
            print("Index out of range")
        except Exception as e:
            print(e.__class__)
            print(e)

def insert_args(inputs):
    while True:
        args = ()
        for i in range(len(inputs)):
            flag = True
            input_type = int if inputs[i]["type"].__contains__("int") else \
                bool if inputs[i]["type"].__contains__("bool") else str
            while flag:
                try:
                    a = input(
                        (inputs[i]["name"] if (inputs[i]["name"] != "") else "_") + " : " + inputs[i]["type"] + " "
                    )
                    a = input_type(a)
                    flag = False
                except ValueError:
                    print("Invalid argument type")
                except Exception as e:
                    print(e.__class__)
                    print(e)
            args += (a,)
        try:
            return args
        except TypeError as e:
            raise Exception("Error occurred: malformed input\n" + e.args[0])


def get_contract(deploy_map):
    while True:
        try:
            index = int(input("Insert a valid index for a contract: "))
            if index < 0:
                raise IndexError
            return deploy_map[index][1], deploy_map[index][2]
        except ValueError:
            print("Invalid index selected")
        except IndexError as e:
            print("Index out of range")
        except Exception as e:
            print(e.__class__)
            print(e)

