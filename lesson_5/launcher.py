import subprocess

process = []

while True:
    action = input('Choose: q - quit \n'
                   's - server run \n'
                   'c - console run \n'
                   'x - terminate processes\n'
                   'Your choise: ')
    if action == 'q':
        break
    elif action == 's':
        process.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'c':
        clients_count = int(input('Console number to launch: '))
        for i in range(clients_count):
            process.append(subprocess.Popen(f'python client.py -n Anonymous{i + 1}', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while process:
            process.pop().kill()