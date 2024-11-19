from modules.errors import RTError
from modules.list import List
from modules.value import Number
from modules.value import String
from modules.value import Value
from modules.context import Context
from modules.symbol_table import SymbolTable
import os
class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"
        
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(self.context.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args, rt_result):
        res = rt_result
        if len(args) > len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
                self.context
            ))
        if len(args) < len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
                self.context
            ))
        return res.success(None)
    
    def populate_args(self, arg_names, args, execution_context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(execution_context)
            execution_context.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, execution_context, rt_result):
        res = rt_result
        res.register(self.check_args(arg_names, args, rt_result))
        if res.should_return(): return res
        self.populate_args(arg_names, args, execution_context)
        return res.success(None)

class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
    
    def execute(self, args, interpreter, rt_result, run=None):
        res = rt_result
        execution_context = self.generate_new_context()
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)
        
        res.register(self.check_and_populate_args(method.arg_names, args, execution_context, rt_result))
        if res.should_return(): return res

        if self.name == "run":
            return_value = res.register(method(execution_context, rt_result, run))
        else:
            return_value = res.register(method(execution_context, rt_result))
        if res.should_return(): return res

        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<built-in function {self.name}>"

    def execute_print(self, execution_context, rt_result):
        # print(str(execution_context.symbol_table.get("value")))
        # return rt_result.success(Number.null)
        value = execution_context.symbol_table.get("value")
        if isinstance(value, List):
            concatenated_string = ''.join([str(element) for element in value.elements])
        else:
            concatenated_string = str(value)
        print(concatenated_string)
        return rt_result.success(Number.null)
    execute_print.arg_names = ["value"]

    def execute_print_ret(self, execution_context, rt_result):
        return rt_result.success(String(str(execution_context.symbol_table.get("value"))))
    execute_print_ret.arg_names = ["value"]

    def execute_input(self, execution_context, rt_result):
        text = input()
        try:
            number = float(text)
            return rt_result.success(Number(number))
        except ValueError:
            return rt_result.success(String(text))
    execute_input.arg_names = []
    
    def execute_input_int(self, execution_context, rt_result):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again.")
                text = input()
        return rt_result.success(Number(number))
    execute_input_int.arg_names = []

    def execute_input_float(self, execution_context, rt_result):
        while True:
            text = input()
            try:
                number = float(text)
                break
            except ValueError:
                print(f"'{text}' must be a float. Try again.")
        return rt_result.success(Number(number))
    execute_input_float.arg_names = []

    def execute_clear(self, execution_context, rt_result):
        os.system('cls' if os.name == 'nt' else 'clear')
        return rt_result.success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, execution_context, rt_result):
        is_number = isinstance(execution_context.symbol_table.get("value"), Number)
        return rt_result.success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ['value']

    def execute_is_string(self, execution_context, rt_result):
        is_string = isinstance(execution_context.symbol_table.get("value"), String)
        return rt_result.success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ['value']

    def execute_is_list(self, execution_context, rt_result):
        is_list = isinstance(execution_context.symbol_table.get("value"), List)
        return rt_result.success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ['value']

    def execute_is_function(self, execution_context, rt_result):
        is_function = isinstance(execution_context.symbol_table.get("value"), BaseFunction)
        return rt_result.success(Number.true if is_function else Number.false)
    execute_is_function.arg_names = ['value']

    def execute_append(self, execution_context, rt_result):
        list_ = execution_context.symbol_table.get("list")
        value = execution_context.symbol_table.get("value")
        if not isinstance(list_, List):
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                execution_context
            ))
        list_.elements.append(value)
        return rt_result.success(Number.null)
    execute_append.arg_names = ['list', 'value']

    def execute_pop(self, execution_context, rt_result):
        list_ = execution_context.symbol_table.get("list")
        index = execution_context.symbol_table.get("index")
        if not isinstance(list_, List):
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                execution_context
            ))
        if not isinstance(index, Number):
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                execution_context
            ))
        try:
            element = list_.elements.pop(index.value)
        except:
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "Index out of bounds", execution_context))
        return rt_result.success(element)
    execute_pop.arg_names = ['list', 'index']

    def execute_extend(self, execution_context, rt_result):
        list1 = execution_context.symbol_table.get("list1")
        list2 = execution_context.symbol_table.get("list2")
        if not isinstance(list1, List):
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                execution_context
            ))
        if not isinstance(list2, List):
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                execution_context
            ))
        list1.elements.extend(list2.elements)
        return rt_result.success(Number.null)
    execute_extend.arg_names = ['list1', 'list2']

    def execute_len(self, execution_context, rt_result):
        list_ = execution_context.symbol_table.get("list")
        if not isinstance(list_, List):
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be list",
                execution_context
            ))
        return rt_result.success(Number(len(list_.elements)))
    execute_len.arg_names = ['list']

    def execute_run(self, execution_context, rt_result, run):
        fn = execution_context.symbol_table.get("fn")
        if not isinstance(fn, String):
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be string",
                execution_context
            ))
        fn = fn.value
        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{fn}\"\n" + str(e),
                execution_context
            ))
        _, error, context = run(fn, script)
        if error:
            return rt_result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script \"{fn}\"\n" + error.as_string(),
                execution_context
            ))
        if context:
            execution_context.print_symbol_table()
            

        return rt_result.success(Number.null)

    execute_run.arg_names = ['fn'] 

BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.input_float = BuiltInFunction("input_float")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.run = BuiltInFunction("run")

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return
    
    def execute(self, args, interpreter, rt_result, run=None):
        res = rt_result
        execution_context = self.generate_new_context()
        self.context = execution_context  # Ensure the function context is set
        
        res.register(self.check_and_populate_args(self.arg_names, args, execution_context, rt_result))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, execution_context, run))
        if res.should_return() and res.func_return_value is None: return res
        
        ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
        execution_context.print_symbol_table()
        return res.success(ret_value)
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<function {self.name}>"
