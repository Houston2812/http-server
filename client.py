import socket
import os
import argparse
import ipaddress
from util import TestErrorCode
#TODO import necessary library


HTTP_PORT = 20080
BUF_SIZE = 4096

parser = argparse.ArgumentParser()
parser.add_argument(dest="server_ip",action='store', help='server ip address')
args = parser.parse_args()


def main():
    try:
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        return TestErrorCode.TEST_ERROR_HTTP_CONNECT_FAILED

    try:
        ipaddress.ip_address(args.server_ip)
    except ValueError:
        print("ip address is invalid, ", args.server_ip)

    try:
        clientSock.connect((args.server_ip, HTTP_PORT))
    except socket.error as e:
        return TestErrorCode.TEST_ERROR_HTTP_CONNECT_FAILED
    clientSock.setblocking(0)

    #TODO: send HTTP requests

if __name__ == '__main__':
    main()
