import compiler.run as run
from compiler.lexer import Lexer

while True:
    text = input('CoffeeScript > ')
    if text.strip() == "": continue
    result, error, context = run.run('<stdin>', text)
    if error: print(error.as_string())
    elif result: 
        if len(result.elements) == 1: print(repr(result.elements[0]))
        else: print(repr(result))

    # # Optional prints
    # BUILT_IN_FUNCTIONS = [
    #     "NULL", "TRUE", "FALSE", "MATH_PI", "PRINT", "INPUT", "INPUT_INT", "INPUT_FLOAT", "CLEAR",
    #     "IS_NUMBER", "IS_STRING", "IS_LIST", "IS_FUNCTION", "APPEND", "POP", "EXTEND", "LEN", "RUN"
    # ]
    # if context:
    #     print("--------------------------------------------")
    #     print("Symbol table in context: " + context.display_name)
    #     for key in context.symbol_table.symbols:
    #         if key in BUILT_IN_FUNCTIONS: continue
    #         symbol = context.symbol_table.get(key)
    #         print(f"{key} : {repr(symbol)} (type: {type(symbol).__name__})")

    # # Generate tokens and print the token table
    # lexer = Lexer('<stdin>', text)
    # tokens, error = lexer.make_tokens()
    # if error:
    #     print(error.as_string())
    #     continue
    # print("////////////////////////////////////////////")
    # print("Tokens:", tokens)
    # print("--------------------------------------------")