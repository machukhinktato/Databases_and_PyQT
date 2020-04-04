import dis


# Metaclass for checking server compliance:
class ServerMaker(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        attrs = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        if 'connect' in methods:
            raise TypeError('usage of connect method invalid in server class')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('incorrect socket inizialization.')
        super().__init__(clsname, bases, clsdict)


# Metaclass for validating clients:
class ClientMaker(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('Usage of prohibited method - detected')
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Absence of socket function calls.')
        super().__init__(clsname, bases, clsdict)
