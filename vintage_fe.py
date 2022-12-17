def formalargs_type(args):

    output_list = list()
    for a in args[1]:
        (FORMALARG, type, id) = a
        output_list.append(type)
    return ('LIST', output_list)

# there are lots of places where we need to lookahead
# on primitive data types -- this list will make it easier.
primitive_lookahead = [
    'INTEGER_TYPE',
    'FLOAT_TYPE',
    'STRING_TYPE',
    ]

# stmt_list : ({VOID_TYPE,INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE,ID,GET,PUT,RETURN,WHILE,IF,LCURLY} stmt)*
stmt_lookahead = [
    'VOID_TYPE',
    'INTEGER_TYPE',
    'FLOAT_TYPE',
    'STRING_TYPE',
    'ID',
    'GET',
    'PUT',
    'RETURN',
    'WHILE',
    'IF',
    'LCURLY',
    ]
def stmt_list(stream):
    lst = []
    while stream.pointer().type in stmt_lookahead:
        s = stmt(stream)
        lst.append(s)
    return ('STMTLIST', lst)

# stmt : {VOID_TYPE} VOID_TYPE ID LPAREN ({INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} formal_args)? RPAREN stmt
#      | {INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} data_type ID decl_suffix
#      | {ID} ID id_suffix
#      | {GET} GET ID ({SEMI} SEMI)?
#      | {PUT} PUT exp ({SEMI} SEMI)?
#      | {RETURN} RETURN ({INTEGER,ID,LPAREN,MINUS,NOT} exp)? ({SEMI} SEMI)?
#      | {WHILE} WHILE LPAREN exp RPAREN stmt
#      | {IF} IF LPAREN exp RPAREN stmt ({ELSE} ELSE stmt)?
#      | {LCURLY} LCURLY stmt_list RCURLY
def stmt(stream):
    if stream.pointer().type in ['VOID_TYPE']:
        stream.match('VOID_TYPE')
        ret_type = ('VOID_TYPE',)
        id_tok = stream.match('ID')
        stream.match('LPAREN')
        args = ('NIL',)
        if stream.pointer().type in primitive_lookahead:
            args = formal_args(stream)
        stream.match('RPAREN')
        arg_types = formalargs_type(args)
        body = stmt(stream)
        return ('FUNDECL',
                ('ID', id_tok.value),
                ('FUNCTION_TYPE', ret_type, arg_types),
                args,
                body)
    elif stream.pointer().type in primitive_lookahead:
        type = data_type(stream)
        id_tok = stream.match('ID')
        e = decl_suffix(stream)
        if e[0] == 'FUNCTION':
            (FUNCTION, args, body) = e
            arg_types = formalargs_type(args)
            return ('FUNDECL',
                    ('ID', id_tok.value),
                    ('FUNCTION_TYPE', type, arg_types),
                    args,
                    body)
        elif e[0] == 'EXPINIT':
            return ('VARDECL',
                    ('ID', id_tok.value),
                    type,
                    e[1])
        elif e[0] == 'ARRAYINIT':
            return ('ARRAYDECL',
                    ('ID', id_tok.value),
                    type,
                    e[1])
        elif e[0] == 'NIL' and type[0] in primitive_lookahead:
            return ('VARDECL',
                    ('ID', id_tok.value),
                    type,
                    ('CONST', ('INTEGER_TYPE',), ('VALUE', 0)))
        elif e[0] == 'NIL' and type[0] == 'ARRAY_TYPE':
            # unpack the array type
            (ARRAY_TYPE, btype, (SIZE, size)) = type
            return ('ARRAYDECL',
                    ('ID', id_tok.value),
                    type,
                    ('LIST',
                        [('CONST',('INTEGER_TYPE',),('VALUE', 0))
                            for _ in range(size)]))
    elif stream.pointer().type in ['ID']:
        id_tok = stream.match('ID')
        e = id_suffix(stream)
        if e[0] == 'CALL':
            return ('CALLSTMT', ('ID', id_tok.value), e[1])
        elif e[0] == 'VAR_ASSIGN':
            return ('ASSIGN', ('ID', id_tok.value), e[1])
        elif e[0] == 'ARRAY_ASSIGN':
            return ('ASSIGN',
                    ('ARRAY_ACCESS',
                     ('ID', id_tok.value),
                     ('IX', e[1])),
                    e[2])
        elif e[0] == 'FUN_ARRAY_ASSIGN':
            (FUN_ARRAY_ASSIGN, args, ix, ae) = e
            return ('ASSIGN',
                    ('ARRAY_ACCESS',
                     ('CALLEXP', ('ID', id_tok.value), args),
                     ('IX', ix)),
                     ae)
    elif stream.pointer().type in ['GET']:
        stream.match('GET')
        id_tk = stream.match('ID')
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('GET', ('ID', id_tk.value))
    elif stream.pointer().type in ['PUT']:
        stream.match('PUT')
        e = exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('PUT', e)
    elif stream.pointer().type in ['RETURN']:
        stream.match('RETURN')
        if stream.pointer().type in exp_lookahead:
            e = exp(stream)
        else:
            e = ('NIL',)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('RETURN', e)
    elif stream.pointer().type in ['WHILE']:
        stream.match('WHILE')
        stream.match('LPAREN')
        e = exp(stream)
        stream.match('RPAREN')
        s = stmt(stream)
        return ('WHILE', e, s)
    elif stream.pointer().type in ['IF']:
        stream.match('IF')
        stream.match('LPAREN')
        e = exp(stream)
        stream.match('RPAREN')
        s1 = stmt(stream)
        if stream.pointer().type in ['ELSE']:
            stream.match('ELSE')
            s2 = stmt(stream)
            return ('IF', e, s1, s2)
        else:
            return ('IF', e, s1, ('NIL',))
    elif stream.pointer().type in ['LCURLY']:
        stream.match('LCURLY')
        sl = stmt_list(stream)
        stream.match('RCURLY')
        return ('BLOCK', sl)
    else:
        raise SyntaxError("stmt: syntax error at {}"
                          .format(stream.pointer().value))

