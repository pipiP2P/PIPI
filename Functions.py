from win32com.shell import shell, shellcon
import hashlib
import os
from os import listdir
from os.path import isfile, join
from File import File_Info
import Tkinter
import tkMessageBox
import win32api
import win32con

PATH = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0) + "\PiPi"
MB = 1000000


def check_if_new_file(files_list):
    new_files_list = get_all_files()
    return new_files_list == files_list


def get_file_object(file_path, name):
    """
    Returns an object of type File_Info for the file 'name' in file_path
    """
    _hash = sha1OfFile(file_path)
    file_size = os.path.getsize(file_path)
    desc_path = PATH + "\\" + sha1_of_file(file_path) + ".txt"
    if os.path.isfile(desc_path):
        description = open(desc_path, 'r').read()
    else:
        create_description(name, file_path)
    if file_size % MB == 0:
        num_of_parts = file_size / MB
    else:
        num_of_parts = file_size / MB + 1
    final_object = File_Info(name, description, file_size, num_of_parts, _hash)
    return final_object


def sha1_off_file(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def get_all_files():
    return get_all_files_two(PATH)


def get_all_files_two(check_path):
    """
    Creates the special directory of the program if it wasn't already created
    and returns list of tuples of files in the folder with their SHA1
    """
    check_folder()
    names_with_sha1 = []
    for f in listdir(check):
        if os.path.isdir(join(check_path, f)):
            names_with_sha1 += get_all_files_two(join(check_path, f))
        elif os.path.isfile(join(check_path, f)):
            names_with_sha1.append(get_file_object(check_path, f))
    return names_with_sha1


def check_folder():
    """ Create folder if it doesn't exist """
    if not os.path.exists(PATH):
        os.makedirs(PATH)


def create_description(name, path):
    if os.path.isfile(join(path, name)):
        description = open(sha1_off_file(join(path, name), 'w'))
        description.write("No Description")
        fn = path + name
        os.popen('attrib +h ' + fn)
