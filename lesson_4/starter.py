""" Program runner"""

import subprocess

PROCESS = []

while True:
    ACTION = input('please, choose the options: '
                   's - launch server, '
                   'x - close all windows, '
                   'q - quit program: ')
    if ACTION == 'q':
        break
    elif ACTION == 's':
        clients_count = int(input('Enter number of consoles to launch: '))
        # Запускаем сервер!
        PROCESS.append(subprocess.Popen(
            'python server.py',
            creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(clients_count):
            PROCESS.append(subprocess.Popen(
                f'python client.py -n {i + 1}',
                creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            PROCESS.pop().kill()
