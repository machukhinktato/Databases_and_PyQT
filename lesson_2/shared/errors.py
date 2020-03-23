"""errors"""


# Exception - invalid data received from socket
class IncorrectDataRecivedError(Exception):
    def __str__(self):
        return 'Invalid message received from remote computer.'


# Exception - server error
class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


# Exception - function argument is not a dictionary.
class NonDictInputError(Exception):
    def __str__(self):
        return 'The argument of the function must be a dictionary.'


# Error - there is no required field in the accepted dictionary.
class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'The accepted dictionary is missing a required field {self.missing_field}.'
