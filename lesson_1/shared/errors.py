"""Errors"""


class UnreadableReceivedDataError(Exception):
    """
    Incorrect data were received from socket
    """
    def __str__(self):
        return 'Invalid message received from a remote computer.'


class RequestedFieldAbsentError(Exception):
    """
    Requested field is absent
    """
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'In accepted dictionary a required field ' \
               f'{self.missing_field} was missed.'


class ExceptionServerError(Exception):
    """Exception - server error"""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class DictArgumentNotFound(Exception):
    """Exception due to type of var which is not dict"""
    def __str__(self):
        return 'Argument of function shall be dict'
