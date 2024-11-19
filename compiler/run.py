###############################
# IMPORTS
###############################
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.interpreter import Interpreter
from modules.context import Context
from modules.function import BuiltInFunction
from modules.symbol_table import SymbolTable
from modules.value import Number

###############################
# RUN
###############################

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("PRINT", BuiltInFunction("print"))
global_symbol_table.set("INPUT", BuiltInFunction("input"))
global_symbol_table.set("INPUT_INT", BuiltInFunction("input_int"))
global_symbol_table.set("INPUT_INT", BuiltInFunction("input_float"))
global_symbol_table.set("CLEAR", BuiltInFunction("clear"))
global_symbol_table.set("IS_NUMBER", BuiltInFunction("is_number"))
global_symbol_table.set("IS_STRING", BuiltInFunction("is_string"))
global_symbol_table.set("IS_LIST", BuiltInFunction("is_list"))
global_symbol_table.set("IS_FUNCTION", BuiltInFunction("is_function"))
global_symbol_table.set("APPEND", BuiltInFunction("append"))
global_symbol_table.set("POP", BuiltInFunction("pop"))
global_symbol_table.set("EXTEND", BuiltInFunction("extend"))
global_symbol_table.set("LEN", BuiltInFunction("len"))
global_symbol_table.set("RUN", BuiltInFunction("run"))

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
    result = interpreter.visit(ast.node, context, run)

    return result.value, result.error, context