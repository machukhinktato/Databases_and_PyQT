"""client server communication, client side code review"""
import sys
import json
import socket
import time
import argparse
import logging
import threading
import logs.config_log_client_side
from shared.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from shared.utilities import get_message, send_message
from shared.errors import RequestedFieldAbsentError, ExceptionServerError, \
    UnreadableReceivedDataError
from shared.decorators import log

CLIENT_SIDE_LOGGER = logging.getLogger('client_side_logger')


@log
def command_to_exit(account_name):
    """
    function creates dictionary with message to leave
    :param account_name:
    :return:
    """
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def server_msg_handler(from_socket, to_socket):
    """
    function - handler of messages from other users, received from server
    """
    while True:
        try:
            message = get_message(from_socket)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and\
                    message[DESTINATION] == to_socket:
                print(f'\n Received message from user {message[SENDER]}: '
                      f'\n {message[MESSAGE_TEXT]}')
                CLIENT_SIDE_LOGGER.info(
                    f'\n Received message from user {message[SENDER]}: '
                    f'\n {message[MESSAGE_TEXT]}'
                )
            else:
                CLIENT_SIDE_LOGGER.error(
                    f'Received incorrect message from server: {message}')
        except UnreadableReceivedDataError:
            CLIENT_SIDE_LOGGER.error(
                f'message decoding failed'
            )
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_SIDE_LOGGER.critical(
                f'connection with server was lost'
            )
            break


@log
def message_writer(to_socket, account_name='Anonymous'):
    """
    function requests message text and returns him,
    also it may leave program, by necessity
    :param to_socket:
    :param account_name:
    :return formed_dict_to_send:
    """
    to_receiver = input('Send message to user: ')
    message = input('Enter text message: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_receiver,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_SIDE_LOGGER.debug(
        f'message dict formed: {message_dict}'
    )
    try:
        send_message(to_socket, message_dict)
        CLIENT_SIDE_LOGGER.info(
            f'message to {to_receiver} was sent'
        )
    except:
        CLIENT_SIDE_LOGGER.critical(
            'something going wrong, '
            'connection with server will be lost'
        )
        sys.exit(1)


@log
def user_online(from_socket, client_name):
    """
    function coop with user, requests commands, sends msgs
    :param from_socket:
    :param client_name:
    :return:
    """
    helper()
    while True:
        command = input('Enter command: ')
        if command == 'm':
            message_writer(from_socket, client_name)
        elif command == 'h':
            helper()
        elif command == 'x':
            send_message(from_socket, command_to_exit(client_name))
            print('connection will be closed')
            CLIENT_SIDE_LOGGER.info(
                f'process will be closed by user request'
            )
            time.sleep(0.8)
            break
        else:
            print('Unknown command, please try again.\n'
                  'To call help(show list of useful commands)'
                  'Enter - h : ')


@log
def launch_presence(account_name='Anonymous'):
    """
    Function which generating presence of client
    """
    note_to_server = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_SIDE_LOGGER.debug(
        f'formed {PRESENCE} message from user {account_name}')
    return note_to_server


@log
def helper():
    print('Commands: \n'
          'm - send message \n'
          'h - show list of a commands \n'
          'x - stop program and leave')


@log
def server_response(message):
    """
    Function to detect user presence which returns OK or Error
    """
    CLIENT_SIDE_LOGGER.debug(f'analyzing server request: {message} ')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ExceptionServerError(f'400 : {message[ERROR]}')
    raise RequestedFieldAbsentError(RESPONSE)


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
    server_addr = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        CLIENT_SIDE_LOGGER.critical(
            f'attempt to launch client with wrong port number: {server_port}. '
            f'ports allowed from 1024 to 65535, process will be closed'
        )
        sys.exit(1)

    return server_addr, server_port, client_name


def client_initializer():
    """
    Loading param of cmd and do init of socket
    with transfer by result
    """
    print('Welcome to MikeT messenger!')
    server_addr, server_port, client_name = argument_parser()

    if not client_name:
        client_name = input('Enter your name: ')

    CLIENT_SIDE_LOGGER.info(
        f'client application was launched with parameters: '
        f'server address: {server_addr} '
        f'port: {server_port}, mode: {client_name}'
    )
    try:
        transfer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transfer.connect((server_addr, server_port))
        send_message(transfer, launch_presence(client_name))
        answer = server_response(get_message(transfer))
        CLIENT_SIDE_LOGGER.info(f'received response from server {answer}')
        print('Сonnection to the server has been established')
    except json.JSONDecodeError:
        CLIENT_SIDE_LOGGER.error(
            f'failed to decode received Json string'
        )
        sys.exit(1)
    except ExceptionServerError as error:
        CLIENT_SIDE_LOGGER.error(
            f'during attempt to connect, server return error: {error.text}'
        )
        sys.exit(1)
    except RequestedFieldAbsentError as missing_error:
        CLIENT_SIDE_LOGGER.error(f'in server response has no requested field'
                                 f'{missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_SIDE_LOGGER.critical(
            f'connection to server is not available'
            f' {server_addr}:{server_port}, '
            f'request to connect was refused'
        )
        sys.exit(1)
    else:
        target_side = threading.Thread(
            target=server_msg_handler, args=(transfer, client_name))
        target_side.daemon = True
        target_side.start()

        user_side = threading.Thread(
            target=user_online, args=(transfer, client_name))
        user_side.daemon = True
        user_side.start()
        CLIENT_SIDE_LOGGER.debug('process started')

        while True:
            time.sleep(1)
            if target_side.is_alive() and user_side.is_alive():
                continue
            break


if __name__ == '__main__':
    client_initializer()
