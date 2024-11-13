from modules.errors import InvalidSyntaxError
from compiler.tokens import TOKENS
from modules.nodes import NumberNode, BinOpNode, UnaryOpNode
###############################
# PARSE RESULT
###############################
# ParseResult class to keep track of the result of the parsing process
class ParseResult:
    def __init__(self):
        self.error = None  # To store any error encountered during parsing
        self.node = None   # To store the resulting node of the parsing process
    
    # Register the result of a parsing operation
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error  # Propagate the error if any
            return res.node  # Return the node from the result
        return res  # Return the result directly if it's not a ParseResult
    
    # Mark the parsing as successful and store the resulting node
    def success(self, node):
        self.node = node
        return self
    
    # Mark the parsing as failed and store the error
    def failure(self, error):
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
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != TOKENS['TT_EOF']:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*' or '/'"
			))
		return res

	def atom(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TOKENS['TT_INT'], TOKENS['TT_FLOAT']):
			res.register(self.advance())
			return res.success(NumberNode(tok))

		elif tok.type == TOKENS['TT_LPAREN']:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TOKENS['TT_RPAREN']:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int, float, '+', '-' or '('"
		))

	def power(self):
		return self.bin_op(self.atom, (TOKENS['TT_POW'], ), self.factor)

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TOKENS['TT_PLUS'], TOKENS['TT_MINUS']):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		return self.power()

	def term(self):
		return self.bin_op(self.factor, (TOKENS['TT_MUL'], TOKENS['TT_DIV']))

	def expr(self):
		return self.bin_op(self.term, (TOKENS['TT_PLUS'], TOKENS['TT_MINUS']))
	
	def bin_op(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a
		
		res = ParseResult()
		left = res.register(func_a())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func_b())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)