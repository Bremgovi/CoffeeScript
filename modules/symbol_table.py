###############################
# SYMBOL TABLE
###############################
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None # To keep track of global variables

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value):
        self.symbols[name] = value
    
    def remove(self, name):
        del self.symbols[name]

    def __repr__(self):
        return f"{self.symbols}"
    
    
