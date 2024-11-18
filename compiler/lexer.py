from compiler.tokens import Token, TOKENS, KEYWORDS
from modules.errors import ExpectedCharError, IllegalCharError
import string

LETTERS = string.ascii_letters
DIGITS = '0123456789'
LETTERS_DIGITS = LETTERS + DIGITS

###############################
# POSITION
# Position class to keep track of the current character in the input text
###############################

class Position: 
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln 
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

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
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_string())
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
            elif self.current_char == ',':
                tokens.append(Token(TOKENS['TT_COMMA'], pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TOKENS['TT_LPAREN'], pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TOKENS['TT_RPAREN'], pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
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
        
    # Function to convert character into identifier
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TOKENS['TT_KEYWORD'] if id_str in KEYWORDS else TOKENS['TT_IDENTIFIER']
        return Token(tok_type, id_str, pos_start, self.pos)

    # Function to convert character into string
    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False

        self.advance()
        return Token(TOKENS['TT_STRING'], string, pos_start, self.pos)

    # Function to convert character into equals
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TOKENS['TT_NE'], pos_start=pos_start, pos_end=self.pos), None
        
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!' expected)")
    
    def make_equals(self):
        token_type = TOKENS['TT_EQ']
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TOKENS['TT_EE']

        elif self.current_char == '>':
            self.advance()
            token_type = TOKENS['TT_ARROW']
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_less_than(self):
        token_type = TOKENS['TT_LT']
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TOKENS['TT_LTE']
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_greater_than(self):
        token_type = TOKENS['TT_GT']
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TOKENS['TT_GTE']
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    