import os
import sys
import argparse
import socket
# TODO: Import necessary library

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
    serverSock.listen(0)

    #TODO: handle HTTP requests

if __name__ == '__main__':
    main()
