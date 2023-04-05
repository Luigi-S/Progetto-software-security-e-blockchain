from prettytable import PrettyTable
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem
import  getpass
import json

from Log import Logger, RegistrationFailed

def signWithAddress(address):
    # funzione di login per accedere alla chiave di un account registrato per validare una transazione
    logger = Logger(address)
    while True:
        try:
            password = hidden_esc_input(f"Insert password for {str(logger.getAddress())}")
            key = logger.getKey(passwd=password)
            return key
        except RegistrationFailed:
            print("Wrong password")


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
            index = int(esc_input("Insert a valid method index"))
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
            index = int(esc_input("Insert a valid index for a contract"))
            if index < 0:
                raise IndexError
            return deploy_map[index][1], deploy_map[index][2]
        except ValueError:
            print("Invalid index selected")
        except IndexError:
            print("Index out of range")

def get_abi():
    while True:
        try:
            abi_path = esc_input("Insert path to ABI")
            with open(abi_path) as f:
                data = f.read()
            return json.loads(data)
        except IOError:
            print("Could not access ABI file")
        except json.decoder.JSONDecodeError:
            print("File is not a JSON")

def esc_input(text = "Insert"):
    print(f"{text} or [q]uit:")
    x = input()
    if x == 'q':
        raise KeyboardInterrupt
    return x

def hidden_esc_input(text = "Insert"):
    x = getpass.getpass(prompt=f"{text} or [q]uit:")
    if x == 'q':
        raise KeyboardInterrupt
    return x

class SConsoleMenu(ConsoleMenu):
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
     def draw(self, *args, **kwargs):
         if isinstance(self.selected_item, FunctionItem):
            if self.selected_item.get_return():
                print(self.selected_item.get_return())
         super().draw()