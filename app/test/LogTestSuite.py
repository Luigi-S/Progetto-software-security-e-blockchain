import os
import unittest

from dotenv import dotenv_values

from Log import Logger, InvalidAddress, RegistrationFailed

valid_address = "0x02eeD43C52B532F284f95dd7E08AB2B47f4937Cd"
unmatching_key = "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1"
matching_key = "0xca8fafd5be4de8ec2d342336eaa90199f42f772b1d520adef87fc5f2859abbc0"
valid_pwd = "V4l!dpwd"

PWD_DOTENV = "../pwd.env"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ConstructorLogger('def test_invalid'))
    suite.addTest(ConstructorLogger('def test_valid'))
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

    
    def test_valid(self):
        logger = Logger(valid_address)
        self.assertEqual(valid_address, logger.getAddress())

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
