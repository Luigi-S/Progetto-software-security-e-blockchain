import secrets
import unittest
from contextlib import contextmanager
from io import StringIO
from unittest import mock
from unittest.mock import patch

from eth_account import Account
from web3.exceptions import BadFunctionCallOutput

from app.Log import Logger
from app.compiler import deploy
from call import Caller


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ConnectionHostTestCase('def test_invalid_address'))
    suite.addTest(ConnectionHostTestCase('def test_invalid_abi'))
    suite.addTest(ConnectionHostTestCase('def test_invalid_address'))
    suite.addTest(ConnectionHostTestCase('def test_unmatching_abi'))
    suite.addTest(ConnectionHostTestCase('def test_valid'))
    suite.addTest(ConnectionHostTestCase('def test_no_credit'))
    return suite

@contextmanager
def input(*cmds):
    """Replace input."""
    cmds = "\n".join(cmds)
    with mock.patch("sys.stdin", StringIO(f"{cmds}\n")):
        yield

valid_link = "ws://127.0.0.1:10000"
valid_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
valid_pwd = "V4l!dpwd"
v_abi = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint256", "name": "pippo", "type": "uint256"}], "name": "XXX", "type": "event"}, {"inputs": [{"internalType": "string", "name": "_nome", "type": "string"}, {"internalType": "uint256", "name": "_matricola", "type": "uint256"}], "name": "addStudente", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "destroy", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "lista_studenti", "outputs": [{"internalType": "uint256", "name": "matricola", "type": "uint256"}, {"internalType": "string", "name": "nome", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "nome_matricola", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "retrieve", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_numero", "type": "uint256"}], "name": "store", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
v_bytecode = '608060405234801561001057600080fd5b5061055e806100206000396000f3fe608060405234801561001057600080fd5b506004361061004c5760003560e01c80632aa4be1e146100515780632e64cec1146100815780636057361d1461009f5780637f1d77c0146100bb575b600080fd5b61006b60048036038101906100669190610343565b6100ec565b60405161007891906103a5565b60405180910390f35b61008961011a565b60405161009691906103a5565b60405180910390f35b6100b960048036038101906100b491906103ec565b610123565b005b6100d560048036038101906100d091906103ec565b61012d565b6040516100e3929190610498565b60405180910390f35b6002818051602081018201805184825260208301602085012081835280955050505050506000915090505481565b60008054905090565b8060008190555050565b6001818154811061013d57600080fd5b9060005260206000209060020201600091509050806000015490806001018054610166906104f7565b80601f0160208091040260200160405190810160405280929190818152602001828054610192906104f7565b80156101df5780601f106101b4576101008083540402835291602001916101df565b820191906000526020600020905b8154815290600101906020018083116101c257829003601f168201915b5050505050905082565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b6000601f19601f8301169050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b61025082610207565b810181811067ffffffffffffffff8211171561026f5761026e610218565b5b80604052505050565b60006102826101e9565b905061028e8282610247565b919050565b600067ffffffffffffffff8211156102ae576102ad610218565b5b6102b782610207565b9050602081019050919050565b82818337600083830152505050565b60006102e66102e184610293565b610278565b90508281526020810184848401111561030257610301610202565b5b61030d8482856102c4565b509392505050565b600082601f83011261032a576103296101fd565b5b813561033a8482602086016102d3565b91505092915050565b600060208284031215610359576103586101f3565b5b600082013567ffffffffffffffff811115610377576103766101f8565b5b61038384828501610315565b91505092915050565b6000819050919050565b61039f8161038c565b82525050565b60006020820190506103ba6000830184610396565b92915050565b6103c98161038c565b81146103d457600080fd5b50565b6000813590506103e6816103c0565b92915050565b600060208284031215610402576104016101f3565b5b6000610410848285016103d7565b91505092915050565b600081519050919050565b600082825260208201905092915050565b60005b83811015610453578082015181840152602081019050610438565b60008484015250505050565b600061046a82610419565b6104748185610424565b9350610484818560208601610435565b61048d81610207565b840191505092915050565b60006040820190506104ad6000830185610396565b81810360208301526104bf818461045f565b90509392505050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b6000600282049050600182168061050f57607f821691505b602082108103610522576105216104c8565b5b5091905056fea26469706673582212208f8602025791aa0b91d4749ea31dfdcce23e285ad05e88bd8e52f16e8c41080c64736f6c63430008110033'

