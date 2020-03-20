"""unittest of functions in client_side.py"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from shared.variables import RESPONSE, ERROR, USER, \
    ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client_side import launch_presence, server_response


class TestClass(unittest.TestCase):
    """ test class"""

    def test_of_presense(self):
        """test if presence ability"""
        test = launch_presence()
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1,
                                USER: {ACCOUNT_NAME: 'Anonymous'}})

    def test_200(self):
        """Testing correct parsing with 200 code"""
        self.assertEqual(server_response({RESPONSE: 200}),
                         '200 : OK')

    def test_400(self):
        """Testing correct parsing with 400 code"""
        self.assertEqual(server_response({RESPONSE: 400,
                                          ERROR: 'Bad Request'}),
                         '400 : Bad Request')

    def test_absence_of_response(self):
        """Testing exclude without RESPONSE field"""
        self.assertRaises(ValueError, server_response,
                          {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
