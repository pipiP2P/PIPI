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
time = int(time.time())


def create_files_message():
    string_list = []
    for cur_file in MY_FILES:
        string_list.append(cur_file.to_string())
    return '$'.join(string_list)


def create_files_message():
    string_list = []
    for cur_file in MY_FILES:
        string_list.append(cur_file.to_string())
    return '$'.join(string_list)


def file_exists(file_hash, client_socket):
    files_with_sha1 = get_all_files()
    val = 0
    for current_file in files_with_sha1:
        if current_file[1] == file_hash:
            reply_message = [FILE_RESPONSE, '1', current_file[1], parts_num, str(get_size(current_file[0]))]
            client_socket.send(';'.join(reply_message))
            val = 1
    if val == 0:
        reply_message = [FILE_RESPONSE, '0', '0', '0', '0']
        client_socket.send(';'.join(reply_message))


def udp_connection_handler():
    others_files_with_info = []
    while True:
        rlist, wlist, xlist = select.select([udp_socket], [udp_socket], [])
        for current_socket in rlist:
            try:
                data_received = current_socket.recv(4096)
                if data_received != "":
                    all_list = convert_message(data_received)
                    list_length = len(all_list)
                    if list_length == 2:
                        # Do we have the file?
                        # We will search our special directory to find the file name requested
                        protocol_number, file_hash = all_list
                        file_exists(file_hash, current_socket)
                    elif list_length == 3:
                        protocol_number, file_hash, parts_numbers = all_list
                    elif list_length == 1:
                        print "[-] Received bad data!"
            except:
                print "[-] Error trying to analyse or send info"
    time.sleep(0.001)

client_socket = socket.socket()
client_socket.connect(('10.20.239.230', 50000))
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('', UDP_PORT))
thread = Thread(target=udp_connection_handler, args=[])
thread.start()
while True:
    rlist, wlist, xlist = select.select([client_socket], [client_socket], [])
    for current_socket in rlist:
        data = current_socket.recv(1024)
        if data.stratswith("ping"):
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
        if current_time - time >= 30:
            time = current_time
            socket.send(create_files_message())
    time.sleep(0.001)
