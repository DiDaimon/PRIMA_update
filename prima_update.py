# -*- coding: utf-8 -*-
"""Программа выполняет обновление PRIMA с сервера.



Version:
    1.0
    1.1 Рефакторинг кода, добавление комментариев.
TODO:
    * Переписать конфигурацию на конфиг TOML

"""
import configparser
import os
import shutil
from datetime import datetime
from filecmp import dircmp
from art import tprint
from colorama import init, Fore, Style

# Читаем файл с настройками и объявляем глобальные переменные.
config = configparser.ConfigParser()
config.read("settings.ini")
DIR_SOURCE = config['Global']['server_directory']
DIR_DESTINATION = config['Global']['local_directory']
IGNORE = config['Ignore']['list'].split(sep=',')  # Список файлов и папок для игнорирования.

# Добавляем краски в терминал
init(autoreset=True)
MESSAGE_FAILED = Fore.RED + Style.BRIGHT + "[FAILED] " + Style.RESET_ALL + Fore.RED
MESSAGE_ATTENTION = Fore.YELLOW + Style.BRIGHT + "[ATTENTION] " + Style.RESET_ALL + Fore.YELLOW
MESSAGE_OK = Fore.GREEN + Style.BRIGHT + "[OK] " + Style.RESET_ALL + Fore.GREEN
MESSAGE_WARNING = Fore.BLUE + Style.BRIGHT + "[WARNING] " + Style.RESET_ALL + Fore.BLUE


def clear_terminal():
    """
    Clears the terminal screen.

    This function is used to clear the terminal screen by executing the appropriate command based
    on the operating system. If the operating system is Windows, the 'cls' command is executed.
    Otherwise, the 'clear' command is executed.

    """
    os.system('cls' if os.name == 'nt' else 'clear')


def update_lnk():
    """
    Updates the shortcut on the desktop with the latest version of PRIMA.
    
    This function takes no parameters.
    
    Raises:
        FileNotFoundError: If the PRIMA executable file is not found in the source directory.
    """
    path = os.path.expanduser('~\\Desktop\\')
    date_change = os.path.getmtime(os.path.join(DIR_SOURCE, 'PRIMA.exe'))
    new_date = datetime.fromtimestamp(date_change).strftime('%d.%m.%y')
    for file in os.listdir(path):
        if '[PRIMA]' in file:
            old_name = file
            os.rename(os.path.join(path, old_name), os.path.join(path, f'[PRIMA] {new_date}.lnk'))
            print(f'{MESSAGE_OK}Ярлык на Рабочем столе изменен на [PRIMA] {new_date}')
            return
    print(f'{MESSAGE_FAILED}Ярлык на рабочем столе не найден')


def copy_diff_files(files):
    """
    Copies the specified files to a destination directory.

    Args:
        files (List[str]): A list of file paths to be copied.

    Returns:
        None

    Raises:
        OSError: If an error occurs while copying the files.
    """
    for file in files:
        source = file
        destination = file.replace(DIR_SOURCE, DIR_DESTINATION)
        if os.path.isdir(file):
            try:
                shutil.copytree(source, destination)
                print(f'{MESSAGE_OK}Каталог {destination} успешно переписан')
            except:
                print(f'{MESSAGE_FAILED}Каталог {destination} не переписан')
        else:
            try:
                shutil.copy(source, destination)
                print(f'{MESSAGE_OK}Файл {destination} успешно переписан')
            except:
                print(f'{MESSAGE_FAILED}Файл {destination} не переписан')


def copy_tree():
    """
    Copy the entire directory tree (including all files and subdirectories) from DIR_SOURCE to
    DIR_DESTINATION. If the destination directory already exists, the function will copy the
    contents of DIR_SOURCE into it. If the destination directory does not exist, it will be created.
    """
    try:
        shutil.copytree(DIR_SOURCE, DIR_DESTINATION, dirs_exist_ok=True)
        print(f'{MESSAGE_OK}Папка PRIMA полностью скопирована.')
    except:
        print(f'{MESSAGE_FAILED}Копирование не удалось')


def diff_files(dcmp, diff_lst: list, only_lst: list):
    """
    Generate a list of files that are different or missing between two directories.

    Args:
        dcmp (dc.DirCmp): A directory comparison object.
        diff_lst (list): A list to store the paths of different files.
        only_lst (list): A list to store the paths of missing files.
    """
    if dcmp.diff_files:
        for file in dcmp.diff_files:
            print(f'{MESSAGE_ATTENTION}[*] Файл изменен: {file}')
            diff_lst.append(f'{dcmp.left}\\{file}')
    if dcmp.left_only:
        for file in dcmp.left_only:
            print(f'{MESSAGE_ATTENTION}[-] Файл отсутствует: {file}')
            only_lst.append(f'{dcmp.left}\\{file}')
    for sub_dcmp in dcmp.subdirs.values():
        diff_files(sub_dcmp, diff_lst, only_lst)


def user_interface():
    """
    Displays a user interface menu and prompts the user to choose an action.

    Returns:
        int: The user's chosen action, which is a number between 1 and 5.
    """
    print('''
Выберите действие и нажмите Enter:
 [1] Для замены измененных файлов.
 [2] Для копирования отсутствующих файлов.
 [3] Для внесения всех изменений.
 [4] Для полного копирования.
 [5] Для пропуска (без изменений).
    ''')
    while True:
        answer = input('Выберите действие: ')
        if answer.isdecimal() and 1 <= int(answer) <= 5:
            return int(answer)
        else:
            print('Неверный ввод повторить')


def main():
    """
	This function is the main entry point of the program.

    It clears the terminal, prints the program name, and checks for changes between two directories.
    It then prompts the user for a choice and performs different actions based on the user's input.
    The function returns nothing.

	"""
    # Выводим название программы
    clear_terminal()
    tprint('PRIMA - UPDATER', font='tarty1')

    diff_object = dircmp(DIR_SOURCE, DIR_DESTINATION, IGNORE)
    print('\nПроверка наличия изменений:')
    diff, only = [], []
    diff_files(diff_object, diff, only)
    if not diff and not only:
        print(f'{MESSAGE_OK}Изменений не обнаружено.')
        return
    choice = user_interface()
    if choice == 1:
        copy_diff_files(diff)
        update_lnk()
    elif choice == 2:
        copy_diff_files(only)
        update_lnk()
    elif choice == 3:
        copy_diff_files(diff + only)
        update_lnk()
    elif choice == 4:
        copy_tree()
        update_lnk()
    elif choice == 5:
        print(f'{MESSAGE_OK}Изменения внесены не будут.')


# A common idiom to place the main functionality of a Python script in a function called main,
# and then use the following idiom at the end of the script:
if __name__ == '__main__':
    main()
