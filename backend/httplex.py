import ply.lex as lex

# List of token names
tokens = (
    'UPHEX',
    'LOHEX',
    'UPALPHA',
    'LOALPHA',
    'DIGIT',
    'CR',
    'LF',
    'SP',
    'HT',
    'CTL',
    'SLASH',
    'DOT',
    'COLON',
    'QUESTION',
    'ASTERISK',
    'PERCENT',
    'PLUS',
    'MINUS',
    'AT',
    'SEMICOLON',
    'AMPERSAND',
    'EQUAL',
    'DOLLAR',
    'COMMA',
    'MARKSEP',
    'SEPARATORS',
    'MARKTOKEN',
    'TOKEN',
    'TEXT',
)

# Regular expression rules for simple tokens
t_UPHEX = r'[A-F]'
t_LOHEX = r'[a-f]'
t_UPALPHA = r'[A-Z]'
t_LOALPHA = r'[a-z]'
t_DIGIT = r'[0-9]'
t_CR = r'\x0d'
t_LF = r'\x0a'
t_SP = r'\x20'
t_HT = r'\x09'
t_CTL = r'(?![\x0d\x0a\x09])[\x00-\x1f\x7f]'
t_SLASH = r'\/'
t_DOT = r'\.'
t_COLON = r':'
t_QUESTION = r'\?'
t_ASTERISK = r'\*'
t_PERCENT = r'\%'
t_PLUS = r'\+'
t_MINUS = r'-'
t_AT = r'@'
t_SEMICOLON = r';'
t_AMPERSAND = r'\&'
t_EQUAL = r'='
t_DOLLAR = r'\$'
t_COMMA = r','
t_MARKSEP = r'\(\)'
# "(" | ")" | "<" | ">" | "@" | "," | ";" | ":" | "\" | <"> |  "[" | "]" | "?" | "=" | "{" | "}" 
t_SEPARATORS = r'[\(\)\<\>\,;\\\"\[\]?=\{\}]'
t_MARKTOKEN = r'[\_\!\~\']'
# <any CHAR except CTLs or separators>
t_TOKEN = r'(?![(\(\)\<\>@\,\;:\\\"\/\[\]\?=\{\}\.\x20\x09\x00-\x1f\x7f0-9-\_\!\~\*\'\&])[\x00-\x7f]'
# <any OCTET except CTLs or LWS or separators>
t_TEXT = r'(?![\x00-\x08\x0b-\x0c\x0e-\x1f\x7f\x09\x20\(\)\<\>@\,;:\\\"\/\[\]?=\{\}\.0-9-\_\!\~\*\'\&])[\x80-\xff]'
#t_LWS = r'(\x0d\x0a)?[\x20\x09]+'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

#data = '''
#'''
#
#lexer.input(data)
#
#while True:
#    tok = lexer.token()
#    if not tok:
#        break
#    print(tok)
