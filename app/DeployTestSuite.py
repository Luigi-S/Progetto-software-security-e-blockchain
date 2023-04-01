import unittest
from io import StringIO
import re
from unittest.mock import patch

from app.ConnectionHost import ConnectionHost
from compiler import compile, deploy

valid_link = "ws://127.0.0.1:10000"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(CompileTestCase("def test_invalid_path"))
    suite.addTest(CompileTestCase("def test_non_dotsol"))
    suite.addTest(CompileTestCase("def test_wrong_dotsol"))
    suite.addTest(DeployTestCase("def test_invalid_url"))
    suite.addTest(DeployTestCase("def test_unmatching_key"))
    suite.addTest(DeployTestCase("def test_invalid_key"))
    suite.addTest(DeployTestCase("def test_invalid_address"))
    suite.addTest(DeployTestCase("def test_invalid_abi"))
    suite.addTest(DeployTestCase("def test_invalid_bytecode"))
    suite.addTest(DeployTestCase("def test_invalid_url"))
    suite.addTest(DeployTestCase("def test_unmatching_abi"))
    suite.addTest(DeployTestCase("def test_all_valid"))
    return suite


class CompileTestCase(unittest.TestCase):
    valid_contract_path = "prova.sol"

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_path(self, stdout):
        invalid_path = "/\\invalid_path\\/"
        compile(invalid_path)
        expected = "No such file or directory:"
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_non_dotsol(self, stdout):
        non_dotsol_path = "DeployTestSuite.py"
        compile(non_dotsol_path)
        expected = "ERROR: the file .sol isn't syntactically correct."
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_wrong_dotsol(self, stdout):
        wrong_dotsol_path = "sbagliato.sol"
        compile(wrong_dotsol_path)
        expected = "ERROR: the file .sol isn't syntactically correct."
        self.assertTrue(expected in stdout.getvalue())



