###############################
# IMPORTS
###############################
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter
from modules.context import Context

###############################
# RUN
###############################
def run(fn, text):
    # Generate Tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # Generate Result
    interpreter = Interpreter()
    context = Context('<program>')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error