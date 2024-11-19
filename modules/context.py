###############################
# CONTEXT
###############################
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

    def print_symbol_table(self):
        BUILT_IN_FUNCTIONS = [
        "NULL", "TRUE", "FALSE", "MATH_PI", "PRINT", "INPUT", "INPUT_INT", "INPUT_FLOAT", "CLEAR",
        "IS_NUMBER", "IS_STRING", "IS_LIST", "IS_FUNCTION", "APPEND", "POP", "EXTEND", "LEN", "RUN"
        ]
        address = hex(id(self))
        with open("symbol_table.txt", "a") as file:
            file.write(f"\nSymbol table in context: <{self.display_name}> at {address}\n")
            file.write("--------------------------------------------\n")
            if self.symbol_table:
                for key, value in self.symbol_table.symbols.items():
                    if key in BUILT_IN_FUNCTIONS: continue
                    hex_address = hex(id(key))
                    file.write(f"{key} : {repr(value)} (type: {type(value).__name__}), {hex_address}\n")
            file.write("--------------------------------------------\n")

        with open("address_table.txt", "a") as file:
            file.write(f"\<{self.display_name}> at {address}\n")
            
        if self.parent:
            self.parent.print_symbol_table()


        # print(f"\nSymbol table in context: <{self.display_name}>")
        # print("--------------------------------------------")
        # if self.symbol_table:
        #     for key, value in self.symbol_table.symbols.items():
        #         if key in BUILT_IN_FUNCTIONS: continue
        #         print(f"{key} : {repr(value)} (type: {type(value).__name__})")
        # print("--------------------------------------------")
        # if self.parent:
        #     self.parent.print_symbol_table()