# data_type : {INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} primitive_type
#                   ({LSQUARE} LSQUARE INTEGER RSQUARE)?
def data_type(stream):
    if stream.pointer().type in primitive_lookahead:
        type = primitive_type(stream)
        if stream.pointer().type in ['LSQUARE']:
            stream.match('LSQUARE')
            int_tok = stream.match('INTEGER')
            size = int_tok.value
            stream.match('RSQUARE')
            type = ('ARRAY_TYPE', type, ('SIZE', size))
        return type
    else:
        raise SyntaxError("data_type: syntax error at {}"
                          .format(stream.pointer().value))

# primitive_type : {INTEGER_TYPE} INTEGER_TYPE
#           | {FLOAT_TYPE} FLOAT_TYPE
#           | {STRING_TYPE} STRING_TYPE
def primitive_type(stream):
    if stream.pointer().type in ['INTEGER_TYPE']:
        stream.match('INTEGER_TYPE')
        return ('INTEGER_TYPE',)
    elif stream.pointer().type in ['FLOAT_TYPE']:
        stream.match('FLOAT_TYPE')
        return ('FLOAT_TYPE',)
    elif stream.pointer().type in ['STRING_TYPE']:
        stream.match('STRING_TYPE')
        return ('STRING_TYPE',)
    else:
        raise SyntaxError("primitive_type: syntax error at {}"
                          .format(stream.pointer().value))

# decl_suffix : {LPAREN} LPAREN ({INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} formal_args)? RPAREN stmt
#             | {ASSIGN} ASSIGN exp ({SEMI} SEMI)?
#             | ({SEMI} SEMI)?
def decl_suffix(stream):
    if stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        if stream.pointer().type in primitive_lookahead:
            args = formal_args(stream)
        else:
            args = ('LIST', [])
        stream.match('RPAREN')
        body = stmt(stream)
        return ('FUNCTION', args, body )
    elif stream.pointer().type in ['ASSIGN']:
        stream.match('ASSIGN')
        if stream.pointer().type in exp_lookahead:
            ie = exp(stream)
            if ie[0] != 'CONST':
                raise ValueError("only constants are allowed in initializers")
            e = ('EXPINIT', ie)
        elif stream.pointer().type in ['LCURLY']:
            stream.match('LCURLY')
            ie = exp(stream)
            if ie[0] != 'CONST':
                raise ValueError("only constants are allowed in initializers")
            ll = [ie]
            while stream.pointer().type in ['COMMA']:
                stream.match('COMMA')
                ie = exp(stream)
                if ie[0] != 'CONST':
                    raise ValueError("only constants are allowed in initializers")
                ll.append(ie)
            stream.match('RCURLY')
            e = ('ARRAYINIT', ('LIST', ll))
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return e
    else:
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('NIL',)

