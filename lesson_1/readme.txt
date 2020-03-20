MikeT messenger.

1. Module description:
    a. shared - package with utilities for data transfer and global variables.
    b. logs - package with the configuration of logging and the logs themselves.
    c. test_unittest - autotests for checking the functionality of project functions
    d. client_side.py - main client module.
    e. decorators.py - function decorator for logging function calls.
    f. errors.py - Description of exception classes used in the project.
    g. simulation.py - auxiliary utility for simultaneously starting the server and several clients.
    h. server_side.py - main server module.

2. Client module - client_side.py
The module supports sending messages to recipients, while receiving new messages.
    Supported command line options:
        a. Server address. Allows you to specify the server address for the connection. By default, Localhost.
        b. Server port. Allows you to specify the port on which the connection will be made. By default: 7777
        in. -n or --name. The username in the system. Not set by default.
        If you do not specify this parameter, the program
        at startup, it will request a username for authorization in the system.
    After starting the application, an attempt will be made to establish a connection with the server.
    If successful, help will be displayed on the internal commands of the application:
        a. m. Send a MESSAGE. After entering the command, the application will ask for the recipient's name and the message itself.
        b. h. Re-displays HELP for application commands.
        in. x. Terminates the application (EXIT).

3. Server module - server_side.py
The module provides forwarding of messages received from clients to recipients. Messages are processed on the server and sent only to the addressee.
     Supported command line options:
         a. Port number. The port number on which the server will accept incoming connections. Default: 7777
         b. Address. The address from which the server will accept connections. By default, all addresses are listened.
     After starting the server, no additional steps are required.