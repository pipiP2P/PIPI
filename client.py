import socket
import select
import time
import File

FILES = []
ADDRESSES = []
MY_ADDR = socket.gethostbyname(socket.gethostname())

client_socket = socket.socket()
client_socket.connect(('10.10.10.64', 50000))

while True:
    rlist, wlist, xlist = select.select([client_socket], [client_socket], [])
    for current_socket in rlist:
        data = current_socket.recv(1024)
        if data == "ping":
            print "Received ping, sending back PONG"
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
    time.sleep(0.001)