# id_suffix : {LPAREN} LPAREN ({INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} actual_args)?
#                      ({LSQUARE} LSQUARE exp RSQUARE ASSIGN exp)?
#                      ({SEMI} SEMI)?
#           | {LSQUARE} LSQUARE exp RSQUARE = exp ({SEMI} SEMI)?
#           | {ASSIGN} ASSIGN exp ({SEMI} SEMI)?
def id_suffix(stream):
    if stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        if stream.pointer().type in exp_lookahead:
            args = actual_args(stream)
        else:
            args = ('LIST', list())
        stream.match('RPAREN')
        tree = ('CALL', args)
        if stream.pointer().type in ['LSQUARE']:
            stream.match('LSQUARE')
            ix = exp(stream)
            stream.match('RSQUARE')
            stream.match('ASSIGN')
            e = exp(stream)
            tree = ('FUN_ARRAY_ASSIGN',
                    args,
                    ix,
                    e)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return tree
    elif stream.pointer().type in ['LSQUARE']:
        stream.match('LSQUARE')
        ix = exp(stream)
        stream.match('RSQUARE')
        stream.match('ASSIGN')
        e = exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('ARRAY_ASSIGN', ix, e)
    elif stream.pointer().type in ['ASSIGN']:
        stream.match('ASSIGN')
        e = exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('VAR_ASSIGN', e)
    else:
        raise SyntaxError("id_suffix: syntax error at {}"
                          .format(stream.pointer().value))

# exp : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp_low
# exp_lookahead
#   == exp_low_lookahead
#   == exp_med_lookahead
#   == exp_high_lookahead
#   == primary_lookahead
exp_lookahead = [
    'INTEGER',
    'FLOAT',
    'STRING',
    'ID',
    'LPAREN',
    'MINUS',
    'NOT',
    ]

def exp(stream):
    if stream.pointer().type in exp_lookahead:
        e = exp_low(stream)
        return e
    else:
        raise SyntaxError("exp: syntax error at {}"
                          .format(stream.pointer().value))

# exp_low : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp_med ({EQ,LE} (EQ|LE) exp_med)*
def exp_low(stream):
    if stream.pointer().type in exp_lookahead:
        e = exp_med(stream)
        while stream.pointer().type in ['EQ','LE']:
            if stream.pointer().type == 'EQ':
                op_tk = stream.match('EQ')
            else:
                op_tk = stream.match('LE')
            tmp = exp_med(stream)
            e = (op_tk.type, e, tmp)
        return e
    else:
        raise SyntaxError("exp_low: syntax error at {}"
                          .format(stream.pointer().value))

# exp_med : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp_high ({PLUS,MINUS} (PLUS|MINUS) exp_high)*
def exp_med(stream):
    if stream.pointer().type in exp_lookahead:
        e = exp_high(stream)
        while stream.pointer().type in ['PLUS','MINUS']:
            if stream.pointer().type == 'PLUS':
                op_tk = stream.match('PLUS')
            else:
                op_tk = stream.match('MINUS')
            tmp = exp_high(stream)
            e = (op_tk.type, e, tmp)
        return e
    else:
        raise SyntaxError("exp_med: syntax error at {}"
                          .format(stream.pointer().value))

# exp_high : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} primary ({MUL,DIV} (MUL|DIV) primary)*
def exp_high(stream):
    if stream.pointer().type in exp_lookahead:
        e = primary(stream)
        while stream.pointer().type in ['MUL','DIV']:
            if stream.pointer().type == 'MUL':
                op_tk = stream.match('MUL')
            else:
                op_tk = stream.match('DIV')
            tmp = primary(stream)
            e = (op_tk.type, e, tmp)
        return e
    else:
        raise SyntaxError("exp_high: syntax error at {}"
                          .format(stream.pointer().value))

