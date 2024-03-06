import os
import sys
import time
import socket
import argparse
import ipaddress

from datetime import datetime
from utils.http_header import *
from utils.logger import logger
from utils.util import TestErrorCode
from backend.parse_http import serialize_http_request

HTTP_PORT = 20080
BUF_SIZE = 4096

parser = argparse.ArgumentParser()
parser.add_argument(dest="server_ip",action='store', help='server ip address')
parser.add_argument(dest="uri",action='store', help='Resource to request')
parser.add_argument(dest="method",action='store',  choices=['GET', 'HEAD', 'POST'], default="GET", help='Method to use')
parser.add_argument("--data", dest="body", action='store', default="", help='Data to send in the body of HTTP request')
parser.add_argument("-p", dest='partial', action=argparse.BooleanOptionalAction, type=bool, help="To simulate partial request. 2 parts with 2s seconds interval are send")
parser.add_argument("-m", dest="multiple", default=1, type=int, action="store", help="Number of requests that will be sent by client without getting response from server")

args = parser.parse_args()


def main():
    try:
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        return TestErrorCode.TEST_ERROR_HTTP_CONNECT_FAILED

    try:
        ipaddress.ip_address(args.server_ip)
    except ValueError:
        logger.error("[!!] IP address is invalid, ", args.server_ip)

    try:
        clientSock.connect((args.server_ip, HTTP_PORT))
    except socket.error as e:
        return TestErrorCode.TEST_ERROR_HTTP_CONNECT_FAILED
    clientSock.setblocking(0)

    requests = []

    request = Request()
    request.HttpVersion = HTTP_VER

    if args.method == "GET":
        request.HttpMethod = GET
        request.headers[CONTENT_TYPE] = HTML_MIME

    elif args.method == "POST":
        request.HttpMethod = POST
        request.HttpBody = args.body
        request.headers[CONTENT_TYPE] = OCTET_MIME
        request.headers[CONTENT_LENGTH] = str(len(args.body))

    elif args.method == "HEAD":
        request.HttpMethod = HEAD
        request.headers[CONTENT_TYPE] = HTML_MIME

    request.HttpURI = args.uri
    request.Host = str(args.server_ip)
    currentDateAndTime = datetime.now()
    currentTime = currentDateAndTime.strftime("%a, %d %b %Y %H:%M:%S GMT")

    request.headers[DATE] = currentTime
    logger.debug(f"[!] Request: {request}")
    error = serialize_http_request(msgLst=requests, request=request)

    logger.error(f"{requests}")
    if error == TestErrorCode.TEST_ERROR_NONE:
        logger.info(f"[<] Requesting {request.HttpURI} from server")
        for msg in requests:
            logger.debug(f"[!] Message: {msg}")  

            for i in range(args.multiple):
                if args.partial:
                    logger.debug(f"[!] Sending partial message")
                    clientSock.send(msg[:len(msg)//2])
                    msg = msg[len(msg)//2:]
                    time.sleep(1)
                    clientSock.send(msg)
                else:
                    clientSock.send(msg)
                
                logger.info(f'[<<] Sent {i+1}th request')
                time.sleep(0.01)
                   
        logger.info(f"[+] Waiting for server to reply")
        server_response = b''
        time.sleep(0.5)
        try:
            while True:
                try:
                    while True:
                        data = clientSock.recv(BUF_SIZE)
                        server_response += data

                        # if 0 bytes received, it means client stopped sending
                        if  len(data) == 0 and server_response != 0:
                            break
                except BlockingIOError:
                    pass
                    
                if len(server_response) != 0:
                    logger.info("[+] Received information from server")
                    logger.debug(f"[>] Received: \n{server_response.decode()}")
                    server_response = b''
        except KeyboardInterrupt:
            logger.info(f"Finished")
            sys.exit()
            
if __name__ == '__main__':
    main()
