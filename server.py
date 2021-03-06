import socket
import select
import time
from threading import Thread
from File import *

addresses = [] # Addresses of all the connected peers
messages_to_send = []
open_client_sockets = []
heartbeat_responses = [] # List of sockets that answered to heartbeat request
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 50000))
server_socket.listen(100)
sockets_and_ips = {} # Dictionary of IP and socket
FILES = []
STRING_FILES = []

def debug_print(dbg_info):
    print dbg_info


def send_message_to_all(content):
    for client in open_client_sockets:
        client.send(content)


def user_disconnected(client_socket):
    for ip in sockets_and_ips.keys():
        if sockets_and_ips[ip] == client_socket:
            debug_print(ip + 'Disconnected')
            del sockets_and_ips[ip]
            break
    client_socket.close()
    open_client_sockets.remove(client_socket)
    send_message_to_all("remove " + ip)
    addresses.remove(ip)


def check_for_responses():
    for socket in open_client_sockets:
        if socket not in heartbeat_responses:
            # User didn't response to our ping
            debug_print("%s hasn't responded to our ping!".format(sockets_and_ips[socket]))
            user_disconnected(socket)
        else:
            # The client responded, just delete the heartbeat response from list
            heartbeat_responses.remove(socket)


def send_heartbeat(wlist):
    for client in wlist:
        try:
            client.send("ping" + '$'.join(STRING_FILES))
        except:
            user_disconnected(client)


def start_pinging_till_death():
    """
    Manages the heartbeat system.
    Sends ping to the connected peers and
    checks after 30 seconds who hasn't responded
    """
    while True:
        debug_print("New round of pinging")
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
        send_heartbeat(wlist)
        time.sleep(30)
        check_for_responses()


def send_waiting_messages(write_list):
    for message in messages_to_send:
        (this_socket, data) = message
        for client_socket in open_client_sockets:
            if client_socket in write_list:
                if client_socket is not this_socket:
                    try:
                        client_socket.send(data)
                        debug_print("Send data:" + data )
                    except:
                        user_disconnected(client_socket)
        messages_to_send.remove(message)


def add_files(files_list):
    files_list = files_list.split('$')
    for cur_file in files_list:
        cur_file = cur_file.split(';')
        if len(cur_file) == 5:
            if ';'.join(cur_file) not in STRING_FILES:
                STRING_FILES.append(';'.join(cur_file))
                FILES.append(File_Info(cur_file[0], cur_file[1], cur_file[2], cur_file[3], cur_file[4]))


thread = Thread(target=start_pinging_till_death, args=[])
thread.start()
while True:
    rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
    for current_socket in rlist:
        # New connection:
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            open_client_sockets.append(new_socket)
            debug_print("Received new connection " + address[0])
            if address[0] not in addresses:
                # We have a unique connection
                new_socket.send(';'.join(addresses))  # Send the connected socket the other peers IPs
                addresses.append(address[0])  # Add his address to the connected peers
                sockets_and_ips[address[0]] = new_socket  # Add him to the socket-IP dictionary
                heartbeat_responses.append(new_socket)
                messages_to_send.append((current_socket, address[0]))  # Send everyone that the user connected
                wlist.append(new_socket)
            else:
                debug_print("This user already connected to server from the same IP")
                
        else:
            try:
                data = current_socket.recv(4096)
                if data == "":
                    #Remove socket and notify
                    user_disconnected(current_socket)

                elif data == "pong":  ###################################### change to startswith ############
                    heartbeat_responses.append(current_socket)
                    debug_print("Received pong from: " + sockets_and_ips[current_socket])
            except:
                # Client connection closed, remove him
                user_disconnected(current_socket)

    send_waiting_messages(wlist)
    time.sleep(0.001)
