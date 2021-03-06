"""
Common variables
"""
import logging

# default port for network connections
DEFAULT_PORT = 7777
# default ip address for connection
DEFAULT_IP_ADDRESS = '127.0.0.1'
# max queue of connections
MAX_CONNECTIONS = 5
# maximal length of message in bytes
MAX_PACKAGE_LENGTH = 1024
# coding
ENCODING = 'utf-8'
# actual logging level
LOGGING_LEVEL = logging.DEBUG
# database for server storage:
SERVER_CONFIG = 'server.ini'
# database for data storage:
SERVER_DATABASE = 'sqlite:///server_base.db3'
# JIM protocol main keys
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'
# other keys usable in protocols
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
# dictionary responses:
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202, LIST_INFO: None}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}
