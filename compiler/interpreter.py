from compiler.tokens import TOKENS
from modules.list import List
from modules.errors import RTError
from modules.function import Function
from modules.value import Number
from modules.value import String

###############################
# RUNTIME RESULT
###############################
class RTResult:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value
    
    def success(self, value=None):
        self.reset()
        self.value = value
        return self
    
    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self
    
    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self
    
    def should_return(self):
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )

###############################
# INTERPRETER (VCI)
###############################
class Interpreter:
    def visit(self, node, context, run=None):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context, run)
    
    def no_visit_method(self, node, context, run=None):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self, node, context, run=None):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_StringNode(self, node, context, run=None):
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node, context, run=None):
        res = RTResult()
        elements = []
        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context, run)))
            if res.should_return(): return res
        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context, run=None):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)
        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context, run=None):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context, run))
        if res.should_return(): return res

        if node.declaration:
            if context.symbol_table.get(var_name):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"Variable '{var_name}' already declared",
                    context
                ))
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context, run=None):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context, run))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context, run))
        if res.should_return(): return res
        error = None
        if node.op_tok.type == TOKENS['TT_PLUS']:
            result, error = left.added_to(right)
        elif node.op_tok.type == TOKENS['TT_MINUS']:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TOKENS['TT_MUL']:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TOKENS['TT_DIV']:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TOKENS['TT_MOD']:
            result, error = left.modded_by(right)
        elif node.op_tok.type == TOKENS['TT_POW']:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TOKENS['TT_EE']:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TOKENS['TT_NE']:
            result, error = left.get_comparison_ne(right)   
        elif node.op_tok.type == TOKENS['TT_LT']:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TOKENS['TT_GT']:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TOKENS['TT_LTE']:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TOKENS['TT_GTE']:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TOKENS['TT_KEYWORD'], 'AND'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TOKENS['TT_KEYWORD'], 'OR'):
            result, error = left.ored_by(right)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context, run=None):
        res = RTResult()
        number = res.register(self.visit(node.node, context, run))
        if res.should_return(): return res

        error = None
        if node.op_tok.type == TOKENS['TT_MINUS']:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TOKENS['TT_KEYWORD'], 'NOT'):
            number, error = number.notted()
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
        
    def visit_IfNode(self, node, context, run=None):
        res = RTResult()
        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context, run))
            if res.should_return(): return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context, run))
                if res.should_return(): return res
                return res.success(Number.null if should_return_null else expr_value)
        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit(expr, context, run))
            if res.should_return(): return res
            return res.success(Number.null if should_return_null else expr_value)
        return res.success(Number.null)
    
    def visit_ForNode(self, node, context, run=None):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context, run))
        if res.should_return(): return res
        
        end_value = res.register(self.visit(node.end_value_node, context, run))
        if res.should_return(): return res
        
        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context, run))
            if res.should_return(): return res
        else:
            step_value = Number(1)
        
        i = start_value.value
        
        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value
        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            value = res.register(self.visit(node.body_node, context, run))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
            if res.loop_should_continue: continue
            if res.loop_should_break: break
            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_WhileNode(self, node, context, run=None):
        res = RTResult()
        elements = []
        
        while True:
            condition = res.register(self.visit(node.condition_node, context, run))
            if res.should_return(): return res

            if not condition.is_true(): break

            value = res.register(self.visit(node.body_node, context, run))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
            if res.loop_should_continue: continue
            if res.loop_should_break: break
            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_FuncDefNode(self, node, context, run=None):
        res = RTResult()
        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)
        return res.success(func_value)
    
    def visit_CallNode(self, node, context, run=None):
        res = RTResult()
        args = []
        value_to_call = res.register(self.visit(node.node_to_call, context, run))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
        
        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context, run)))
            if res.should_return(): return res
        
        return_value = res.register(value_to_call.execute(args, self, res, run))
        if res.should_return(): return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)
    
    def visit_ReturnNode(self, node, context, run=None):
        res = RTResult()
        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context, run))
            if res.should_return(): return res
        else:
            print("HOLA")
            value = Number.null
        return res.success_return(value)
    
    def visit_ContinueNode(self, node, context, run=None):
        return RTResult().success_continue()
    
    def visit_BreakNode(self, node, context, run=None):
        return RTResult().success_break()