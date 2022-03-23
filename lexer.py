from collections import namedtuple
import ply.lex as lex

reserved = {
    'variables': 'VARIABLES',
    'si'       : 'SI',
    'fin'      : 'FIN',
    'entier'   : 'ENTIER',
    'reel'     : 'REEL'
}

# List of token names.   This is always required
tokens = [
   'LIT_NUM',
   'NEWLINE',
   'ID'
] + list(reserved.values())

literals = '''+-*/(){}=:,;'''

# Regular expression rules for simple tokens
t_NEWLINE = r'\n'

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

LitNumVal = namedtuple('LitNumVal', ['type', 'value'])

def t_LIT_NUM(t):
    r'\d?[.]?\d+'
    if '.' in t.value:
        t.value = LitNumVal("float", float(t.value))
    else:
        t.value = LitNumVal("int", int(t.value))

    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex(debug=False)