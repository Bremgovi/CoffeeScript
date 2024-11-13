from compiler.tokens import Token, TOKENS
from modules.errors import IllegalCharError
###############################
# POSITION
###############################
# Position class to keep track of the current character in the input text
class Position: 
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx # index of the current character in the input text
        self.ln = ln # line number in the input text
        self.col = col # column number in the input text
        self.fn = fn # filename of the input text
        self.ftxt = ftxt # full input text

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

# Lexer class to convert the input text into tokens
class Lexer:
    def __init__(self, fn, text):
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    # Function to add tokens to an array of tokens
    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char.isdigit():
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TOKENS['TT_PLUS'], pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TOKENS['TT_MINUS'], pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TOKENS['TT_MUL'], pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TOKENS['TT_DIV'], pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TOKENS['TT_POW'], pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TOKENS['TT_LPAREN'], pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TOKENS['TT_RPAREN'], pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos.copy(), "'" + char + "'")
        tokens.append(Token(TOKENS['TT_EOF'], pos_start=self.pos))
        return tokens, None
    
    # Function to convert character into integer or float
    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOKENS['TT_INT'], int(num_str), pos_start, self.pos)
        else:
            return Token(TOKENS['TT_FLOAT'], float(num_str), pos_start, self.pos)

