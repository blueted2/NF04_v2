from collections import namedtuple
import ply.lex as lex

reserved = {
    'variables': 'VARIABLES',
    # 'si'       : 'SI',
    # 'fin'      : 'FIN',
    # 'entier'   : 'ENTIER',
    # 'reel'     : 'REEL',
    # 'ptr'      : 'POINTEUR',
    'pointeur' : 'POINTEUR',
    'ptr'      : 'PTR',
    'vers'     : 'VERS',
    'tableau'  : 'TABLEAU',
    'tab'      : 'TAB',
    'de'       : 'DE'
}

# List of token names.   This is always required
tokens = [
   'LIT_NUM',
   'LIT_INT',
   'LIT_FLOAT',
   'NEWLINE',
   'ID',
   'POINTS'
] + list(reserved.values())

literals = "+-*/(){}[]=:,;"

# Regular expression rules for simple tokens
def t_NEWLINE(t):
    r'\n'
    t.value = "\n"
    t.type = "NEWLINE"
    t.lexer.lineno += len(t.value)

    return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'


t_LIT_FLOAT = 'a^'
t_LIT_INT = 'a^'

def t_LIT_NUM(t):
    r'\d?[.]?\d+'
    if '.' in t.value:
        t.type = "LIT_FLOAT"
        t.value = float(t.value)
    else:
        t.type = "LIT_INT"
        t.value = int(t.value)

    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    lower_value = t.value.lower()
    t.type = reserved.get(lower_value,'ID')    # Check for reserved words

    if t.type != "ID":
        t.value = lower_value
    return t

def t_POINTS(t):
    r'\.\.\.'
    t.type = "POINTS"
    return t

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex(debug=False)