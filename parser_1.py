class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = lexer.get_tokens()
        self.current_token_index = 0

    def parse(self):
        statements = []
        while self.current_token_index < len(self.tokens):
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            else:
                # if we can't parse a statement, skip the current token and try again
                self.current_token_index += 1
        return statements

    def parse_statement(self):
        token = self.tokens[self.current_token_index]
        if token.kind == 'PRINT':
            return self.parse_print_statement()
        elif token.kind == 'LET':
            return self.parse_assignment_statement()
        elif token.kind == 'IF':
            return self.parse_if_statement()
        elif token.kind == 'GOTO':
            return self.parse_goto_statement()
        elif token.kind == 'GOSUB':
            return self.parse_gosub_statement()
        elif token.kind == 'RETURN':
            return self.parse_return_statement()
        elif token.kind == 'FOR':
            return self.parse_for_loop()
        elif token.kind == 'NEXT':
            return self.parse_next_statement()
        elif token.kind == 'END':
            return self.parse_end_statement()
        elif token.kind == 'REM':
            return self.parse_remark_statement()
        else:
            return None
    
    def parse_print_statement(self):
        # consume the PRINT token
        self.current_token_index += 1
        # parse the expression to be printed
        expression = self.parse_expression()
        return ('PRINT', expression)
    
    def parse_if_statement(self):
        # consume the IF token
        self.current_token_index += 1
        # parse the condition
        condition = self.parse_expression()
        # check for the THEN token
        if self.tokens[self.current_token_index].kind != 'THEN':
            return None
        self.current_token_index += 1
        # parse the statement to be executed if the condition is true
        true_statement = self.parse_statement()
        # check for an ELSE clause
        if self.current_token_index < len(self.tokens) and self.tokens[self.current_token_index].kind == 'ELSE':
            self.current_token_index += 1
            # parse the statement to be executed if the condition is false
            false_statement = self.parse_statement()
        else:
            false_statement = None
        return ('IF', condition, true_statement, false_statement)
    
    def parse_assignment_statement(self):
        # consume the LET token
        self.current_token_index += 1
        # parse the variable being assigned to
        variable        = self.tokens[self.current_token_index]
        if variable.kind != 'ID':
            return None
        self.current_token_index += 1
        # check for the equals sign
        if self.tokens[self.current_token_index].kind != 'EQ':
            return None
        self.current_token_index += 1
        # parse the expression being assigned
        expression = self.parse_expression()
        return ('LET', variable.value, expression)
    
    def parse_goto_statement(self):
        # consume the GOTO token
        self.current_token_index += 1
        # parse the line number
        line_number = self.tokens[self.current_token_index]
        if line_number.kind != 'NUMBER':
            return None
        self.current_token_index += 1
        return ('GOTO', line_number.value)
    
    def parse_gosub_statement(self):
        # consume the GOSUB token
        self.current_token_index += 1
        # parse the line number
        line_number = self.tokens[self.current_token_index]
        if line_number.kind != 'NUMBER':
            return None
        self.current_token_index += 1
        return ('GOSUB', line_number.value)
    def parse_return_statement(self):
        # consume the RETURN token
        self.current_token_index += 1
        return ('RETURN',)
    
    def parse_for_loop(self):
        # consume the FOR token
        self.current_token_index += 1
        # parse the loop variable
        loop_variable = self.tokens[self.current_token_index]
        if loop_variable.kind != 'ID':
            return None
        self.current_token_index += 1
        # check for the equals sign
        if self.tokens[self.current_token_index].kind != 'EQ':
            return None
        self.current_token_index += 1
        # parse the starting value
        start_value = self.parse_expression()
        # check for the TO token
        if self.tokens[self.current_token_index].kind != 'TO':
            return None
        self.current_token_index += 1
        # parse the ending value
        end_value = self.parse_expression()
        # check for an optional STEP clause
        if self.current_token_index < len(self.tokens) and self.tokens[self.current_token_index].kind == 'STEP':
            self.current_token_index += 1
            # parse the step value
            step_value = self.parse_expression()
        else:
            step_value = None
        # parse the statement to be executed in the loop
        loop_statement = self.parse_statement()
        return ('FOR', loop_variable.value, start_value, end_value, step_value, loop_statement)
    
    def parse_next_statement(self):
        # consume the NEXT token
        self.current_token_index += 1
        # parse the loop variable
        loop_variable = self.tokens[self.current_token_index]
        if loop_variable.kind != 'ID':
            return None
        self.current_token_index += 1
        return ('NEXT', loop_variable.value)
    
    def parse_end_statement(self):
        # consume the END token
        self.current_token_index += 1
        return ('END',)
    
    def parse_remark_statement(self):
        # consume the REM token
        self.current_token_index += 1
        # parse the rest of the line as the remark
        remark = ''
        while self.current_token_index < len(self.tokens) and self.tokens[self.current_token_index].kind != 'EOL':
            remark += self.tokens[self.current_token_index].value
            self.current_token_index += 1
        return ('REM', remark)
    
    def parse_expression(self):
        # parse a term
        term = self.parse_term()
        if not term:
            return None
        # check for additional terms separated by + or -
        terms = [term]
        while self.current_token_index < len(self.tokens) and self:
          terms.append(self.parse_term())
        # if we have more than one term, return a tuple representing the expression
        if len(terms) > 1:
            return ('EXPR', terms)
        # otherwise, return the single term
        return term
    
    def parse_term(self):
        # parse a factor
        factor = self.parse_factor()
        if not factor:
            return None
        # check for additional factors separated by * or /
        factors = [factor]
        while self.current_token_index < len(self.tokens) and self.tokens[self.current_token_index].kind in ['MUL', 'DIV', 'MOD']:
            factors.append(self.parse_factor())
        # if we have more than one factor, return a tuple representing the term
        if len(factors) > 1:
            return ('TERM', factors)
        # otherwise, return the single factor
        return factor
    
    def parse_factor(self):
        # check for a leading sign
        sign = 1
        if self.tokens[self.current_token_index].kind in ['ADD', 'SUB']:
            if self.tokens[self.current_token_index].kind == 'SUB':
                sign = -1
            self.current_token_index += 1
        # check for an opening parenthesis
        if self.tokens[self.current_token_index].kind == 'LPAREN':
            self.current_token_index += 1
            # parse the expression inside the parenthesis
            expression = self.parse_expression()
            # check for the closing parenthesis
            if self.tokens[self.current_token_index].kind != 'RPAREN':
                return None
            self.current_token_index += 1
            # return the expression inside the parenthesis with the correct sign
            return ('FACTOR', sign, expression)
        # check for a number
        if self.tokens[self.current_token_index].kind in ['NUMBER', 'FLOAT_TYPE']:
            number = self.tokens[self.current_token_index]
            self.current_token_index += 1
            # return the number with the correct sign
            return ('FACTOR', sign, number.value)
        # check for an identifier
        if self.tokens[self.current_token_index].kind == 'ID':
            identifier = self.tokens[self.current_token_index]
            self.current_token_index += 1
            # check for an opening parenthesis, indicating a function call
            if self.current_token_index < len(self.tokens) and self.tokens[self.current_token_index].kind == 'LPAREN':
                self.current_token_index += 1
                # parse the arguments to the function
                arguments = self.parse_arguments()
                # check for the closing parenthesis
                if self.tokens[self.current_token_index].kind != 'RPAREN':
                    return None
                self.current_token_index += 1
                # return the function call with the correct sign
                return ('FACTOR', sign, ('FUNC', identifier.value, arguments))
            # return the identifier with the correct sign
            return ('FACTOR', sign, identifier.value)
        # check for a function
        if self.tokens[self.current_token_index].kind == 'FUNC':
            func = self.tokens[self.current_token_index]
            self.current_token_index += 1
            # parse the arguments to the function
            arguments = self.parse_arguments()
            # check for the closing parenthesis
            if self.tokens[self.current_token_index].kind != 'RPAREN':
                return None
            self.current_token_index += 1
            # return the function call with the correct sign
            return ('FACTOR', sign, ('FUNC', func.value[:-1], arguments))
        # if we couldn't parse a factor, return None
        return None
    
    def parse_arguments(self):
        # list to hold the arguments
        arguments = []
        # parse the first argument
        argument = self.parse_expression()
        if argument:
            arguments.append(argument)
        # parse any additional arguments separated by commas
        while self.current_token_index < len(self.tokens) and self.tokens[self.current_token_index].kind == 'COMMA':
            self.current_token_index += 1
            argument = self.parse_expression()
            if argument:
                arguments.append(argument)
        # return the list of arguments
        return arguments
