import sys
import json
import socket
import time
import argparse
import logging
import threading
import logs.config_client_log
from shared.variables import *
from shared.utils import *
from shared.errors import *
from shared.decos import log
from shared.metaclasses import ClientBuilder
from client_database import ClientDatabase

# Initialization of the client logger
logger = logging.getLogger('client')

# Socket Lock and Database Object
sock_lock = threading.Lock()
database_lock = threading.Lock()


# Class of handling and sending messages on server and user
class ClientOut(threading.Thread, metaclass=ClientBuilder):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    # The function creates a dictionary with an exit message.
    def call_logout(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    # The function asks who to send the message
    # to and the message itself, and sends the
    # received data to the server.
    def create_message(self):
        to = input('Message to user: ')
        message = input('Enter message: ')

        with database_lock:
            if not self.database.check_user(to):
                logger.error(f'attempt to send message for unregistered user: {to}')
                return

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'dict message formed: {message_dict}')

        with database_lock:
            self.database.save_message(self.account_name, to, message)

        with sock_lock:
            try:
                send_message(self.sock, message_dict)
                logger.info(f'Message for user {to} sent')
            except OSError as err:
                if err.errno:
                    logger.critical('connection with server lost.')
                    exit(1)
                else:
                    logger.error('unable to send message. Connection timeout.')

    # function coop with user, requests commands, sends msgs
    def run(self):
        self.print_help()
        while True:
            command = input('Enter command: ')
            if command == 'm':
                self.create_message()
            elif command == 'h':
                self.print_help()
            elif command == 'x':
                with sock_lock:
                    try:
                        send_message(self.sock, self.call_logout())
                    except:
                        pass
                    print('Program closing.')
                    logger.info('programm will be close by user request')
                time.sleep(0.5)
                break

            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

            elif command == 'edit':
                self.edit_contacts()

            elif command == 'history':
                self.print_history()

            else:
                print('Unknown command, please try again.\n'
                      'h (help) - show list of useful commands')

    def print_help(self):
        print('Commands:')
        print('m - send message')
        print('history - call a history of messages')
        print('contacts - list of contacts')
        print('edit - edit list of contacts')
        print('h - show list of a commands')
        print('x - stop program and leave')

    def print_history(self):
        ask = input('Show incoming messages - in, outcoming - out, '
                    'all - just press Enter:')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'\nUser message: {message[0]} by {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nMessage to user: {message[1]} by {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(
                        f'\nMessage from user:  {message[0]}, to user  {message[1]} by {message[3]}\n{message[2]}')

    # Функция изменеия контактов
    def edit_contacts(self):
        ans = input('for delete enter - del, to add - add: ')
        if ans == 'del':
            edit = input('Enter name of account to delete: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    logger.error('attempt to delete unregistred user')
        elif ans == 'add':
            edit = input('Create new user, name: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        logger.error('unable to send information on server')


# The class that receives messages from the server.
# Receives messages, displays in the console.
class ClientIn(threading.Thread, metaclass=ClientBuilder):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    # function - handler of messages from other users, received from server
    def run(self):
        while True:
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)

                except IncorrectDataRecivedError:
                    logger.error(f'message decoding failed')
                except OSError as err:
                    if err.errno:
                        logger.critical(f'connection with server lost (run)')
                        break
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    logger.critical(f'connection with server was lost')
                    break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                            and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                        print(f'\nReceived message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except:
                                logger.error('error while connect with database')

                        logger.info(f'received message by user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        logger.error(f'received incorrect message from server: {message}')


@log
def create_presence(account_name):
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
    logger.debug(f'formed {PRESENCE} message from user {account_name}')
    return out


@log
def server_response(message):
    """
    Function to detect user presence which returns OK or Error
    """
    logger.debug(f'analyzing server request: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)



@log
def arg_parser():
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
        logger.critical(
            f'attempt to launch server with incorrect number of port: {server_port}. '
            f'addresses allowed between 1024 untilо 65535. Connection is over.')
        exit(1)

    return server_address, server_port, client_name


def contacts_list_request(sock, name):
    logger.debug(f'reuqest of contact list by user {name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    logger.debug(f'request formed {req}')
    send_message(sock, req)
    ans = get_message(sock)
    logger.debug(f'answer received {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def add_contact(sock, username, contact):
    logger.debug(f'creating contact {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Creating contact error')
    print('successful creating contact')


# function requests a list of users whom been there before
def user_list_request(sock, username):
    logger.debug(f'user list request {username}')
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def remove_contact(sock, username, contact):
    logger.debug(f'Creating contacts {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('detele error')
    print('delete successful')


def database_load(sock, database, username):
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        logger.error('databse load request error.')
    else:
        database.add_users(users_list)

    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        logger.error('List of contact request error')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    print('Welcome to MikeT messenger!')

    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Enter your name: ')
    else:
        print(f'You logged with name: {client_name}')

    logger.info(
        f'client application was launched with parameters:\n'
        f'server address: {server_address}\n'
        f'port: {server_port}, mode: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        transport.settimeout(1)

        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = server_response(get_message(transport))
        logger.info(f'received response from server: {answer}')
        print(f'Connection to the server has been established')
    except json.JSONDecodeError:
        logger.error('failed to decode received Json string')
        exit(1)
    except ServerError as error:
        logger.error(f'during attempt to connect, server return error: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'in server response has no requested field '
                     f'{missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'connection to server is not available'
            f' {server_addr}:{server_port}, '
            f'request to connect was refused')
        exit(1)
    else:

        database = ClientDatabase(client_name)
        database_load(transport, database, client_name)

        module_sender = ClientOut(client_name, transport, database)
        module_sender.daemon = True
        module_sender.start()
        logger.debug('Запущены процессы')

        module_receiver = ClientIn(client_name, transport, database)
        module_receiver.daemon = True
        module_receiver.start()

        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
