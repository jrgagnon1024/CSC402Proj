import re

class Lexer:
    # List of token types
    TOKEN_TYPES = [
        ('INTEGER', r'\d+'),         # integers
        ('PLUS', r'\+'),             # plus sign
        ('MINUS', r'-'),             # minus sign
        ('MULTIPLY', r'\*'),         # multiply sign
        ('DIVIDE', r'/'),            # divide sign
        ('LPAREN', r'\('),           # left parenthesis
        ('RPAREN', r'\)'),           # right parenthesis
        ('ID', r'[A-Z][A-Z0-9]*'),   # identifier
        ('FUNC', r'[A-Z]+\('),       # function
        ('EOL', r';'),               # end of line
        ('SPACE', r'\s+')            # whitespace
    ]

    def __init__(self, input_string):
        # Create a regular expression to match all valid tokens
        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.TOKEN_TYPES)
        self.line_num = 1
        self.line_start = 0
        self.tokens = []
        for mo in re.finditer(token_regex, input_string):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'EOL':
                self.line_start = mo.end()
                self.line_num += 1
            elif kind == 'SPACE':
                pass
            else:
                column = mo.start() - self.line_start
                self.tokens.append(Token(kind, value, self.line_num, column))
    
    def get_tokens(self):
        return self.tokens

# Token class
class Token:
    def __init__(self, kind, value, line_num, column):
        self.kind = kind
        self.value = value
        self.line_num = line_num
        self.column = column
    
    def __str__(self):
        return 'Token(%s, %s, %d, %d)' % (self.kind, self.value, self.line_num, self.column)