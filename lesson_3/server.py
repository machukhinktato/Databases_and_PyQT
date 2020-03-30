import socket
import sys
import argparse
import json
import logging
import select
import time
import threading
import logs.config_server_log
from shared.errors import *
from shared.variables import *
from shared.utils import *
from shared.decos import log
from shared.descs import Port
from shared.metaclasses import ServerBuilder
from database import ServerStorage

LOGGER = logging.getLogger('server')


@log
def argument_parser():
    """
    parsing arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


# main class of server
class Server(threading.Thread, metaclass=ServerBuilder):
    port = Port()

    # parameters of connection
    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = dict()
        super().__init__()

    # prepares socket
    def init_socket(self):
        LOGGER.info(
            f'server launched, port to connect: {self.port}, '
            f'connections from: {self.addr}. '
            f'If address not specified, all connections '
            f'will be available')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    # internal processes, waits for connections, add|remove users
    # works with messages, tries to send them if exists
    def run(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'connection with address {client_address} stabilized')
                self.clients.append(client)

            income_list = []
            outcome_list = []
            err_lst = []
            try:
                if self.clients:
                    income_list, outcome_list, err_lst = \
                        select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if income_list:
                for client_with_message in income_list:
                    try:
                        self.income_message(get_message(
                            client_with_message), client_with_message)

                    except:
                        LOGGER.info(
                            f'user {client_with_message.getpeername()} '
                            f'logged out')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.outcome_message(message, outcome_list)

                except:
                    LOGGER.info(f'connection with user '
                                f'{message[DESTINATION]} is over')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    # The function of addressing a message to a specific client.
    # Accepts a dictionary message, a list of registered users and
    # listening sockets. Returns nothing.
    def outcome_message(self, message, listen_socks):

        if message[DESTINATION] in self.names and \
                self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)

            LOGGER.info(
                f'message to user {message[DESTINATION]} '
                f'by user {message[SENDER]}.')

        elif message[DESTINATION] in self.names and \
                self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError

        else:
            LOGGER.error(
                f'user {message[DESTINATION]} not logged, '
                f'sending is unavailable.')

    # A message handler from clients, receives a dictionary - a message
    # from a client, checks the correctness, sends a response dictionary
    # if necessary.
    def income_message(self, message, client):

        LOGGER.debug(f'Parsing a message from a client : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:

            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(
                    message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)

            else:
                response = RESPONSE_400
                response[ERROR] = 'User name is occupied.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return

        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return

        elif ACTION in message and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return

        else:
            response = RESPONSE_400
            response[ERROR] = 'Incorrect request.'
            send_message(client, response)
            return


def print_help():
    print('Commands: ')
    print('users - to call list of registred users ')
    print('connected - to call list of users online ')
    print('log - to show history of users enterance ')
    print('exit - to stop server process ')
    print('help - to call help menu')


# Loading command line parameters, if there are no parameters,
# then we set the values by default.
def server_launcher():
    listen_address, listen_port = argument_parser()
    database = ServerStorage()
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    print_help()

    while True:
        command = input('Enter command: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'user {user[0]}, last login: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(
                    f'user {user[0]}, connected: {user[1]}:{user[2]}, '
                    f'connection setup time {user[3]}'
                )
        elif command == 'log':
            name = input("Enter name of user to see log history. "
                         "To call all history just push 'enter': ")
            for user in sorted(database.login_history(name)):
                print(f"User: {user[0]}, logged from: {user[1]}. "
                      f"Entered from: {user[2]}:{user[3]}")
            else:
                print("Unknown command.")


if __name__ == '__main__':
    server_launcher()
