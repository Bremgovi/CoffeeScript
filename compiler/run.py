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
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("FALSE", Number.false)

def run(fn, text, context = None):
    # Generate Tokens (Lexical Analysis)
    # Visits each character in the text and generates the corresponding token
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error, context
    
    # Generate AST (Intermediate Representation) (Syntax Analysis) (Semantic Analysis)
    # Visits each token and generates the corresponding node in the AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error, context

    # Generate Result (VCI and execution)
    # Visits each node in the AST and executes the corresponding method in the interpreter
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error, context