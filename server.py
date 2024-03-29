import os
import sys
import time
import socket
import select
import argparse
import cProfile

from utils.http_header import *
from utils.logger import logger
from backend.connection import Connection
from backend.parse_http import parse_http_request
from utils.handlers import get_handler, head_handler, post_handler, data_handler, cache_handler, error_404_handler, error_400_handler, error_503_handler

BUF_SIZE = 4096 * 100
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

    while True:
        events = epoll.poll(1)

        if len(connections):
            
            # check if the existing connection timed out
            # timeout occurs after a minute if the connection has nothing to send to the client
            # close all connections that timed out
            fds = []
            for key, conn in connections.items():
                if not conn.check_timeout():     
                    logger.warning(f"Remaining requests/response: {len(conn.requests)}/{len(conn.responses)}")   

                    epoll.unregister(conn.file_descriptor) 
                    conn.connection.close()
                    fds.append(conn.file_descriptor)
            
            # clear cache 
            cache_handler()

            # remove connections from the dictionary
            for fd in fds:
                del connections[fd]        
                logger.warning(f"[-] Unregistered: {fd:6}")

        for file_descriptor, event in events:

            if file_descriptor == server_file_descriptior:
                
                # accept incoming client connection
                connection, address = serverSock.accept()
                
                # set socket mode to non-blocking
                connection.setblocking(0)

                connection.setsockopt( 
                    socket.SOL_SOCKET, 
                    socket.SO_SNDBUF, 
                    BUF_SIZE) 
                connection.setsockopt( 
                    socket.SOL_SOCKET, 
                    socket.SO_RCVBUF, 
                    BUF_SIZE)

                # register client in epoll 
                client_file_descriptor = connection.fileno()
                epoll.register(client_file_descriptor, select.EPOLLIN)

                # create connection handler
                connections[client_file_descriptor] = Connection(connection=connection, file_descriptor=client_file_descriptor)

                logger.info(f"[+] Client connected: {client_file_descriptor}")

            elif event & select.EPOLLIN:

                # receive data of the client
                client_data = data_handler(connection=connections[file_descriptor].connection)

                # check if the received connection partial or not
                # append the incoming data if the request is partial
                if connections[file_descriptor].partial_request != '':
                    client_data = connections[file_descriptor].partial_request + client_data
                    connections[file_descriptor].partial_request = ''
                
                # modify the state of client based on whether data was received or not
                if len(client_data) != 0:
                    logger.info(f"[<] Receiving from: {file_descriptor}")
                    logger.debug(f"[!] Parsing incoming HTTP request from: {file_descriptor}")

                    # parse incoming request
                    request = Request()
                    error = parse_http_request(client_data, size=len(client_data), request=request)
                    
                    request.HttpURI = "www" + request.HttpURI
                    
                    logger.info(f"[!] Request from {file_descriptor}: {request}")
                    logger.debug(f"[!] Error: {error}")
                    
                    # if the incoming request was identified as partial by parser, store the received part and wait for the next chunk
                    if error == TestErrorCode.TEST_ERROR_PARSE_PARTIAL:
                        connections[file_descriptor].partial_request += client_data
                        logger.warning(f"[...] Partial request from {file_descriptor}")
                        continue
                    
                    # if the request was parsed succesfully store the request
                    connections[file_descriptor].add_request(request)

                    # if number of clients exceeds 100
                    # Send ERROR 503 Service Unavailable 
                    if len(connections.keys()) > 100:
                        logger.error(f"[-] Error 503 Service Unavailable for {file_descriptor}")

                        # generate ERROR 503 request 
                        error = error_503_handler(connection=connections[file_descriptor])

                        # modify epoll state if response is generated successfully 
                        if error == TestErrorCode.TEST_ERROR_NONE:
                            epoll.modify(file_descriptor, select.EPOLLOUT)
                            continue

                    # check if the request is malformed
                    # send ERROR 400 Bad Request     
                    elif error == TestErrorCode.TEST_ERROR_PARSE_FAILED or request.Valid == False:
                        logger.warning(f"[-] Error 400 Bad Request for {file_descriptor}")

                        # generate ERROR 400 request 
                        error = error_400_handler(connection=connections[file_descriptor])

                        # modify epoll state if response is generated successfully 
                        if error == TestErrorCode.TEST_ERROR_NONE:
                            epoll.modify(file_descriptor, select.EPOLLOUT)
                    
                    # if request is formatted correctly handle the respective method
                    elif error == TestErrorCode.TEST_ERROR_NONE:
                      
                        logger.debug(f"[!] Request from {file_descriptor}")

                        # handle GET request
                        if request.HttpMethod == GET:
                            logger.info(f"[+] GET request from {file_descriptor}")

                            # generate GET request
                            error = get_handler(request=request, connection=connections[file_descriptor], file_descriptor=file_descriptor)

                            # if client requested wrong resource reply with ERROR 404 Not Found
                            if error == TestErrorCode.TEST_ERROR_FILE_NOT_FOUND:
                                logger.warning(f"[-] Error 404 Not Found for {file_descriptor}")

                                # generate ERROR 404 request 
                                error = error_404_handler(connection=connections[file_descriptor])
                                             
                            # modify epoll state if response is generated successfully 
                            if error == TestErrorCode.TEST_ERROR_NONE:
                                epoll.modify(file_descriptor, select.EPOLLOUT)
                        
                        # handle HEAD request
                        elif request.HttpMethod == HEAD:
                            logger.info(f"[+] HEAD request from {file_descriptor}")

                            # generate HEAD request
                            error = head_handler(request=request, connection=connections[file_descriptor], file_descriptor=file_descriptor)

                            # if client requested wrong resource reply with ERROR 404 Not Found
                            if error == TestErrorCode.TEST_ERROR_FILE_NOT_FOUND:
                                logger.warning(f"[-] Error 404 Not Found for {file_descriptor}")

                                # generate ERROR 404 request 
                                error = error_404_handler(connection=connections[file_descriptor])

                            # modify epoll state if response is generated successfully 
                            if error == TestErrorCode.TEST_ERROR_NONE:
                                epoll.modify(file_descriptor, select.EPOLLOUT)
                        
                        # handle POST request
                        elif request.HttpMethod == POST:
                            logger.info(f"[+] POST request from {file_descriptor}")

                            # generate POST request
                            error = post_handler(request=request, connection=connections[file_descriptor], file_descriptor=file_descriptor)

                            # if client request body is wrong reply with ERROR 404 Not Found
                            if error == TestErrorCode.TEST_ERROR_FILE_NOT_FOUND:
                                logger.warning(f"[-] Error 404 Not Found for {file_descriptor}")

                                # generate ERROR 404 request 
                                error = error_404_handler(connection=connections[file_descriptor])
                                
                            # modify epoll state if response is generated successfully 
                            if error == TestErrorCode.TEST_ERROR_NONE:
                                epoll.modify(file_descriptor, select.EPOLLOUT)
                        
                else:
                    epoll.modify(file_descriptor, select.EPOLLHUP) 
            
            elif event & select.EPOLLOUT:
                
                # reply to the client
                response = connections[file_descriptor].get_response()
                
                # send response 
                logger.debug(f"Response: {response}")
                byteswritten = connections[file_descriptor].connection.send(response)
                response = response[byteswritten:]
                connections[file_descriptor].set_response(response)
                logger.info(f"Respons byteswritten: {byteswritten}")

                
                if len(response) == 0:
                    logger.info(f"[>] Replied to: {file_descriptor}")

                    logger.debug(f"[!] Requests: {len(connections[file_descriptor].requests)}")
                    logger.debug(f"[!] Responses: {len(connections[file_descriptor].responses)}")

                    # remove request and respective response
                    connections[file_descriptor].remove_response()    
                    connections[file_descriptor].remove_request()

                    logger.debug(f"[!] Requests: {len(connections[file_descriptor].requests)}")
                    logger.debug(f"[!] Responses: {len(connections[file_descriptor].responses)}")
                                    
                    logger.info(f"[+] Removed request/response")

                    # modify epoll state when response was sent
                    epoll.modify(file_descriptor, select.EPOLLIN) 

            
if __name__ == '__main__':
    main()
