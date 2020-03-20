"""
client server communication, server side code review
"""
import socket
import sys
import json
import argparse
import logging
import select
import time
import logs.config_log_server_side
from shared.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, \
    USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, \
    MESSAGE_TEXT, RESPONSE_400, DESTINATION, RESPONSE_200, EXIT
from shared.utilities import get_message, send_message
from shared.errors import UnreadableReceivedDataError
from shared.decorators import log

SERVER_SIDE_LOGGER = logging.getLogger('server_side_logger')


@log
def analyzer(message, message_list, client, clients, names):
    """
    A message handler from clients that accepts a dictionary -
    message from the client, checks the correctness, returns a
    response dictionary for a client
    """
    SERVER_SIDE_LOGGER.debug(f'analyze of client message {message}')
    if ACTION in message and message[ACTION] == PRESENCE and\
            TIME in message and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'name of user is occupied'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        message_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT \
            and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'bad request'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    The function of addressing a message to a specific client. Accepts a message dictionary,
    list of registered users and listening sockets. Returns nothing.
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_SIDE_LOGGER.info(f'Message was sent to user {message[DESTINATION]} '
                                f'from user {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_SIDE_LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


@log
def argument_parser():
    """
    parsing arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    addr_to_listen = namespace.a
    port_to_listen = namespace.p

    if not 1023 < port_to_listen < 65536:
        SERVER_SIDE_LOGGER.critical(
            f'attempt to launch server with wrong port '
            f'{port_to_listen}, allowed ports from 1024 to 65535.'
        )
        sys.exit(1)

    return addr_to_listen, port_to_listen


def server_launcher():
    """
    loading params of cmd, if they're not set,
    will defined by default, after that function detects
    addr which will be listen, prepares port and
    starts to receive a information
    """
    addr_to_listen, port_to_listen = argument_parser()

    SERVER_SIDE_LOGGER.info(
        f'server launched, port to connect: {port_to_listen} '
        f'connection from address: {addr_to_listen} '
        f'(If address not defined, connection will be available without it)'
    )

    transfer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer.bind((addr_to_listen, port_to_listen))
    transfer.settimeout(0.5)
    clients_online = []
    messages_queue = []
    names = dict()
    transfer.listen(MAX_CONNECTIONS)

    while True:
        try:
            client_socket_box, client_data = transfer.accept()
        except OSError:
            pass
        else:
            SERVER_SIDE_LOGGER.info(f'connection with PC {client_data} stabilized')
            clients_online.append(client_socket_box)

        data_list_for_receiving = []
        data_list_to_send = []
        data_list_of_err_occured = []

        try:
            if clients_online:
                data_list_for_receiving, data_list_to_send, data_list_of_err_occured = \
                    select.select(clients_online, clients_online, [], 0)
        except OSError:
            pass
        if data_list_for_receiving:
            for msg_by_client in data_list_for_receiving:
                try:
                    analyzer(get_message(msg_by_client),
                             messages_queue, msg_by_client, clients_online,
                             names)
                except Exception:
                    SERVER_SIDE_LOGGER.info(f'client {msg_by_client.getpeername()} '
                                            f'disconnected from server')
                    clients_online.remove(msg_by_client)
        for i in messages_queue:
            try:
                process_message(i, names, data_list_to_send)
            except Exception:
                SERVER_SIDE_LOGGER.info(
                    f'connection with client {i[DESTINATION]} lost'
                )
                clients_online.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages_queue.clear()


if __name__ == '__main__':
    server_launcher()
