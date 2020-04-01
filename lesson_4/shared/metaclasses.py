import dis


class ServerBuilder(type):
    """
    metaclass to check server conformity
    """
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
            raise TypeError(
                'Usage of connect method in server class is impossible'
            )
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError(
                'Incorrect socket initialization'
            )
        super().__init__(clsname, bases, clsdict)


class ClientBuilder(type):
    """
    metaclass to check client conformity
    """
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
                raise TypeError(
                    'prohibited method usage - detected'
                )
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError(
                'There is no functions who works with sockets'
            )
        super().__init__(clsname, bases, clsdict)
