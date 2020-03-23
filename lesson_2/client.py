"""client server communication, client side code review"""
import sys
import json
import socket
import time
import dis
import argparse
import logging
import threading
import logs.config_client_log
from shared.variables import *
from shared.utils import *
from shared.errors import *
from shared.decos import log
from shared.metaclasses import ClientBuilder

LOGGER = logging.getLogger('client')


# Class of handling and sending messages on server and user
class ClientOut(threading.Thread, metaclass=ClientBuilder):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # function creates dictionary with message to leave
    def produce_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    # function requests message text and returns it,
    # also it may leave program, by necessity
    def produce_message(self):
        to = input('Send message to user: ')
        message = input('Enter text message: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'message dict is formed: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            LOGGER.info(f'message to user {to} sent')
        except:
            LOGGER.critical('connection lost')
            exit(1)

    # function coop with user, requests commands, sends msgs
    def run(self):
        self.print_help()
        while True:
            command = input('Enter command: ')
            if command == 'm':
                self.produce_message()
            elif command == 'h':
                self.print_help()
            elif command == 'x':
                try:
                    send_message(self.sock, self.produce_exit_message())
                except:
                    pass
                print('Connection closing.')
                LOGGER.info(
                    'process will be closed by user request.')
                time.sleep(0.5)
                break
            else:
                print('Unknown command, please try again.\n'
                      'h (help) - show list of useful commands')

    # function which calls help list
    def print_help(self):
        print('Commands: \n'
              'm - send message \n'
              'h - show list of a commands \n'
              'x - stop program and leave')


# The class that receives messages from the server.
# Receives messages, displays in the console.
class ClientIn(threading.Thread, metaclass=ClientBuilder):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # function - handler of messages from other users, received from server
    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(
                        f'\n Received message from user'
                        f' {message[SENDER]}: '
                        f'\n {message[MESSAGE_TEXT]}')
                    LOGGER.info(
                        f'\n Received message from user '
                        f'{message[SENDER]}: '
                        f'\n {message[MESSAGE_TEXT]}')
                else:
                    LOGGER.error(
                        f'Received incorrect message from server: '
                        f'{message}')
            except IncorrectDataRecivedError:
                LOGGER.error(f'message decoding failed')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOGGER.critical(f'connection with server was lost')
                break


@log
def produce_presence(account_name):
    """
    Function which generating presence of client
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(
        f'formed {PRESENCE} message from user {account_name}')
    return out


@log
def server_response(message):
    """
    Function to detect user presence which returns OK or Error
    """
    LOGGER.debug(
        f'analyzing server request: {message} ')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def argument_parser():
    """
    function to create parser of cmd, reads parameters and return
    three of them
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'attempt to launch client with wrong port number: {server_port}. '
            f'ports allowed from 1024 to 65535, process will be closed'
        )
        exit(1)

    return server_address, server_port, client_name


def server_launcher():
    """
    Loading param of cmd and do init of socket
    with transfer by result
    """
    print('Welcome to MikeT messenger!')
    server_address, server_port, client_name = argument_parser()

    if not client_name:
        client_name = input('Enter your name: ')
    else:
        print(f'You logged with name: {client_name}')

    LOGGER.info(
        f'client application was launched with parameters: '
        f'server address: {server_address} '
        f'port: {server_port}, mode: {client_name}'
    )

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, produce_presence(client_name))
        answer = server_response(get_message(transport))
        LOGGER.info(
            f'received response from server {answer}'
        )
        print(f'Connection to the server has been established')
    except json.JSONDecodeError:
        LOGGER.error(
            'failed to decode received Json string'
        )
        exit(1)
    except ServerError as error:
        LOGGER.error(
            f'during attempt to connect, server return error: {error.text}'
        )
        exit(1)
    except ReqFieldMissingError as missing_error:
        LOGGER.error(
            f'in server response has no requested field'
            f'{missing_error.missing_field}'
        )
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f'connection to server is not available'
            f' {server_addr}:{server_port}, '
            f'request to connect was refused'
        )
        exit(1)
    else:
        receive_data = ClientIn(client_name , transport)
        receive_data.daemon = True
        receive_data.start()

        send_data = ClientOut(client_name , transport)
        send_data.daemon = True
        send_data.start()
        LOGGER.debug('process launched')

        while True:
            time.sleep(1)
            if receive_data.is_alive() and send_data.is_alive():
                continue
            break


if __name__ == '__main__':
    server_launcher()
