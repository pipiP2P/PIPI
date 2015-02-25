from win32com.shell import shell, shellcon
import hashlib
import os
from os import listdir
from os.path import isfile, join
PATH = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0) + "\PiPi"

def get_file_object(file_path, name):
    _hash = sha1OfFile(file_path)
    file_size = os.path.getsize(file_path)
    desc_path = PATH + "\\" + sha1OfFile(file_path) + ".txt"
    if os.path.isfile(desc_path):
        description = open(desc_path, 'r').read()
    else:
        description = ""



def sha1OfFile(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def get_all_files():
    """
    Creates the special directory of the program if it wasn't already created
    and returns list of tuples of files in the folder with their SHA1
    """
    check_folder()
    names_with_SHA1 = [[f, sha1OfFile(PATH + "\\" + f)] for f in listdir(PATH) if isfile(join(PATH, f))]
    return names_with_SHA1


def check_folder():
    """ Create folder if it doesn't exist """
    if not os.path.exists(PATH):
        os.makedirs(PATH)
