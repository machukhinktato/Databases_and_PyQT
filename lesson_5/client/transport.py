import socket
import sys
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append('../')
from common.utils import *
from common.variables import *
from common.errors import ServerError

logger = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.database = database
        self.username = username
        self.transport = None
        self.connection_init(port, ip_address)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'Connection with server lost.')
                raise ServerError('Connection with server lost!')
            logger.error('Connection timeout during update users list.')
        except json.JSONDecodeError:
            logger.critical(f'Connection with server lost.')
            raise ServerError('Connection with server lost!')
        self.running = True

    def connection_init(self, port, ip):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.transport.settimeout(5)

        connected = False
        for i in range(5):
            logger.info(f'attempt to connect №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            logger.critical('Connection with server lost.')
            raise ServerError('Connection with server lost!')

        logger.debug('connection established')

        try:
            with socket_lock:
                send_message(self.transport, self.create_presence())
                self.process_server_ans(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            logger.critical('Connection with server lost.')
            raise ServerError('Connection with server lost!')

        logger.info('connection established.')

    def create_presence(self):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        logger.debug(f'there is {PRESENCE} message to user {self.username}')
        return out

    def process_server_ans(self, message):
        logger.debug(f'Parsing server message: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                logger.debug(f'unknown code number received {message[RESPONSE]}')

        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message and message[DESTINATION] == self.username:
            logger.debug(f'received message by {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER] , 'in' , message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def contacts_list_update(self):
        logger.debug(f'contact list request by user {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        logger.debug(f'request formed {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        logger.debug(f'answer received {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            logger.error('could not refresh list of contacts.')

    def user_list_update(self):
        logger.debug(f'friends list request {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            logger.error('could not refresh friends list')

    def add_contact(self, contact):
        logger.debug(f'creating of contact {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def remove_contact(self, contact):
        logger.debug(f'deleting contact {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def transport_shutdown(self):
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        logger.debug('transport closes his work.')
        time.sleep(0.5)

    def send_message(self, to, message):
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'dict of message formed: {message_dict}')

        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_ans(get_message(self.transport))
            logger.info(f'message to user {to} sent')

    def run(self):
        logger.debug('process launched - receiver of server messages.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Connection with server lost.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.debug(f'connection with server lost.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    logger.debug(f'server message received: {message}')
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)
