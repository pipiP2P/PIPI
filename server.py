import socket
import select
import time
from threading import Thread

addresses = []  # Addresses of all the connected peers
messages_to_send = []
open_client_sockets = []
heartbeat_responses = []  # List of sockets that answered to heartbeat request
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 50000))
server_socket.listen(100)
sockets_and_ips = {}  # List of tuples of IP and socket


def send_message_to_all(content):
    for client in open_client_sockets:
        client.send(content)


def user_disconnected(client_socket):
    for ip in sockets_and_ips.keys():
        if sockets_and_ips[ip] == client_socket:
            print ip, 'Disconnected'
            del sockets_and_ips[ip]
            break
    client_socket.close()
    open_client_sockets.remove(client_socket)
    send_message_to_all("remove " + ip)
    addresses.remove(ip)


def check_for_responses():
    for socket in open_client_sockets:
        if socket not in heartbeat_responses:
            user_disconnected(socket)
        else:
            # The client responded, just delete the heartbeat response from list
            heartbeat_responses.remove(socket)


def send_heartbeat(wlist):
    for client in wlist:
        try:
            client.send("ping")
        except:
            user_disconnected(client)


def start_pinging_till_death():
    while True:
        print "New round of pinging"
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
                        print "Sent data:" + data
                    except:
                        user_disconnected(client_socket)
        messages_to_send.remove(message)

thread = Thread(target=start_pinging_till_death, args=[])
thread.start()
while True:
    rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
    for current_socket in rlist:
        # New connection:
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            open_client_sockets.append(new_socket)
            print "Received new connection " + address[0]
            if address[0] not in addresses:
                addresses.append(address[0])
                sockets_and_ips[address[0]] = new_socket
                heartbeat_responses.append(new_socket)
                messages_to_send.append((current_socket, address[0]))
                wlist.append(new_socket)
            else:
                print "This user already connected to server from the same IP"
                
        else:
            try:
                data = current_socket.recv(4096)
                if data == "":
                    #Remove socket and notify
                    user_disconnected(current_socket)
                elif data == "pong":
                    heartbeat_responses.append(current_socket)
                    print "RECEIVED PONG"
            except:
                # Client connection closed, remove him
                user_disconnected(current_socket)
    send_waiting_messages(wlist)
    time.sleep(0.001)
