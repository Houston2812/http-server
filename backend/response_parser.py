import ply.yacc as yacc
import ply.lex as lex

from http_header import Response, SUCCESS
from httplex import tokens

# global variables
parsingResponse = None 
return_val = [-1]
def set_parsing_options(response, ret):
    global parsingResponse
    global return_val
    parsingResponse = response
    return_val = ret

start="response"

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
       phrasechar : TEXT
                  | tokenchar
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


def p_term_phrase(p):
    '''phrase : phrasechar
              | phrase phrasechar'''
    if (len(p) == 2):
        p[0] = p[1]
    elif(len(p) == 3):
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

def p_expression_responseheaderpart(p):
    '''responseheaderpart : token COLON fieldvalue crlf
                         | token COLON crlf'''
    global parsingResponse
    if (len(p) == 5):
        parsingResponse.headers[p[1]] = p[3].strip()
    elif (len(p) == 4):
        parsingResponse.headers[p[1]] = ""


def p_expression_responseheader(p):
    '''responseheader : responseheaderpart
                     | responseheader responseheaderpart'''
    pass

def p_expression_httpversion(p):
    'httpversion : token SLASH DIGIT DOT DIGIT'
    if p[1] == 'HTTP':
        p[0] = p[1]+p[2]+p[3]+p[4]+p[5]
    else:
        p[0] = 0

def p_expression_statuscode(p):
    'statuscode : DIGIT DIGIT DIGIT'
    p[0] = p[1] + p[2] + p[3]


def p_expression_statusline(p):
    'statusline : httpversion SP statuscode SP phrase crlf'
    global parsingResponse
    parsingResponse.HttpVersion = p[1]
    parsingResponse.StatusCode = p[3]
    parsingResponse.ReasonPhrase = p[5]

def p_expression_response(p):
    '''response : statusline responseheader crlf
                | statusline crlf'''
    global return_val
    return_val[0] = SUCCESS

# Error rule for syntax errors
def p_error(p):
    global return_val
    return_val[0] = -1

parser = yacc.yacc(write_tables=False, debug=False)
