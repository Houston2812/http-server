from backend import parser as Parser
# from backend import response_parser as Rparser
from enum import Enum
from datetime import datetime
from utils.http_header import Request, SUCCESS, HTTP_SIZE, HTTP_VER, CRLF, CONNECTION, HOST, CONNECTION_VAL, SERVER, SERVER_VAL, DATE, CONTENT_TYPE, CONTENT_LENGTH, ZERO, LAST_MODIFIED
from utils.util import TestErrorCode
import copy

class State(Enum):
    STATE_START = 0
    STATE_CR = 1
    STATE_CRLF = 2
    STATE_CRLFCR = 3
    STATE_CRLFCRLF = 4

def parse_http_request(inbuf, size, request):
    '''
        Parse an HTTP request form a buffer to a Request object.

        :param inbuf: The input buffer
        :type: string
        :param size: The size of inbuf
        :type: int
        :param request: The output Request object
        :type: Reqeust
	'''
    
    i = 0
    buf = ''
    ret = [-1]
    state = State.STATE_START

    while (state != State.STATE_CRLFCRLF):
        expected = None

        if i == size:
            break

        ch = inbuf[i]
        buf += ch 
        i += 1

        if (state == State.STATE_START or state == State.STATE_CRLF):
            expected = '\r';

        elif (state == State.STATE_CR or state == State.STATE_CRLFCR):
            expected = '\n'
    
        else:
            state = State.STATE_START
            continue

        if (ch == expected):
            state = State(state.value + 1)

        else:
            state = State.STATE_START

    if (state == State.STATE_CRLFCRLF):
        Parser.set_parsing_options(request, ret) 
        Parser.parser.parse(buf)
        if (ret[0] == SUCCESS):
            request.Valid = True
            request.headers = copy.deepcopy(request.headers)
            return TestErrorCode.TEST_ERROR_NONE
        return TestErrorCode.TEST_ERROR_PARSE_FAILED

    return TestErrorCode.TEST_ERROR_PARSE_PARTIAL 

def serialize_http_request(msgLst, request):
    '''
	Serialize an HTTP request from a Request to buffer

    :param msgLst: The output message list
    :type: list
    :param request: The input Request object
    :type: Reqeust
	'''
    msg = b''
    if (request.HttpMethod != "GET"):
        return TestErrorCode.TEST_ERROR_PARSE_FAILED

    msg += request.HttpMethod.encode() + ' '.encode() + request.HttpURI.encode() + ' '.encode() + HTTP_VER.encode() + CRLF.encode()
    msg += HOST.encode() + request.Host.encode() + CRLF.encode()
    msg += CONNECTION.encode() + CONNECTION_VAL.encode() + CRLF.encode() + CRLF.encode()

    msgLst.append(msg)

    return TestErrorCode.TEST_ERROR_NONE

def serialize_http_response(msgLst, prepopulatedHeaders, contentType, contentLength, lastModified, body):
    '''
	Serialize an HTTP response from Request to buffer

    :param msgLst: The output message list
    :type: list
    :param prepopulatedHeaders: The prepopulated headers (input) 
    :type: string
	:param contentType: The content type (input)
	:type: string
	:param contentLength: The content length (input)
	:type: string
	:param lastModified: The last modified time (input)
	:type: string
	:param body: The HTTP body (input)
	:type: string
	'''
    currentDateAndTime = datetime.now()
    currentTime = currentDateAndTime.strftime("%a, %d %b %Y %H:%M:%S GMT")
    dateLen = len(currentTime)
    bodyLen = len(body)
    contentTypeLen = 0 if contentType is None else len(contentType)
    contentLengthLen = 0 if contentLength is None else len(contentLength)
    lastModifiedLen = 0 if lastModified is None else len(lastModified)
    msg = b'' 
    
    # prepopulated
    msg += HTTP_VER.encode() + b' '
    msg += prepopulatedHeaders.encode()
    msg += CONNECTION.encode() + CONNECTION_VAL.encode() + CRLF.encode()
    msg += SERVER.encode() + SERVER_VAL.encode() + CRLF.encode()
    msg += DATE.encode()+ currentTime.encode() + CRLF.encode()
    if (contentType is not None):
        msg += CONTENT_TYPE.encode() + contentType.encode() + CRLF.encode()
    if (contentLength is not None):
        msg += CONTENT_LENGTH.encode() + contentLength.encode() + CRLF.encode()
    else:
        msg += CONTENT_LENGTH.encode() + ZERO.encode() + CRLF.encode()
    if (lastModified is not None):
        msg += LAST_MODIFIED.encode() + lastModified.encode() + CRLF.encode()
    msg += CRLF.encode()

    if (body is not None):
        msg += body
    msgLst.append(msg)
        
    return TestErrorCode.TEST_ERROR_NONE 

