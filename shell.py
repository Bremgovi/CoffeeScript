import compiler.run as run
from compiler.lexer import Lexer

while True:
    text = input('CoffeeScript > ')
    result, error, context = run.run('<stdin>', text)
    if error: print(error.as_string())
    elif result: print(result)

    # Optional prints
    if context:
        print("--------------------------------------------")
        print("Symbol table in context: " + context.display_name)
        print(context.symbol_table)

    # Generate tokens and print the token table
    lexer = Lexer('<stdin>', text)
    tokens, error = lexer.make_tokens()
    if error:
        print(error.as_string())
        continue
    print("////////////////////////////////////////////")
    print("Tokens:", tokens)
    print("--------------------------------------------")