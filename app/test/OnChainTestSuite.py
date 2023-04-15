import unittest
from contextlib import contextmanager
from io import StringIO
from unittest import mock
from unittest.mock import patch

from onchain import OnChain

PORTS = 4
valid_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
matching_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"

def suite():
    suite = unittest.TestSuite()
    suite.addTest(OnChainDeployTestCase("def test_target_non_existent"))
    suite.addTest(OnChainDeployTestCase("def test_target_non_string"))
    suite.addTest(OnChainDeployTestCase("def test_target_is_dir"))
    suite.addTest(TestShardingAlgorithm("def test_alg_not_exists"))
    suite.addTest(TestShardingAlgorithm("def test_alg_out_of_bound"))
    suite.addTest(TestShardingAlgorithm("def test_valid"))
    suite.addTest(TestShardingAlgorithm("def test_set_non_existing_shard_status"))
    suite.addTest(TestShardingAlgorithm("def test_set_shard_status"))
    return suite

@contextmanager
def input(*cmds):
    """Replace input."""
    cmds = "\n".join(cmds)
    with mock.patch("sys.stdin", StringIO(f"{cmds}\n")):
        yield

class OnChainDeployTestCase(unittest.TestCase):
    valid_path = "prova.sol"

    def setUp(self) -> None:
        self.onchain = OnChain()

    @patch('sys.stdout', new_callable=StringIO)
    def test_target_non_existent(self, stdout):
        self.onchain.deploySC("non-valid-path", valid_address, matching_key)
        expected_out = "The target does not exist"
        self.assertTrue(expected_out in stdout.getvalue())

    
    @patch('sys.stdout', new_callable=StringIO)
    def test_target_non_string(self, stdout):
        self.onchain.deploySC(3, valid_address, matching_key)
        expected_out = "TypeERROR"
        self.assertTrue(expected_out in stdout.getvalue())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_target_is_dir(self, stdout):
        self.onchain.deploySC("test", valid_address, matching_key)
        expected_out = "Non valid input: impossible to find a deployable contract"
        self.assertTrue(expected_out in stdout.getvalue())

    
    @patch('sys.stdout', new_callable=StringIO)
    def test_target_not_sol(self, stdout):
        self.onchain.deploySC("call.py", valid_address, matching_key)
        expected_out = "Non valid input: impossible to find a deployable contract"
        self.assertTrue(expected_out in stdout.getvalue())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_target_not_compilable(self, stdout):
        self.onchain.deploySC("sc/sbagliato.sol", valid_address, matching_key)
        expected_out = "ERROR: the file .sol isn't syntactically correct."
        self.assertTrue(expected_out in stdout.getvalue())


class TestShardingAlgorithm(unittest.TestCase):
    def setUp(self) -> None:
        self.onchain = OnChain()

    @patch('sys.stdout', new_callable=StringIO)
    def test_alg_not_exists(self, stdout):
        non_valid_alg = 999
        self.onchain.setShardingAlgorithm(non_valid_alg, valid_address, matching_key)
        expected = "The method called hasn't been found or the type of parameters wasn't correct."
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_alg_out_of_bound(self, stdout):
        non_valid_alg = 9
        self.onchain.setShardingAlgorithm(non_valid_alg, valid_address, matching_key)
        expected = "ERROR"
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_valid(self, stdout):
        valid_alg = 0
        self.onchain.setShardingAlgorithm(valid_alg, valid_address, matching_key)
        expected_out = "Sharding algorithm changed"
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_set_non_existing_shard_status(self, stdout):
        non_valid_shard = PORTS + 1
        self.onchain.setShardStatus(non_valid_shard, True, valid_address, matching_key)
        expected_out = "ERROR"
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_set_shard_status(self, stdout):
        shard_id = 0
        status = True
        self.onchain.setShardStatus(shard_id, status, valid_address, matching_key)
        expected_out = "Shard " + shard_id.__str__() + " is now " + ("enabled" if status else "disabled")
        self.assertTrue(expected_out in stdout.getvalue())


if __name__ == '__main__':
    caller_suite = unittest.TextTestRunner()
    caller_suite.run(suite())
