from prettytable import PrettyTable
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem
import  getpass
import json
import re
from functools import reduce
from ast import literal_eval

from Log import Logger, RegistrationFailed

type_dict = {
    "bool" : bool,
    "int" : int,
    "uint" :  int,
    "fixed" : float,
    "ufixed" : float,
    "fixedx" : float,
    "ufixedx" : float,
    "address" : str,
    "address payable" : str,
    "bytes" : str,
    "string" : str,
}



def validate_multi_array(array, py_type, dims):
    if not isinstance(array, list):
        raise ValueError()
    if dims[0] and len(array) != dims[0]:
        raise ValueError()
    flat_list = array.copy()
    i = 1
    try:
        while isinstance(flat_list[0], list):
            comp_dim = dims[i] if dims[i] else len(flat_list[0])
            flat_list = reduce(lambda acc, item: acc + [i for i in item] if len(item) == comp_dim else None, flat_list, [])
            i+=1
    except:
        raise ValueError()
    if i != len(dims):
        raise ValueError()
    if not all([type(item) == py_type for item in flat_list]):
        raise TypeError()



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
            print(e)

def insert_args(inputs):
    while True:
        args = ()
        for i in range(len(inputs)):
            flag = True
            str_dims = re.findall(r"\[[0-9]*\]", str(inputs[i]["type"]))
            dims = list (map(lambda item : int(item[1:-1]) if item[1:-1] else 0, str_dims))
            sol_type = re.sub(r"[0-9]|\[[0-9]*\]","", str(inputs[i]["type"]))
            py_type = type_dict.get(sol_type)
            if not py_type:
                py_type = str
            while flag:
                try:
                    a = input( f"{inputs[i]['name'] if inputs[i]['name'] else '_'} : {py_type.__name__}{''.join(str_dims)} ")
                    if len(dims) > 0:
                        a = literal_eval(a)
                        validate_multi_array(a, py_type, dims)
                    else:
                        a = py_type(a)
                    flag = False
                except ValueError:
                    print("Invalid argument value")
                except TypeError as e:
                    print("Invalid argument type")
                except Exception as e:
                    print("Error encountered during type checking")
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