# primary : {INTEGER} INTEGER
#         | {FLOAT} FLOAT
#         | {STRING} STRING
#         | {ID} ID ({LPAREN,LSQUARE} id_exp_suffix)?
#         | {LPAREN} LPAREN exp RPAREN
#         | {MINUS} MINUS primary
#         | {NOT} NOT primary
def primary(stream):
    if stream.pointer().type in ['INTEGER']:
        tk = stream.match('INTEGER')
        return ('CONST', ('INTEGER_TYPE',), ('VALUE', int(tk.value)))
    elif stream.pointer().type in ['FLOAT']:
        tk = stream.match('FLOAT')
        return ('CONST', ('FLOAT_TYPE',), ('VALUE', float(tk.value)))
    elif stream.pointer().type in ['STRING']:
        tk = stream.match('STRING')
        return ('CONST', ('STRING_TYPE',), ('VALUE', str(tk.value)))
    elif stream.pointer().type in ['ID']:
        id_tok = stream.match('ID')
        if stream.pointer().type in ['LPAREN','LSQUARE']:
            e = id_exp_suffix(stream)
            if e[0] == 'CALL':
                return ('CALLEXP', ('ID', id_tok.value), e[1])
            elif e[0] == 'ARRAY':
                return ('ARRAY_ACCESS',
                        ('ID', id_tok.value),
                        ('IX', e[1]))
            elif e[0] == 'FUN_ARRAY':
                return ('ARRAY_ACCESS',
                        ('CALLEXP', ('ID', id_tok.value), e[1]),
                        ('IX', e[2]))
            else:
                raise ValueError("uknown suffix {}".format(e[0]))
        else:
            return ('ID', id_tok.value)
    elif stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        e = exp(stream)
        stream.match('RPAREN')
        return e
    elif stream.pointer().type in ['MINUS']:
        stream.match('MINUS')
        e = primary(stream)
        if e[0] == 'CONST' and e[1][0] in ['INTEGER_TYPE', 'FLOAT_TYPE']:
            return ('CONST', e[1], -e[2])
        else:
            return ('UMINUS', e)
    elif stream.pointer().type in ['NOT']:
        stream.match('NOT')
        e = primary(stream)
        # (CONST, TYPE, VAL)
        if e[0] == 'CONST' and e[1][0] == 'INTEGER_TYPE':
            return ('CONST', ('INTEGER_TYPE',), 0 if e[2] else 1)
        else:
            return ('NOT', e)
    else:
        raise SyntaxError("primary: syntax error at {}"
                          .format(stream.pointer().value))

# id_exp_suffix : {LPAREN} LPAREN ({INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} actual_args)? RPAREN
#                       ({LSQUARE} LSQUARE exp RSQUARE)?
#               | {LSQUARE} LSQUARE exp RSQUARE
def id_exp_suffix(stream):
    if stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        if stream.pointer().type in exp_lookahead:
            args = actual_args(stream)
        else:
            args = ('LIST', [])
        stream.match('RPAREN')
        tree = ('CALL', args)
        if stream.pointer().type in ['LSQUARE']:
            stream.match('LSQUARE')
            e = exp(stream)
            stream.match('RSQUARE')
            tree = ('FUN_ARRAY', args, e)
        return tree
    elif stream.pointer().type in ['LSQUARE']:
        stream.match('LSQUARE')
        e = exp(stream)
        stream.match('RSQUARE')
        return ('ARRAY', e)
    else:
        raise ValueError("syntax error at {}"
                        .format(stream.pointer().value))

# formal_args : {INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} data_type ID ({COMMA} COMMA data_type ID)*
def formal_args(stream):
    if stream.pointer().type in primitive_lookahead:
        type = data_type(stream)
        id_tok = stream.match('ID')
        ll = [('FORMALARG', type, ('ID', id_tok.value))]
        while stream.pointer().type in ['COMMA']:
            stream.match('COMMA')
            type = data_type(stream)
            id_tok = stream.match('ID')
            ll.append(('FORMALARG', type, ('ID', id_tok.value)))
        return ('LIST', ll)
    else:
        raise SyntaxError("formal_args: syntax error at {}"
                          .format(stream.pointer().value))

# actual_args : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp ({COMMA} COMMA exp)*
def actual_args(stream):
    if stream.pointer().type in exp_lookahead:
        e = exp(stream)
        ll = [e]
        while stream.pointer().type in ['COMMA']:
            stream.match('COMMA')
            e = exp(stream)
            ll.append(e)
        return ('LIST', ll)
    else:
        raise SyntaxError("actual_args: syntax error at {}"
                          .format(stream.pointer().value))

# frontend top-level driver
def parse(stream):
    from cuppa5_lexer import Lexer
    token_stream = Lexer(stream)
    sl = stmt_list(token_stream) # call the parser function for start symbol
    if not token_stream.end_of_file():
        raise SyntaxError("parse: syntax error at {}"
                          .format(token_stream.pointer().value))
    else:
        return sl

if __name__ == "__main__":
    from sys import stdin
    from dumpast import dumpast
    char_stream = stdin.read() # read from stdin
    dumpast(parse(char_stream))