class ConnectionHostTestCase(unittest.TestCase):
    def test_invalid_address(self):
        with self.assertRaises(Exception):
            Caller(valid_link, "invalid_address", v_abi)

    def test_invalid_abi(self):
        with self.assertRaises(KeyError):
            Caller(valid_link, valid_address, [{"invalid_abi": "non_valid"}])


class MethodCallTestCase(unittest.TestCase):
    def setUp(self) -> None:
        matching_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
        self.contract_address = deploy(v_bytecode, v_abi, valid_address, matching_key, valid_link)

    # def method_call(self, method_i, address):

    def test_invalid_address(self):
        with self.assertRaises(BadFunctionCallOutput):
            Caller(chain_link=valid_link, contract_address="NON-VALIDO", abi=v_abi).method_call(7, valid_address)

    @patch('sys.stdout', new_callable=StringIO)
    def test_unmatching_abi(self, stdout):
        unmatching_abi = [{"anonymous": False, "inputs": [{"indexed": False, "internalType": "address", "name": "newAddress", "type": "address"}], "name": "ChangedManager", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "address", "name": "user", "type": "address"}, {"indexed": False, "internalType": "string", "name": "shard", "type": "string"}, {"indexed": False, "internalType": "string", "name": "name", "type": "string"}], "name": "DeployReserved", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}], "name": "OwnershipTransferred", "type": "event"}, {"inputs": [{"internalType": "string", "name": "shard", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}], "name": "deleteFound", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "user", "type": "address"}, {"internalType": "string", "name": "shard", "type": "string"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}, {"internalType": "bool", "name": "reserved", "type": "bool"}, {"internalType": "uint32", "name": "timestamp", "type": "uint32"}], "name": "deployFound", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "user", "type": "address"}, {"internalType": "string", "name": "shard", "type": "string"}, {"internalType": "string", "name": "name", "type": "string"}], "name": "notifyDeploy", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "newAddress", "type": "address"}], "name": "setManager", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}], "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
        with input(valid_pwd):
            Caller(chain_link=valid_link, contract_address=self.contract_address, abi=unmatching_abi) \
                .method_call(7, valid_address)
        expected = "ERROR"
        self.assertTrue(expected in stdout.getvalue())

        with input(valid_pwd):
            Caller(chain_link=valid_link, contract_address=self.contract_address, abi=unmatching_abi) \
                .method_call(0, valid_address)
        expected = "The method called doesn't exist."
        self.assertTrue(expected in stdout.getvalue())

    def test_valid(self):
        value = 3
        with input(str(value), valid_pwd):
            Caller(chain_link=valid_link, contract_address=self.contract_address, abi=v_abi).method_call(7, valid_address)

        return_val = Caller(chain_link=valid_link, contract_address=self.contract_address, abi=v_abi).method_call(6, valid_address)
        self.assertEqual(return_val, value)

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_credit(self, stdout):
        priv = secrets.token_hex(32)
        private_key = "0x" + priv
        account = Account.from_key(private_key)
        address = account.address
        Logger(address).register(private_key, valid_pwd)
        with input(str(5), valid_pwd):
            Caller(chain_link=valid_link, contract_address=self.contract_address, abi=v_abi).method_call(7, address)
        expected = "The params inserted caused a revert."
        self.assertTrue(expected in stdout.getvalue())


if __name__ == '__main__':
    caller_suite = unittest.TextTestRunner()
    caller_suite.run(suite())
