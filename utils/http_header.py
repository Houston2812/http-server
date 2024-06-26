from utils.util import TestErrorCode

SUCCESS = 0
HTTP_SIZE = 4096

# HTTP Methods
HEAD = "HEAD"
GET = "GET"
POST = "POST"

# Request Headers
CONTENT_LENGTH_STR = "content-length"
CONNECTION_STR = "connection"
CLOSE = "close"

# Response Headers
CRLF = "\r\n"
CONNECTION = "Connection:"
CONNECTION_VAL = "Keep-Alive"
SERVER = "Server: "
SERVER_VAL = "case/1.0"
DATE = "Date: "
CONTENT_TYPE = "Content-Type: "
CONTENT_LENGTH = "Content-Length: "
ZERO = "0"
LAST_MODIFIED = "Last-Modified: "
HOST = "Host: "

# Responses
HTTP_VER = "HTTP/1.1"
OK = "200 OK\r\n"
NOT_FOUND = "404 Not Found\r\n"
SERVICE_UNAVAILABLE = "503 Service Unavailable\r\n"
BAD_REQUEST = "400 Bad Request\r\n"

# MIME TYPES
HTML_EXT = "html"
HTML_MIME = "text/html"
CSS_EXT = "css"
CSS_MIME = "text/css"
PNG_EXT = "png"
PNG_MIME = "image/png"
JPG_EXT = "jpg"
JPG_MIME = "image/jpeg"
GIF_EXT = "gif"
GIF_MIME = "image/gif"
OCTET_MIME = "application/octet-stream"


# HTTP Request Header
class Request(object):
    # HTTP version, should be 1.1 in this project
    HttpVersion = ""
    # HTTP method, could be GET, HEAD, or POSt in this project
    HttpMethod = ""
    # HTTP URI, could be /index.html, /index.css, etc.
    HttpURI = ""
    # Host name, should be the IP address
    Host = ""
    # HTTP request headers, could be Content-Length, Connection, etc.
    headers = {}
    # Total header size
    StatusHeaderSize = 0
    # HTTP body, could be the content of the file
    HttpBody = ""
    # Whether the request is valid
    Valid = False
    
    def __init__(self):
        pass

    def __repr__(self) -> str:
        data = f"HTTP Version: {self.HttpVersion}; HTTP Method: {self.HttpMethod}; HTTP Uri: {self.HttpURI}; HTTP Host: {self.Host}; Headers: {self.headers}, HTTP Body: {self.HttpBody};"

        return data
    
    # check request and set self.Valid to False to handle ERROR 400 Bad Request
    def check_request(self):
        # set Valid to false by making an assumption that request is malformedd
        self.Valid = False

        # check HTTP Version
        if self.HttpVersion != HTTP_VER:
            return 
        
        # check HTTP Method
        methods = [GET, POST, HEAD]
        if self.HttpMethod not in methods:
            return 
        
        # check HTTP Headers
        content_types = [HTML_EXT,HTML_MIME,CSS_EXT,CSS_MIME,PNG_EXT,PNG_MIME,JPG_EXT,JPG_MIME,GIF_EXT,GIF_MIME,OCTET_MIME]
        for header, value in self.headers.items():
            # check HTTP Content Types
            if header == "Content-Type":
                if value not in content_types:
                    return 
            
            # check HTTP Connection
            if header == "Connection":
                if not (value.lower() == "keep-alive" or value.lower() == "close"):
                    return 

        # set Valid to true when all checks passed   
        self.Valid = True
        return