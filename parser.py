class Parser:
  
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens[0]
    
    def error(self):
        raise Exception('Invalid syntax')
    
    def eat(self, token_type):
        if self.current_token.kind == token_type:
            self.current_token = self.tokens[self.tokens.index(self.current_token)+1]
        else:
            self.error()
    
    def factor(self):
        """factor : INTEGER | LPAREN expr RPAREN | FUNC LPAREN expr RPAREN"""
        token = self.current_token
        if token.kind == 'INTEGER':
            self.eat('INTEGER')
            return int(token.value)
        elif token.kind == 'LPAREN':
            self.eat('LPAREN')
            result = self.expr()
            self.eat('RPAREN')
            return result
        elif token.kind == 'FUNC':
            # Extract the function name from the token value
            func_name = token.value[:-1]
            self.eat('FUNC')
            self.eat('LPAREN')
            # Parse the function arguments
            args = []
            while self.current_token.kind != 'RPAREN':
                args.append(self.expr())
                if self.current_token.kind == 'COMMA':
                    self.eat('COMMA')
            self.eat('RPAREN')
            # Call the function with the provided arguments
            return self.call_func(func_name, args)

    def term(self):
        """term : factor ((MULTIPLY | DIVIDE) factor)*"""
        result = self.factor()
        
        while self.current_token.kind in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            if token.kind == 'MULTIPLY':
                self.eat('MULTIPLY')
                result = result * self.factor()
            elif token.kind == 'DIVIDE':
                self.eat('DIVIDE')
                result = result / self.factor()
        
        return result
    
    def expr(self):
        """
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MULTIPLY | DIVIDE) factor)*
        factor : INTEGER | LPAREN expr RPAREN
        """
        result = self.term()
        
        while self.current_token.kind in ('PLUS', 'MINUS'):
            token = self.current_token
            if token.kind == 'PLUS':
                self.eat('PLUS')
                result = result + self.term()
            elif token.kind == 'MINUS':
                self.eat('MINUS')
                result = result - self.term()
        
        return result

  
    def call_func(self, func_name, args):
        if func_name == 'SUM':
            return sum(args)
        # Add additional function definitions here
        else:
            raise Exception('Unknown function: {}'.format(func_name))


def parse(tokens):
    parser = Parser(tokens)
    return parser.expr()