class DeployTestCase(unittest.TestCase):
    # def deploy(bytecode, abi, address, key, url_shard):
    v_abi = [{'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'lista_studenti', 'outputs': [{'internalType': 'uint256', 'name': 'matricola', 'type': 'uint256'}, {'internalType': 'string', 'name': 'nome', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'name': 'nome_matricola', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'retrieve', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_numero', 'type': 'uint256'}], 'name': 'store', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
    v_bytecode = '608060405234801561001057600080fd5b5061055e806100206000396000f3fe608060405234801561001057600080fd5b506004361061004c5760003560e01c80632aa4be1e146100515780632e64cec1146100815780636057361d1461009f5780637f1d77c0146100bb575b600080fd5b61006b60048036038101906100669190610343565b6100ec565b60405161007891906103a5565b60405180910390f35b61008961011a565b60405161009691906103a5565b60405180910390f35b6100b960048036038101906100b491906103ec565b610123565b005b6100d560048036038101906100d091906103ec565b61012d565b6040516100e3929190610498565b60405180910390f35b6002818051602081018201805184825260208301602085012081835280955050505050506000915090505481565b60008054905090565b8060008190555050565b6001818154811061013d57600080fd5b9060005260206000209060020201600091509050806000015490806001018054610166906104f7565b80601f0160208091040260200160405190810160405280929190818152602001828054610192906104f7565b80156101df5780601f106101b4576101008083540402835291602001916101df565b820191906000526020600020905b8154815290600101906020018083116101c257829003601f168201915b5050505050905082565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b6000601f19601f8301169050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b61025082610207565b810181811067ffffffffffffffff8211171561026f5761026e610218565b5b80604052505050565b60006102826101e9565b905061028e8282610247565b919050565b600067ffffffffffffffff8211156102ae576102ad610218565b5b6102b782610207565b9050602081019050919050565b82818337600083830152505050565b60006102e66102e184610293565b610278565b90508281526020810184848401111561030257610301610202565b5b61030d8482856102c4565b509392505050565b600082601f83011261032a576103296101fd565b5b813561033a8482602086016102d3565b91505092915050565b600060208284031215610359576103586101f3565b5b600082013567ffffffffffffffff811115610377576103766101f8565b5b61038384828501610315565b91505092915050565b6000819050919050565b61039f8161038c565b82525050565b60006020820190506103ba6000830184610396565b92915050565b6103c98161038c565b81146103d457600080fd5b50565b6000813590506103e6816103c0565b92915050565b600060208284031215610402576104016101f3565b5b6000610410848285016103d7565b91505092915050565b600081519050919050565b600082825260208201905092915050565b60005b83811015610453578082015181840152602081019050610438565b60008484015250505050565b600061046a82610419565b6104748185610424565b9350610484818560208601610435565b61048d81610207565b840191505092915050565b60006040820190506104ad6000830185610396565b81810360208301526104bf818461045f565b90509392505050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b6000600282049050600182168061050f57607f821691505b602082108103610522576105216104c8565b5b5091905056fea26469706673582212208f8602025791aa0b91d4749ea31dfdcce23e285ad05e88bd8e52f16e8c41080c64736f6c63430008110033'
    v_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
    matching_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
    unmatching_key = "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1"

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_url(self, stdout):
        deploy(self.v_bytecode, self.v_abi, self.v_address, self.matching_key, "INVALID-URL")
        expected = "ERROR: system error occurred."
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_unmatching_key(self, stdout):
        deploy(self.v_bytecode, self.v_abi, self.v_address, self.unmatching_key, valid_link)
        expected = "from field must match key"
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_key(self, stdout):
        deploy(self.v_bytecode, self.v_abi, self.v_address, "INVALID_KEY", valid_link)
        expected = "ERROR: the file doesn't contains a valid bytecode or abi."
        self.assertTrue(expected in stdout.getvalue())


    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_address(self, stdout):
        deploy(self.v_bytecode, self.v_abi, "UNVALID-ADDRESS", "---", valid_link)
        expected = "ERROR: system error occurred."
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_abi(self, stdout):
        deploy(self.v_bytecode, {}, self.v_address, self.matching_key, valid_link)
        expected = "Could not format value {} as field 'abi'"
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_bytecode(self, stdout):
        deploy('', self.v_abi, self.v_address, self.matching_key, valid_link)
        expected = "Unsupported type"
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_unmatching_abi(self, stdout):
        another_valid_bytecode = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint8", "name": "newAlg", "type": "uint8"}], "name": "ChangedAlgorithm", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "address", "name": "newAddress", "type": "address"}], "name": "ChangedOracle", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"}, {"components": [{"internalType": "uint8", "name": "shardId", "type": "uint8"}, {"internalType": "string", "name": "shardUrl", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint32", "name": "deployTime", "type": "uint32"}, {"internalType": "bool", "name": "reserved", "type": "bool"}], "indexed": False, "internalType": "struct AbstractManager.Contract", "name": "c", "type": "tuple"}], "name": "DeployDeleted", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"}, {"components": [{"internalType": "uint8", "name": "shardId", "type": "uint8"}, {"internalType": "string", "name": "shardUrl", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint32", "name": "deployTime", "type": "uint32"}, {"internalType": "bool", "name": "reserved", "type": "bool"}], "indexed": False, "internalType": "struct AbstractManager.Contract", "name": "c", "type": "tuple"}], "name": "DeploySaved", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "url", "type": "string"}], "name": "DeployUrl", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}], "name": "OwnershipTransferred", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint8", "name": "shardId", "type": "uint8"}, {"indexed": False, "internalType": "string", "name": "shard", "type": "string"}], "name": "ShardAdded", "type": "event"}, {"inputs": [{"internalType": "string", "name": "url", "type": "string"}, {"internalType": "bool", "name": "active", "type": "bool"}], "name": "addShard", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "deployMap", "outputs": [{"internalType": "uint8", "name": "shardId", "type": "uint8"}, {"internalType": "string", "name": "shardUrl", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint32", "name": "deployTime", "type": "uint32"}, {"internalType": "bool", "name": "reserved", "type": "bool"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "shardUrl", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}], "name": "fullfillDelete", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "user", "type": "address"}, {"internalType": "string", "name": "shardUrl", "type": "string"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}, {"internalType": "bool", "name": "reserved", "type": "bool"}, {"internalType": "uint32", "name": "timestamp", "type": "uint32"}], "name": "fullfillDeploy", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "getDeployMap", "outputs": [{"components": [{"internalType": "uint8", "name": "shardId", "type": "uint8"}, {"internalType": "string", "name": "shardUrl", "type": "string"}, {"internalType": "bytes20", "name": "addr", "type": "bytes20"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint32", "name": "deployTime", "type": "uint32"}, {"internalType": "bool", "name": "reserved", "type": "bool"}], "internalType": "struct AbstractManager.Contract[]", "name": "", "type": "tuple[]"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "string", "name": "name", "type": "string"}], "name": "reserveDeploy", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint8", "name": "newAlg", "type": "uint8"}], "name": "setAlg", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "newAddress", "type": "address"}], "name": "setOracle", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint8", "name": "shardId", "type": "uint8"}, {"internalType": "bool", "name": "status", "type": "bool"}], "name": "setShardStatus", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "shardList", "outputs": [{"internalType": "string", "name": "url", "type": "string"}, {"internalType": "bool", "name": "active", "type": "bool"}, {"internalType": "uint256", "name": "numDeploy", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}], "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
        deploy(another_valid_bytecode, self.v_abi, self.v_address, self.matching_key, valid_link)
        expected = "Could not format value "
        self.assertTrue(expected in stdout.getvalue())

    def test_all_valid(self):
        contract_address = deploy(self.v_bytecode, self.v_abi, self.v_address, self.matching_key, valid_link)
        self.assertTrue(re.fullmatch(pattern="^0x[0-9a-fA-F]{40}", string=contract_address) is not None)

        w3 = ConnectionHost(valid_link).connect()
        numero = 4
        contract = w3.eth.contract(address=contract_address, abi=self.v_abi)
        func = contract.functions.store
        greeting_transaction = func(numero).buildTransaction(
            {
                "chainId": w3.eth.chain_id,
                "gasPrice": w3.eth.gas_price,
                "from": self.v_address,
                "nonce": w3.eth.getTransactionCount(self.v_address),
            }
        )
        signed_greeting_txn = w3.eth.account.sign_transaction(
            greeting_transaction, private_key=self.matching_key
        )
        tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
        self.assertEqual(contract.functions.retrieve().call(), numero)


if __name__ == '__main__':
    caller_suite = unittest.TextTestRunner()
    caller_suite.run(suite())
