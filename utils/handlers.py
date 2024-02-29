import re
import os

from utils.http_header import *
from utils.logger import logger
from utils.util import TestErrorCode
from backend.parse_http import serialize_http_response, parse_http_request

BUF_SIZE = 4096

def file_handler(resource: str) -> bool:
    if os.path.isfile(resource):
        return True
    else:
        return False

def filename_handler(filename: str) -> str:
    if filename == "/favicon.ico":
        body = ""
    else:
        if filename[0] == "/":
            filename = "." + filename
        elif filename[0] != "/":
            filename = "./" + filename

    match = "\.[-a-zA-Z0-9@:%_\+.~#&//]*"

    if re.search(match, filename) == None:
        return None
    
    return filename


def data_handler(connection) -> str:
    # receive data of the client
    client_data: bytes = b''

    try:
        while True:
            client_data += connection.recv(BUF_SIZE)
            
            # if 0 bytes received, it means client stopped sending
            if  len(client_data) == 0:
                break
    except BlockingIOError:
        pass

    return client_data.decode()

def resource_handler(uri: str) -> bytes:
    msg = b''
    with open(uri, 'rb') as response_file:
        msg = response_file.read()

    return msg

def get_handler(request: Request, connection, file_descriptor):
    resource = filename_handler(filename=request.HttpURI)
    responses = []

    if resource == None:
        logger.error(f"[!!] Wrong resource provided for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND

    if not file_handler(resource=resource):
        logger.error(f"[!!] File does not exist for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND    
    
    logger.debug(f"[!] Reading URI from {file_descriptor}: {resource}")
    body = resource_handler(resource)

    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=OK, 
        contentType=HTML_MIME, 
        contentLength=str(len(body)), 
        lastModified=None, 
        body=body
    )

    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE

def head_handler(request: Request, connection, file_descriptor):
    resource = filename_handler(filename=request.HttpURI)
    responses = []

    if resource == None:
        logger.error(f"[!!] Wrong resource provided for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND

    if not file_handler(resource=resource):
        logger.error(f"[!!] File does not exist for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND    

    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=OK, 
        contentType=HTML_MIME, 
        contentLength=None, 
        lastModified=None, 
        body=b''
    )
    
    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE


def error_404_handler(connection):
    responses = []

    body = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Document</title>
            </head>
            <body>
                <h1>404 Not Found</h1>
            </body>
            </html>
        """.encode()
    
    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=NOT_FOUND, 
        contentType=HTML_MIME, 
        contentLength=str(len(body)), 
        lastModified=None, 
        body=body
        )

    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE

def error_400_handler(connection):
    responses = []

    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=BAD_REQUEST, 
        contentType=HTML_MIME, 
        contentLength=None, 
        lastModified=None, 
        body=b""
        )

    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE
