import ply.lex as lex

class MyLexer:
    reserved = [
        'TYPES',
        'VARIABLES',
        'INSTRUCTIONS',
        'ENTIER',
        'REEL',
        'POINTEUR',
        'TABLEAU',
        'SUR',
        'DE',
        'ALGORITHME',
        'SA',
        'OU',
        'ET',
        'NON',
        'PE',
        'PS',
        'POUR',
        'ALLANT',
        'A',
        'PAR',
        'PAS',
        'FINPOUR',
        'FINALGO',
        'FINSA',
        'SOUS',
        'TANT',
        'QUE',
        'FAIRE',
        'FINTQ'
    ]

    # List of token names.   This is always required
    tokens = [
        'LIT_INT',
        'LIT_FLOAT',
        'NEWLINE',
        'ID',
        'POINTS',
        'L_ARROW',
        'EOF',
        'LTE', # "less than equals"    -> '<='
        'GTE', # "greater than equals" -> '>='
    ] + list(reserved)

    aliases = {
        'PTR'            : 'POINTEUR',
        'ALGO'           : 'ALGORITHME',
        'À'              : 'A',
        'SOUSALGO'       : 'SA',
        'SOUSALGORITHME' : 'SA'
    }

    literals = "+-*/(){}[]=:,;.&^%!<>"

    def __init__(self, debug = False):
        self.lexer = lex.lex(module=self, debug=debug)
        self._has_reached_eof = False

    def t_start_cleanup(self, t):
        r'^\n+'
        t.lexer.lineno += len(t.value)

    # Regular expression rules for simple tokens
    def t_NEWLINE(self, t):
        r'\n([ ]*\n)*'
        t.lexer.lineno += t.value.count('\n')
        t.value = "\n"

        return t

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Don't automaticaly match
    t_LIT_FLOAT = 'a^'
    t_LIT_INT = 'a^'

    t_L_ARROW = r'<--'
    t_LTE = r'<='
    t_GTE = r'>='


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
        r'[a-zA-Z_À-ÿ][a-zA-Z_0-9À-ÿ]*'
        upper_value = t.value.upper()

        if upper_value in self.tokens:
            t.type = upper_value
        elif upper_value in self.aliases.keys():
            t.type = self.aliases[upper_value]


        # t.type = self.reserved.get(lower_value,'ID')    # Check for reserved words

        return t

    def t_POINTS(self, t):
        r'\.\.\.?'
        t.type = "POINTS"
        return t

    def t_eof(self, t):
        if not self._has_reached_eof:
            self._has_reached_eof = True
            t.type = 'EOF'
            t.value = t.type
            return t


    # Error handling rule
    def t_error(self, t):
        char = t.value[0]
        print(ord(char))
        print(f"Illegal character '{char}'")

        t.lexer.skip(1)
        raise Exception("Illegal character: TODO: deal with this error")
        