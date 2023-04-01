import http
import os
import unittest

from dotenv import dotenv_values

from app.Log import Logger, InvalidAddress, RegistrationFailed

valid_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
unmatching_key = "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1"
matching_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
valid_pwd = "V4l!dpwd"

PWD_DOTENV = "../pwd.env"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ConstructorLogger('def test_invalid'))
    suite.addTest(ConstructorLogger('def test_valid_non_exists'))
    suite.addTest(ConstructorLogger('def test_valid_exists'))
    suite.addTest(RegisterTestCase('def test_valid_input'))
    suite.addTest(RegisterTestCase('def test_invalid_key'))
    suite.addTest(RegisterTestCase('def test_unmatching_key'))
    suite.addTest(RegisterTestCase('def test_unsecure_pwd'))
    suite.addTest(SignTestCase('def test_wrong_pwd'))
    suite.addTest(SignTestCase('def test_ok'))
    return suite


class ConstructorLogger(unittest.TestCase):
    def test_invalid(self):
        with self.assertRaises(InvalidAddress):
            Logger("invalid_address")

    def test_valid_non_exists(self):
        logger = Logger(valid_address)
        self.assertEqual(valid_address, logger.getAddress())
        self.assertEqual(dotenv_values(PWD_DOTENV, verbose=False), logger._map)

    def test_valid_exists(self):
        logger = Logger(valid_address)
        self.assertEqual(valid_address, logger.getAddress())
        self.assertEqual(dotenv_values(PWD_DOTENV, verbose=False), logger._map)


class RegisterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = Logger(valid_address)

    def test_valid_input(self):
        self.logger.register(matching_key, valid_pwd)
        self.assertTrue(
            self.logger.getAddress() in dotenv_values(os.path.realpath(os.path.dirname(__file__)) + "/../pwd.env", verbose=False).keys()
        )

    def test_invalid_key(self):
        with self.assertRaises(RegistrationFailed):
            self.logger.register("invalid_k", valid_pwd)

    def test_unmatching_key(self):
        with self.assertRaises(RegistrationFailed):
            self.logger.register(unmatching_key, valid_pwd)



class SignTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = Logger(valid_address)

    def test_wrong_pwd(self):
        err_msg = ""
        try:
            self.logger.getKey("nongiusta")
        except RegistrationFailed as e:
            err_msg = e.args[0]
        self.assertEqual(err_msg, "Password does not match")


    def test_ok(self):
        key = self.logger.getKey(valid_pwd)
        self.assertEqual(key, matching_key)




if __name__ == '__main__':
    logger_suite = unittest.TextTestRunner()
    logger_suite.run(suite())
