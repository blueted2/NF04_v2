import ply.lex as lex

class MyLexer:
    reserved = {
        'variables'    : 'VARIABLES',
        'instructions' : 'INSTRUCTIONS',
        'entier'       : 'ENTIER',
        'reel'         : 'REEL',
        'pointeur'     : 'POINTEUR',
        'ptr'          : 'PTR',
        'vers'         : 'VERS',
        'tableau'      : 'TABLEAU',
        'tab'          : 'TAB',
        'de'           : 'DE',
        'algo'         : 'ALGO',
        'sa'           : 'SA',
        'dummy'        : 'DUMMY', # dummy token for testing
    }

    # List of token names.   This is always required
    tokens = [
        'LIT_NUM',
        'LIT_INT',
        'LIT_FLOAT',
        'NEWLINE',
        'ID',
        'POINTS',
        'L_ARROW'
    ] + list(reserved.values())

    literals = "+-*/(){}[]=:,;"

    def __init__(self, debug = False):
        self.lexer = lex.lex(module=self, debug=debug)

    def t_start_cleanup(self, t):
        r'^\n+'
        t.lexer.lineno += len(t.value)

    # Regular expression rules for simple tokens
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        t.value = "\n"

        return t

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Don't automaticaly match
    t_LIT_FLOAT = 'a^'
    t_LIT_INT = 'a^'

    t_L_ARROW = r'<--'

    def t_LIT_NUM(self, t):
        r'\d?[.]?\d+'
        if '.' in t.value:
            t.type = "LIT_FLOAT"
            t.value = float(t.value)
        else:
            t.type = "LIT_INT"
            t.value = int(t.value)

        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        lower_value = t.value.lower()
        t.type = self.reserved.get(lower_value,'ID')    # Check for reserved words

        if t.type != "ID":
            t.value = lower_value
        return t

    def t_POINTS(self, t):
        r'\.\.\.?'
        t.type = "POINTS"
        return t

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
        raise Exception("Illegal character: TODO: deal with this error")
        