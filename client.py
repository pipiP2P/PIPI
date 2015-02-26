import socket
import select
import time
from threading import Thread
from File import *
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


def create_files_message():
    string_list = []
    for cur_file in MY_FILES:
        string_list.append(cur_file.to_string())
    return '$'.join(string_list)


def send_search_answer_true(file_found, client_socket):
    reply_message = [FILE_RESPONSE, '1', file_found.get_hash(), file_found.get_num_of_parts(), file_found.get_size()]
    client_socket.send(';'.join(reply_message))
    print "We have found this hash " + file_found.get_hash()


def send_search_answer_false(requested_hash, client_socket):
    print "We didn't have this hash in our file library:" + requested_hash
    reply_message = [FILE_RESPONSE, '0', '0', '0', '0']
    client_socket.send(';'.join(reply_message))
    
def file_exists(file_hash):
    all_files = get_all_files()
    for current_file in all_files:
        if current_file.get_hash() == file_hash:
            # We found the file
            return current_file
    return False
def question_file_exists(file_hash, client_socket):
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
                        print all_list[0]
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
                                    print "We have this part!"
            except:
                print "[-] Error trying to analyse or send info"
    time.sleep(0.001)

client_socket = socket.socket()
client_socket.connect(('10.10.10.22', 50000))
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('', UDP_PORT))
thread = Thread(target=udp_connection_handler, args=[])
thread.start()
while True:
    rlist, wlist, xlist = select.select([client_socket], [client_socket], [])
    for current_socket in rlist:
        data = current_socket.recv(1024)
        if data.startswith("ping"):
            print "Received ping, sending back PONG"
            add_files(data[4:len(data)-1])
            current_socket.send("pong")
            
        elif data.startswith("remove "):
            ip_to_remove = data.split(' ')
            if len(ip_to_remove) == 2:
                ip_to_remove = ip_to_remove[1]
                if ip_to_remove in ADDRESSES:
                    ADDRESSES.remove(ip_to_remove)
                    print "Removed " + ip_to_remove + "from list"
        else:
            data = data.split(';')
            for address in data:
                if address != MY_ADDR:
                    ADDRESSES.append(address)
                    print "Received new connection from: " + address

    for socket in wlist:
        current_time = int(time.time())
        if current_time - init_time >= 30:
            init_time = current_time
            socket.send(create_files_message())
    time.sleep(0.001)
