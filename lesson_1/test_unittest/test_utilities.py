"""unittest utilities"""

import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.getcwd(), '..'))
from shared.variables import RESPONSE, ERROR, USER,\
    ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from shared.utilities import get_message, send_message


class TestSocket:
    """
    testing class for send and receiving
    requesting dictionary, which will be
     used in testing function
    """
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        """Testing send function, correctly encodes the message,
         also saves what should have been sent to the targeting
          socket - what we send to the socket"""

        test_message_json = json.dumps(self.test_dict)
        self.encoded_message = test_message_json.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        test_message_json = json.dumps(self.test_dict)
        return test_message_json.encode(ENCODING)


class Tests(unittest.TestCase):
    """main class which completes testing"""
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    succesfull_dict = {RESPONSE: 200}
    error_dict = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message(self):
        """
        testing correct work of delivery fucntion
        creating test socket and checking correct of
        dictionary sends
        """
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message,
                         test_socket.received_message)
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    def test_get_message(self):
        """
        test of receiving options
        """
        test_sock_ok = TestSocket(self.succesfull_dict)
        test_sock_err = TestSocket(self.error_dict)
        self.assertEqual(get_message(test_sock_ok),
                         self.succesfull_dict)
        self.assertEqual(get_message(test_sock_err),
                         self.error_dict)


if __name__ == '__main__':
    unittest.main()
