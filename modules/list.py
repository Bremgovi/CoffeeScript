from modules.number import Number
from modules.value import Value
from modules.errors import RTError

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
    
    # Add a value to the list
    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    # Remove a value from the list
    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(
                other.pos_start, other.pos_end,
                "Index out of bounds",
                self.context
            )
        else:
             return None, Value.illegal_operation(self, other)
            
    # Concatenate two lists
    def multed_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)
        
    # Get the value at a certain index
    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                other.pos_start, other.pos_end,
                "Index out of bounds",
                self.context
            )
        else:
            return None, Value.illegal_operation(self, other)
    
    # Copy the list
    def copy(self):
        copy = List(self.elements)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __str__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'