import subprocess
import sys
from subprocess import Popen
from os import path

"""Файл для запуска серверной части и нескольких клиентов"""

process_list = []

path_to_file = path.dirname(__file__)
path_to_server = path.join(path_to_file, 'server.py')
path_to_client = path.join(path_to_file, 'client.py')


def start(count):
    process_list.append(Popen(f'python server.py', shell=True, stdout=subprocess.PIPE))
    for i in range(count):
        username = 'user' + str(i + 1)
        process_list.append(Popen(f"python client.py -n {username}",
                                  shell=True,
                                  stdout=subprocess.PIPE))
        print(process_list)


while True:
    mode = input('Выберите подходящее действие:'
                 ' q = выход'
                 ' s - запустить сервер и клиентов,'
                 ' e - закрыть все окна: ')

    if mode.lower() == 'q':
        break
    elif mode.lower() == 's':
        start(3)

    elif mode.lower() == 'e':
        while process_list:
            process_to_delete = process_list.pop()
            process_to_delete.kill()
