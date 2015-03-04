import socket
import select
import time
from threading import Thread

from Protocol import *
from Functions import *


MESSAGE_LENGTHS = [2, 3, 4, 5]
FILE_REQUEST = '1'
FILE_RESPONSE = '2'
PART_REQUEST = '3'
PART_RESPONSE = '4'
COMMANDS_NUMS = [FILE_REQUEST, FILE_RESPONSE, PART_REQUEST, PART_RESPONSE]
UDP_PORT = 6000
MY_FILES = []
OTHERS_FILES = []
ADDRESSES = []
MY_ADDR = socket.gethostbyname(socket.gethostname())
init_time = int(time.time())

def debug_print(dbg_info):
    print dbg_info


def create_files_message():
    """
    Create a message of all of the files
    """
    string_list = []
    for cur_file in MY_FILES:
        string_list.append(cur_file.to_string())
    return '$'.join(string_list)


def send_search_answer_true(file_found, client_socket):
    """
    Sends True to the client if we found his hash in our folder
    """
    reply_message = [FILE_RESPONSE, '1', file_found.get_hash(), file_found.get_num_of_parts(), file_found.get_size()]
    client_socket.send(';'.join(reply_message))
    debug_print( "We have found this hash " + file_found.get_hash())


def send_search_answer_false(requested_hash, client_socket):
    """
    Sends False to the client if we couldn't find his hash in our folder
    """
    debug_print("We didn't have this hash in our file library:" + requested_hash)
    reply_message = [FILE_RESPONSE, '0', '0', '0', '0']
    client_socket.send(';'.join(reply_message))
    
def file_exists(file_hash):
    """
     Returns true if we have the file hash in our directory
    """
    all_files = get_all_files()
    for current_file in all_files:
        if current_file.get_hash() == file_hash:
            # We found the file
            return current_file
    return False


def question_file_exists(file_hash, client_socket):
    """
    Checks if we have the file - if we do we send the appropriate answer
    """
    current_file = file_exists(file_hash)
    if current_file:
        send_search_answer_true(current_file, client_socket)
    else:
        send_search_answer_false(file_hash, client_socket)


def add_files(files_list):
    files_list = files_list.split('$')
    for cur_file in files_list:
        cur_file = cur_file.split(';')
        if len(cur_file) == 5:
            if ';'.join(cur_file) not in OTHERS_FILES:
                OTHERS_FILES.append(';'.join(cur_file))

def handle_sending_part(file_requested, part_number, client_socket):
    file_content = file_requested.get_file_content(part_number)
    client_socket.send(file_content)


def udp_connection_handler():
    """
    Handles the UDP connection with the other peers

    """
    files_we_can_share = get_all_files()
    while True:
        rlist, wlist, xlist = select.select([udp_socket], [udp_socket], [])
        for current_socket in rlist:
            try:
                data_received = current_socket.recv(4096)
                if data_received != "":
                    all_list = convert_message(data_received)
                    list_length = len(all_list)
                    if list_length == 1:
                        # Error while analysing the message
                        debug_print(all_list[0])
                    elif list_length == 2:
                        # Do we have the file?
                        # We will search our special directory to find the file name requested
                        protocol_number, file_hash = all_list
                        question_file_exists(file_hash, current_socket)

                    elif list_length == 3:
                        # We were requested parts of the file we are sharing
                        protocol_number, file_hash, requested_parts_numbers = all_list
                        file_object = file_exists(file_hash)
                        if file_object:
                            parts_number = file_object.get_num_of_parts()
                            for part_number in requested_parts_numbers:
                                if part_number in parts_number:
                                    # We have the requested part
                                    debug_print("We have this part!")
            except:
                debug_print( "[-] Error trying to analyse or send info")
    time.sleep(0.001)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('', UDP_PORT))
client_socket = socket.socket()
try:
    client_socket.connect(('10.10.10.122', 50000))
except:
    user_to_connect = raw_input("Could not connect to main server. Please write your friend IP")
    is_connected = 0
    while not is_connected:
        try:
            client_socket.connect((user_to_connect, 40000))
            is_connected = 1
            debug_print("Connected to " + user_to_connect)
            data = client_socket.recv(1024)
            ADDRESSES = data.split(';')
        except:
            debug_print("Couldn't connect to" + user_to_connect)
            user_to_connect = raw_input("Could not connect to your friend. Please write others friend IP")


thread = Thread(target=udp_connection_handler, args=[])
thread.start()
if __name__ == '__main__':
    while True:
        rlist, wlist, xlist = select.select([client_socket], [client_socket], [])
        for current_socket in rlist:
            data = current_socket.recv(1024)
            print data
            if data.startswith("ping"):
                debug_print("Received ping, sending back PONG")
                # add_files(data[4:])
                current_socket.send("pong")

            elif data.startswith("remove "):
                ip_to_remove = data.split(' ')
                if len(ip_to_remove) == 2:
                    ip_to_remove = ip_to_remove[1]
                    if ip_to_remove in ADDRESSES:
                        ADDRESSES.remove(ip_to_remove)
                        debug_print("Removed " + ip_to_remove + "from list")
            else:
                data = data.split(';')
                for address in data:
                    if address != MY_ADDR:
                        ADDRESSES.append(address)
                        debug_print("Received new connection from: " + address)

        for socket in wlist:
            current_time = int(time.time())
            if current_time - init_time >= 30:
                init_time = current_time
                # socket.send(create_files_message())
        time.sleep(0.001)
