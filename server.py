import os
import sys
import time
import socket
import select
import argparse

from utils.logger import logger
from utils.http_header import *
from utils.handlers import get_handler, data_handler, resource_handler
from backend.parse_http import serialize_http_response, parse_http_request

BUF_SIZE = 4096
HTTP_PORT = 20080

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="www_folder",action='store', help='www folder')
    args = parser.parse_args()
    
    wwwFolder = args.www_folder
    if not os.path.exists(wwwFolder):
        logger.warning("[!!] Unable to open www folder ", wwwFolder)
        sys.exit(os.EX_OSFILE)
    
    serverSock = socket.socket()
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind(('0.0.0.0', HTTP_PORT))
    serverSock.listen(1)
    
    serverSock.setblocking(0)
    server_file_descriptior = serverSock.fileno()

    logger.info(f"[+] Server started: {server_file_descriptior}")

    # create epoll object
    epoll = select.epoll()

    # register server to epoll
    epoll.register(server_file_descriptior, select.EPOLLIN)

    logger.info("[+] Epoll object registered")
    
    # dictionary of connected clients
    connections = {}
    # dictionary of the received data
    requests = {}
    # dictionary of the data that should be sent back
    responses = {}

    while True:
        events = epoll.poll(1)

        for file_descriptor, event in events:

            if file_descriptor == server_file_descriptior:
                
                # accept incoming client connection
                connection, address = serverSock.accept()

                # set socket mode to non-blocking
                connection.setblocking(0)

                # register client in epoll 
                client_file_descriptor = connection.fileno()
                epoll.register(client_file_descriptor, select.EPOLLIN)

                # cache the file descriptor of client
                connections[client_file_descriptor] = connection
                requests[client_file_descriptor] = []
                responses[client_file_descriptor] = []

                logger.info(f"[+] Client connected: {client_file_descriptor}")

            elif event & select.EPOLLIN:

                # receive data of the client
                client_data = data_handler(connections=connections, file_descriptor=file_descriptor)

                # modify the state of client based on whether data was received or not
                if len(client_data) != 0:
                    logger.info(f"[<] Receiving from: {file_descriptor}")

                    logger.debug(f"[!] Parsing incoming HTTP request from: {file_descriptor}")

                    request = Request()
                    error = parse_http_request(client_data, size=len(client_data), request=request)
                    
                    requests[file_descriptor].append(request)
                    
                    logger.debug(f"[!] Request from {file_descriptor}: {requests[file_descriptor]}")

                    if error == TestErrorCode.TEST_ERROR_NONE:
                        if request.HttpMethod == GET:
                            get_handler(request, responses, file_descriptor)
                            resource = request.HttpURI

                            if resource == "/favicon.ico":
                                continue

                            resource = "." + resource

                            logger.debug(f"[!] Reading URI from {file_descriptor}: {resource}")
                            body = resource_handler(resource)

                            serialize_http_response(
                                msgLst=responses[file_descriptor], 
                                prepopulatedHeaders=OK, 
                                contentType=HTML_MIME, 
                                contentLength=str(len(body)), 
                                lastModified=None, 
                                body=body
                                )

                    epoll.modify(file_descriptor, select.EPOLLOUT)
                else:
                    epoll.modify(file_descriptor, select.EPOLLHUP) 
            
            elif event & select.EPOLLOUT:
                
                # reply to the client
                byteswritten = connections[file_descriptor].send(responses[file_descriptor][0])
                responses[file_descriptor] = responses[file_descriptor][byteswritten:]
                
                logger.info(f"[>] Replying to: {file_descriptor}")
                
                # reset the state of client to the EPOLLIN
                epoll.modify(file_descriptor, select.EPOLLIN) 

            
if __name__ == '__main__':
    main()
