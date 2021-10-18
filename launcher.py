import subprocess

"""Файл для запуска серверной части и нескольких клиентов (в окнах)"""

process_list = []

while True:
    mode = input('Выберите подходящее действие:'
                 ' q = выход'
                 ' s - запустить сервер и клиентов,'
                 ' e - закрыть все окна: ')

    if mode.lower() == 'q':
        break
    elif mode.lower() == 's':
        process_list.append(subprocess.Popen(f'python server.py',
                                             creationflags=subprocess.CREATE_NEW_CONSOLE))
        process_list.append(subprocess.Popen('python client.py -n client1',
                                             creationflags=subprocess.CREATE_NEW_CONSOLE))
        process_list.append(subprocess.Popen('python client.py -n client2',
                                             creationflags=subprocess.CREATE_NEW_CONSOLE))
        process_list.append(subprocess.Popen('python client.py -n client3',
                                             creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif mode.lower() == 'e':
        while process_list:
            process_to_delete = process_list.pop()
            process_to_delete.kill()
