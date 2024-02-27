import ply.yacc as yacc
import ply.lex as lex

from http_header import Request, SUCCESS
# Get the token map from the lexer
from httplex import tokens

# global variables
parsingRequest = None
return_val = [-1] 
def set_parsing_options(request, ret):
    global parsingRequest
    global return_val
    parsingRequest = request
    return_val = ret

start = 'request'

def p_term_assignment(p):
    '''upalpha  : UPALPHA 
                | UPHEX
       loalpha  : LOALPHA 
                | LOHEX
       alpha    : upalpha 
                | loalpha
       alphanum : alpha 
                | DIGIT
       ctl      : CTL 
                | CR 
                | LF 
                | HT
       spht     : SP 
                | HT
       revsep   : COLON 
                | QUESTION 
                | AT 
                | SEMICOLON 
                | EQUAL 
                | COMMA 
                | SLASH
       separators : SEPARATORS 
                  | SLASH
                  | spht 
                  | revsep 
                  | MARKSEP
       revtoken : PLUS 
                | AMPERSAND 
                | DOLLAR
       marktoken : MARKTOKEN 
                 | DOT 
                 | ASTERISK 
                 | MINUS
       tokenchar : TOKEN 
                 | alphanum 
                 | revtoken 
                 | marktoken 
                 | PERCENT
       textchar : TEXT 
                | tokenchar 
                | CR 
                | LF 
                | separators
       octet : textchar 
             | ctl''' 
    p[0] = p[1]

def p_term_crlf(p):
    'crlf : CR LF'
    p[0] = '\r\n'

def p_term_token(p):
    '''token : tokenchar
             | token tokenchar'''
    if (len(p) == 2):
        p[0] = p[1]
    elif (len(p) == 3):
        p[0] = p[1] + p[2] 

def p_term_text(p):
    '''text : textchar
            | text textchar'''
    if (len(p) == 2):
        p[0] = p[1]
    elif (len(p) == 3):
        p[0] = p[1] + p[2]

def p_expression_fieldvaluepart(p):
    '''fieldvaluepart : octet
                      | spht'''
    if (len(p) == 2):
        p[0] = p[1]

def p_expression_fieldvalue(p):
    '''fieldvalue : fieldvaluepart
                  | fieldvalue fieldvaluepart'''
    if (len(p) == 2):
        p[0] = p[1]
    if (len(p) == 3):
        p[0] = p[1] + p[2]

def p_expression_requestheaderpart(p):
    '''requestheaderpart : token COLON fieldvalue crlf
                         | token COLON crlf'''
    global parsingRequest
    if (len(p) == 5):
        parsingRequest.headers[p[1]] = p[3].strip()

        parsingRequest.StatusHeaderSize += len(p[1]) + 1 + len(p[3].strip()) + 2
    elif (len(p) == 4):
        parsingRequest.headers[p[1]] = ""

        parsingRequest.StatusHeaderSize += len(p[1]) + 1 + 2
    if (p[1] == "Host"):
        parsingRequest.Host = p[3].strip()

def p_expression_requestheader(p):
    '''requestheader : requestheaderpart
                     | requestheader requestheaderpart'''
    pass

def p_expression_httpversion(p):
    'httpversion : token SLASH DIGIT DOT DIGIT'
    if p[1] == 'HTTP':
        p[0] = p[1]+p[2]+p[3]+p[4]+p[5]
    else:
        p[0] = 0

def p_expression_requestline(p):
    '''requestline : token SP text SP httpversion crlf'''
    global parsingRequest
    parsingRequest.HttpMethod = p[1]
    parsingRequest.HttpURI = p[3]
    parsingRequest.HttpVersion = p[5]
    parsingRequest.StatusHeaderSize += len(p[1]) + 1 + len(p[3]) + 1 + len(p[5]) + 2

def p_expression_request(p):
    '''request : requestline requestheader crlf
               | requestline crlf'''
    global parsingRequest
    global return_val
    parsingRequest.StatusHeaderSize += 2
    return_val[0] = SUCCESS


# Error rule for syntax errors
def p_error(p):
    return_val[0] = -1

parser = yacc.yacc(write_tables=False, debug=False)
