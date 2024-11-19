from modules.errors import InvalidSyntaxError
from compiler.tokens import TOKENS
from modules.nodes import BreakNode, CallNode, ContinueNode, ForNode, FuncDefNode, IfNode, ListNode, NumberNode, BinOpNode, ReturnNode, StringNode, UnaryOpNode, VarAccessNode, VarAssignNode, WhileNode
###############################
# PARSE RESULT
# ParseResult class to keep track of the result of the parsing process
###############################

class ParseResult:
    def __init__(self):
        self.error = None  # To store any error encountered during parsing
        self.node = None   # To store the resulting node of the parsing process
        self.advance_count = 0  # To keep track of the number of advancements made during parsing
        self.to_reverse_count = 0  # To keep track of the number of advancements to reverse

    def register_advancement(self):
        self.advance_count += 1
        
    # Register the result of a parsing operation
    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error  # Propagate the error if any
        return res.node  # Return the node from the result
    
    # Try to register the result of a parsing operation
    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    # Mark the parsing as successful and store the resulting node
    def success(self, node):
        self.node = node
        return self
    
    # Mark the parsing as failed and store the error
    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

###############################
# PARSER
###############################
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok
    
    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TOKENS['TT_EOF']:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*' or '/'"
            ))
        return res
    
    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TOKENS['TT_NEWLINE']:
            res.register_advancement()
            self.advance()
        
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TOKENS['TT_NEWLINE']:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False
            if not more_statements: break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(ListNode(statements, pos_start, self.current_tok.pos_start.copy()))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'RETURN'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
        
        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'CONTINUE'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
        
        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'BREAK'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'RETURN', 'CONTINUE', 'BREAK', 'VAR', int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUNCTION'"
            ))
        return res.success(expr)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
    
    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TOKENS['TT_LPAREN']:
            res.register_advancement()
            self.advance()
            arg_nodes = []
            
            if self.current_tok.type == TOKENS['TT_RPAREN']:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')', 'VAR', int, float, identifier, '+', '-', '(', '[', 'NOT'"
                    ))
                while self.current_tok.type == TOKENS['TT_COMMA']:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res
                if self.current_tok.type != TOKENS['TT_RPAREN']:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')'"
                    ))
                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)


    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOKENS['TT_INT'], TOKENS['TT_FLOAT']):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        
        if tok.type == TOKENS['TT_STRING']:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TOKENS['TT_IDENTIFIER']:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TOKENS['TT_LPAREN']:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TOKENS['TT_RPAREN']:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
        
        elif tok.type == TOKENS['TT_LSQUARE']:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)

        elif tok.matches(TOKENS['TT_KEYWORD'], 'IF'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)	
        
        elif tok.matches(TOKENS['TT_KEYWORD'], 'FOR'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
       
        elif tok.matches(TOKENS['TT_KEYWORD'], 'WHILE'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(TOKENS['TT_KEYWORD'], 'FUNCTION'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUNCTION'"
        ))

    def power(self):
        return self.bin_op(self.call, (TOKENS['TT_POW'], ), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOKENS['TT_PLUS'], TOKENS['TT_MINUS']):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TOKENS['TT_MUL'], TOKENS['TT_DIV'], TOKENS['TT_MOD']))

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'VAR'):
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TOKENS['TT_IDENTIFIER']:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))
            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TOKENS['TT_EQ']:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
            
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr, True))
        
        elif self.current_tok.type == TOKENS['TT_IDENTIFIER']:
            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type == TOKENS['TT_EQ']:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                return res.success(VarAssignNode(var_name, expr, False))
            else:
                self.reverse()
        node = res.register(self.bin_op(self.comp_expr, ((TOKENS['TT_KEYWORD'], 'AND'), (TOKENS['TT_KEYWORD'], 'OR'))))

        if res.error: 
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUNCTION'"
            ))
        return res.success(node)
    
    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TOKENS['TT_LSQUARE']:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENS['TT_RSQUARE']:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ']', 'VAR', int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUNCTION'"
                ))
            while self.current_tok.type == TOKENS['TT_COMMA']:
                res.register_advancement()
                self.advance()
                element_nodes.append(res.register(self.expr()))
                if res.error: return res
            if self.current_tok.type != TOKENS['TT_RSQUARE']:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))
            res.register_advancement()
            self.advance()
        return res.success(ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy()))
    
    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('IF'))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def elif_expr(self):
        return self.if_expr_cases('ELIF')

    def else_expr(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'ELSE'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TOKENS['TT_NEWLINE']:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'END'):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected 'END'"
                    ))
            else:
                expr = res.register(self.statement())
                if res.error: return res
                else_case = (expr, False)
        return res.success(else_case)
    
    def elif_or_else(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'ELIF'):
            all_cases = res.register(self.elif_expr())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        else:
            else_case = res.register(self.else_expr())
            if res.error: return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))

        res.register_advancement()
        self.advance()
        
        if self.current_tok.type == TOKENS['TT_NEWLINE']:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'END'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.elif_or_else())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.elif_or_else())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        
        return res.success((cases, else_case))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'WHILE'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'WHILE'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENS['TT_NEWLINE']:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'END'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'END'"
                ))
            res.register_advancement()
            self.advance()
            
            return res.success(WhileNode(condition, body, True))


        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhileNode(condition, body, False))
    
    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'FOR'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'FOR'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOKENS['TT_IDENTIFIER']:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOKENS['TT_EQ']:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '='"
            ))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'TO'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'TO'"
            ))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'STEP'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENS['TT_NEWLINE']:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'END'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'END'"
                ))
            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))
    
    def func_def(self):
        res = ParseResult()
        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'FUNCTION'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'FUNCTION'"
            ))
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENS['TT_IDENTIFIER']:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOKENS['TT_LPAREN']:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TOKENS['TT_LPAREN']:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier or '('"
                ))
        res.register_advancement()
        self.advance()

        arg_name_toks = []
        if self.current_tok.type == TOKENS['TT_IDENTIFIER']:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TOKENS['TT_COMMA']:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TOKENS['TT_IDENTIFIER']:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier"
                    ))
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TOKENS['TT_RPAREN']:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',' or ')'"
                ))
        else:
            if self.current_tok.type != TOKENS['TT_RPAREN']:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier or ')'"
                ))
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TOKENS['TT_ARROW']:
            res.register_advancement()
            self.advance()
            body = res.register(self.expr())
            if res.error: return res
            return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, True))

        if self.current_tok.type != TOKENS['TT_NEWLINE']:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '=>' or NEWLINE"
            ))
        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error: return res

        if not self.current_tok.matches(TOKENS['TT_KEYWORD'], 'END'):
            print("TOKEN: ", self.current_tok)
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'END'"
            ))
        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, False))

    def arith_expr(self):
        return self.bin_op(self.term, (TOKENS['TT_PLUS'], TOKENS['TT_MINUS']))

    def comp_expr(self):
        res = ParseResult()
        if self.current_tok.matches(TOKENS['TT_KEYWORD'], 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))
        node = res.register(self.bin_op(self.arith_expr, (TOKENS['TT_EE'], TOKENS['TT_NE'], TOKENS['TT_LT'], TOKENS['TT_GT'], TOKENS['TT_LTE'], TOKENS['TT_GTE'])))
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(', '[', 'NOT'"
            ))
        return res.success(node)