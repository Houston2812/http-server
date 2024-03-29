import re
import os

from utils.http_header import *
from utils.logger import logger
from utils.util import TestErrorCode
from backend.parse_http import serialize_http_response, parse_http_request

BUF_SIZE = 4096

# cache to store the recently read files
cache = {}

# handler to clear cache
def cache_handler():
    global cache
    cache.clear()
    
# handler to check if file exists
def file_handler(resource: str) -> bool:
    if os.path.isfile(resource):
        return True
    else:
        return False

# handler to clean up the request URI
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

# handler to receive incoming data
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

# handler to read requested file
def resource_handler(uri: str) -> bytes:
    body = b""
    global cache
    if uri in cache.keys():
       body = cache[uri] 
    else:
        with open(uri, 'rb') as response_file:
            msgs = response_file.readlines()
            for msg in msgs:
                body += msg
        
        # save file to the cache
        print(len(body))
        cache[uri] = body

    return body

# post body handler to check if it is correctly formatted

def body_handler(body: str) -> bytes:
    parts = re.split("&|=", body)
    if len(parts) > 1:
        return body.encode()
    elif len(parts) == 1 and parts[0] != body:
        return body.encode()
    else:
        # return empty if request body is wrongly wormatted
        return None
    
# get handler
def get_handler(request: Request, connection, file_descriptor):
    
    # check resource
    resource = filename_handler(filename=request.HttpURI)
    responses = []

    # reply with FILE NOT FOUND exist if file does not exist
    if resource == None:
        logger.error(f"[!!] Wrong resource provided for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND

    # reply with FILE NOT FOUND exist if file does not exist
    if not file_handler(resource=resource):
        logger.error(f"[!!] File does not exist for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND    
    
    # read resource
    logger.debug(f"[!] Reading URI from {file_descriptor}: {resource}")
    body = resource_handler(resource)

    # serialize response
    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=OK, 
        contentType=HTML_MIME, 
        contentLength=str(len(body)), 
        lastModified=None, 
        body=body
    )

    # add response to the queue in the connection
    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE

# head handler
def head_handler(request: Request, connection, file_descriptor):

    # check resource
    resource = filename_handler(filename=request.HttpURI)
    responses = []

    # reply with FILE NOT FOUND exist if file does not exist
    if resource == None:
        logger.error(f"[!!] Wrong resource provided for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND

    # reply with FILE NOT FOUND exist if file does not exist
    if not file_handler(resource=resource):
        logger.error(f"[!!] File does not exist for {file_descriptor}: {resource}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND    

    body = resource_handler(resource)

    # serialize response
    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=OK, 
        contentType=HTML_MIME, 
        contentLength=str(len(body)), 
        lastModified=None, 
        body=b''
    )
    
    # add response to the queue in the connection
    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE

# post handler
def post_handler(request: Request, connection, file_descriptor):
    
    responses = []

    body = request.HttpBody
    body = body.encode()

    # reply with FILE NOT FOUND exist if body is wrongly formatted
    if body == None:
        logger.error(f"[!!] Wrong body provided for {file_descriptor}: {body}")
        return TestErrorCode.TEST_ERROR_FILE_NOT_FOUND
    
    # serialize response 
    serialize_http_response(
        msgLst=responses,
        prepopulatedHeaders=OK,
        contentType=OCTET_MIME,
        contentLength=request.headers['Content-Length'],
        lastModified=None,
        body=body
    )

    # add response to the queue in the connection
    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE

# error 400 handler
def error_400_handler(connection):
    responses = []

    # serialize response 
    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=BAD_REQUEST, 
        contentType=HTML_MIME, 
        contentLength=None, 
        lastModified=None, 
        body=b""
        )

    # add response to the queue in the connection
    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE

# error 404 handler
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
    
    # serialize response 
    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=NOT_FOUND, 
        contentType=HTML_MIME, 
        contentLength=str(len(body)), 
        lastModified=None, 
        body=body
        )

    # add response to the queue in the connection
    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE

# error 503 handler
def error_503_handler(connection):
    responses = []

    # serialize response
    serialize_http_response(
        msgLst=responses, 
        prepopulatedHeaders=SERVICE_UNAVAILABLE, 
        contentType=HTML_MIME, 
        contentLength=None, 
        lastModified=None, 
        body=b""
        )

    # add response to the queue in the connection
    connection.add_response(responses)

    return TestErrorCode.TEST_ERROR_NONE
