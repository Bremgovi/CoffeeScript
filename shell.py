import compiler.run as run

while True:
    text = input('shell > ')
    result, error, context = run.run('<stdin>',text)
    if error: print(error.as_string())
    elif result: print(result)
    else: print(result)
    
    # Optional prints
    print("\n--------------------------------------------")
    print("Symbol table in context: " + context.display_name)
    print(context.symbol_table)
    print("--------------------------------------------\n")