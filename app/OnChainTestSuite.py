import unittest
from contextlib import contextmanager
from io import StringIO
from unittest import mock
from unittest.mock import patch

from onchain import OnChain

PORTS = 4
valid_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
valid_pwd = "V4l!dpwd"

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
        with input(valid_pwd):
            self.onchain.deploySC("non-valid-path", valid_address)

        expected_out = "The target directory doesn't exist.\n"
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_target_non_string(self, stdout):
        with input(valid_pwd):
            self.onchain.deploySC(3, valid_address)

        expected_out = "The used account has a private key that doesn't correspond to the public key"
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_target_is_dir(self, stdout):
        with input(valid_pwd):
            self.onchain.deploySC("../app", valid_address)

        expected_out = "Non valid input: impossible to find a deployable contract."
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_target_not_sol(self, stdout):
        with input(valid_pwd):
            self.onchain.deploySC("OnChainTestSuite.py", valid_address)

        expected_out = "Non valid input: impossible to find a deployable contract."
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_target_not_compilable(self, stdout):
        with input(valid_pwd):
            self.onchain.deploySC("sbagliato.sol", valid_address)

        expected_out = "ERROR: the file .sol isn't syntactically correct."
        self.assertTrue(expected_out in stdout.getvalue())


class TestShardingAlgorithm(unittest.TestCase):
    def setUp(self) -> None:
        self.onchain = OnChain()

    @patch('sys.stdout', new_callable=StringIO)
    def test_alg_not_exists(self, stdout):
        non_valid_alg = 999
        with input(valid_pwd):
            self.onchain.setShardingAlgorithm(non_valid_alg, valid_address)
        expected = "The method called hasn't been found or the type of parameters wasn't correct."
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_alg_out_of_bound(self, stdout):
        non_valid_alg = 9
        with input(valid_pwd):
            self.onchain.setShardingAlgorithm(non_valid_alg, valid_address)
        expected = "ERROR"
        self.assertTrue(expected in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_valid(self, stdout):
        valid_alg = 0
        with input(valid_pwd):
            self.onchain.setShardingAlgorithm(valid_alg, valid_address)
        expected_out = "Sharding algorithm changed to:"
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_set_non_existing_shard_status(self, stdout):
        non_valid_shard = PORTS + 1
        with input(valid_pwd):
            self.onchain.setShardStatus(shard_id=non_valid_shard, status=True, my_address=valid_address)
        expected_out = "ERROR"
        self.assertTrue(expected_out in stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_set_shard_status(self, stdout):
        shard_id = 0
        status = True
        with input(valid_pwd):
            self.onchain.setShardStatus(shard_id=shard_id, status=status, my_address=valid_address)
        expected_out = "Shard n. " + shard_id.__str__() + " has now the status \"" + status.__str__() + "\""
        self.assertTrue(expected_out in stdout.getvalue())


if __name__ == '__main__':
    caller_suite = unittest.TextTestRunner()
    caller_suite.run(suite())
