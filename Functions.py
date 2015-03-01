from win32com.shell import shell, shellcon
import hashlib
import os
from os import listdir
from os.path import *
from File import File_Info
import ctypes


PATH = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0) + "\\PiPi"
MB = 1000000


def check_if_new_file(files_list):
    """
    Checks if a new file was added to the sharing folder
    """
    new_files_list = get_all_files()
    return new_files_list == files_list


def get_file_object(file_path, name):
    """
    Returns an object of type File_Info for the file 'name' in file_path
    """
    _hash = sha1_of_file(file_path + "\\" + name)
    file_size = os.path.getsize(file_path)
    desc_path = PATH + "\\" + _hash + ".txt"
    if os.path.isfile(desc_path):
        description = open(desc_path, 'r').read()
    else:
        create_description(name, file_path)
        description = open(desc_path, 'r').read()
    if file_size % MB == 0:
        num_of_parts = file_size / MB
    else:
        num_of_parts = file_size / MB + 1
    final_object = File_Info(name, description, file_size, num_of_parts, _hash)
    return final_object


def sha1_of_file(file_path):
    """
    Returns sha1 of file
    """
    with open(file_path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def get_all_files():
    """
    Creates the special directory of the program if it wasn't already created
    and returns list of File_info objects of all files in folder
    """
    check_folder()
    return get_all_files_two(PATH)


def get_all_files_two(check_path):
    names_with_sha1 = []
    for f in listdir(check_path):
        if os.path.isdir(join(check_path, f)):
            names_with_sha1 += get_all_files_two(join(check_path, f))
        elif os.path.isfile(join(check_path, f)):
            if not has_hidden_attribute(join(check_path, f)):
                names_with_sha1.append(get_file_object(check_path, f))
    return names_with_sha1


def check_folder():
    """ Create folder if it doesn't exist """
    if not os.path.exists(PATH):
        os.makedirs(PATH)


def create_description(name, path):
    """
    Creates a description hidden txt file for a specific file, txt file name is sha1 of file
    """
    if os.path.isfile(join(path, name)):
        desc_path = path + "\\" + sha1_of_file(path + "\\" + name) + ".txt"
        description = open(desc_path, 'w')
        description.write("No Description")
        description.close()
        os.popen('attrib +h ' + desc_path)


def has_hidden_attribute(file_path):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(file_path))
        assert attrs != -1
        result = bool(attrs & 2)
    except (AttributeError, AssertionError):
        result = False
    return result
