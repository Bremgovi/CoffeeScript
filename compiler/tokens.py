###############################
# TOKENS
###############################

TOKENS = {
    'TT_INT': 'INT',
    'TT_FLOAT': 'FLOAT',
    'TT_PLUS': 'PLUS',
    'TT_MINUS': 'MINUS',
    'TT_MUL': 'MUL',
    'TT_DIV': 'DIV',
    'TT_LPAREN': 'LPAREN',
    'TT_RPAREN': 'RPAREN',
    'TT_EOF': 'EOF',
    'TT_POW': 'POW'
}

# Token class to keep track of the tokens in the input text
class Token:
    # Constructor
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end
        

    # String representation of the token
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'