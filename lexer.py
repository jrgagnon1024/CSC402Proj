import re

class Lexer:
    # List of token types
    TOKEN_TYPES = [        # integers
        ('FLOAT_TYPE', r'float'),
        ('STRING_TYPE', r'string'),
        ('DATA', r'data'),
        ('DEF',  r'def'),
        ('FN',   r'fn'),
        ('END',  r'end'),
        ('FOR',  r'for'),
        ('TO',   r'to'),
        ('STEP', r'step'),
        ('GOSUB', r'gosub'),
        ('GOTO',  r'goto'),
        ('IF',    r'if'),
        ('THEN',  r'then'),
        ('INPUT',  r'input'),
        ('LET',   r'let'),
        ('NEXT',  r'next'),
        ('ON',    r'on'),
        ('PRINT', r'print'),
        ('RANDOMIZE', r'randomize'),
        ('READ',      r'read'),
        ('REM',       r'rem'),
        ('RESTORE',   r'restore'),
        ('RETURN',    r'return'),
        ('STOP',      r'stop'),
        ('NUMBER', r'([0-9]*[.])?[0-9]+'),  # for INTEGER and FLOAT see below
        ('STRING', r'\"[^\"]*\"'),
        ('ADD', r'\+'),             # plus sign
        ('SUB', r'-'),             # minus sign
        ('MUL', r'\*'),         # multiply sign
        ('DIV', r'/'),            # divide sign
        ('POW', r'\^'),
        ('LEQ',   r'=<'),
        ('EQ',    r'=='),
        ('NEQ',   r'<>'),
        ('LSS',   r'<'),
        ('GRT',   r'>'),
        ('GREQ',   r'=>'),
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