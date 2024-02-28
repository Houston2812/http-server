import os
import sys
import time
import socket
import select
import argparse
# TODO: Import necessary library

from backend.parse_http import serialize_http_response
from http_header import OK, NOT_FOUND, BAD_REQUEST, SERVICE_UNAVAILABLE
from http_header import HTML_MIME

BUF_SIZE = 4096
HTTP_PORT = 20080


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="www_folder",action='store', help='www folder')
    args = parser.parse_args()
    
    wwwFolder = args.www_folder
    if not os.path.exists(wwwFolder):
        print("Unable to open www folder ", wwwFolder)
        sys.exit(os.EX_OSFILE)
    
    serverSock = socket.socket()
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind(('0.0.0.0', HTTP_PORT))
    serverSock.listen(1)
    
    serverSock.setblocking(0)
    server_file_descriptior = serverSock.fileno()

    print(f"[+] Server started: {server_file_descriptior}")

    # create epoll object
    epoll = select.epoll()

    # register server to epoll
    epoll.register(server_file_descriptior, select.EPOLLIN)

    print("[+] Epoll object registered")
    
    # dictionary of connected clients
    connections = {}
    # dictionary of the received data
    requests = {}
    # dictionary of the data that should be sent back
    responses = {}

    # start time of connection
    start = time.perf_counter()

    while True:
        events = epoll.poll(1)

        for file_descriptior, event in events:

            if file_descriptior == server_file_descriptior:
                
                # accept incoming client connection
                connection, address = serverSock.accept()

                # set socket mode to non-blocking
                connection.setblocking(0)

                # register client in epoll 
                client_file_descriptor = connection.fileno()
                epoll.register(client_file_descriptor, select.EPOLLIN)

                # cache the file descriptor of client
                connections[client_file_descriptor] = connection
                requests[client_file_descriptor] = ''
                responses[client_file_descriptor] = []

                print(f"[+] Client connected: {client_file_descriptor}")

            elif event & select.EPOLLIN:

                # receive data of the client
                client_data = b''

                try:
                    while True:
                        client_data += connections[file_descriptior].recv(BUF_SIZE)
                        
                        # if 0 bytes received, it means client stopped sending
                        if  len(client_data) == 0:
                            break
                except BlockingIOError:
                    pass
                
                # modify the state of client based on whether data was received or not
                if len(client_data) != 0:
                    print(f"[<] Receiving from: {file_descriptior}")
                    requests[file_descriptior] = client_data

                    msg = ''
                    with open("www/test_single/index.html") as response_file:
                        msg = response_file.read()

                    serialize_http_response(msgLst=responses[file_descriptior], prepopulatedHeaders=OK, contentType=HTML_MIME, contentLength=str(len(msg)), lastModified=None, body=msg.encode())
                    # serialize_http_response(responses[file_descriptior], OK, HTML_MIME, contentLength=len(msg), body=msg)

                    print(f"[!] Response message: {responses[file_descriptior]}")

                    epoll.modify(file_descriptior, select.EPOLLOUT)
                else:
                    epoll.modify(file_descriptior, select.EPOLLHUP) 
            
            elif event & select.EPOLLOUT:
                
                # reply to the client
                byteswritten = connections[file_descriptior].send(responses[file_descriptior][0])
                responses[file_descriptior] = responses[file_descriptior][byteswritten:]
                
                print(f"[>] Replying to: {file_descriptior}")
                
                # reset the state of client to the EPOLLIN
                epoll.modify(file_descriptior, select.EPOLLIN) 

            
if __name__ == '__main__':
    main()
