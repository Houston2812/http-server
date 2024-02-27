from util import TestErrorCode

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

