###############################
# IMPORTS
###############################
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter
from modules.context import Context
from modules.symbol_table import SymbolTable
from modules.number import Number

###############################
# RUN
###############################

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))

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
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error