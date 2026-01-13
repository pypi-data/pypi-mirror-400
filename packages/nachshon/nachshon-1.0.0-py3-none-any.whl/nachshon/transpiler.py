# transpiler.py
# Convert Nachshon AST to Python code
# ממיר עץ תחביר נחשון לקוד פייתון

from typing import List, Dict, Optional

try:
    from .parser import (
        ASTNode, NodeType, ProgramNode, FunctionDefNode, ClassDefNode,
        IfStatementNode, WhileStatementNode, ForStatementNode,
        ReturnStatementNode, BreakStatementNode, ContinueStatementNode,
        PassStatementNode, AssignmentNode, AugmentedAssignmentNode,
        ExpressionStatementNode, BinaryOpNode, UnaryOpNode, ComparisonNode,
        LogicalOpNode, CallNode, IdentifierNode, NumberNode, StringNode,
        BooleanNode, NoneNode, ListNode, DictNode, IndexNode, AttributeNode,
        ImportNode, TryExceptNode, WithStatementNode, LambdaNode, ListCompNode, SliceNode,
        TernaryNode
    )
except ImportError:
    from nachshon.parser import (
        ASTNode, NodeType, ProgramNode, FunctionDefNode, ClassDefNode,
        IfStatementNode, WhileStatementNode, ForStatementNode,
        ReturnStatementNode, BreakStatementNode, ContinueStatementNode,
        PassStatementNode, AssignmentNode, AugmentedAssignmentNode,
        ExpressionStatementNode, BinaryOpNode, UnaryOpNode, ComparisonNode,
        LogicalOpNode, CallNode, IdentifierNode, NumberNode, StringNode,
        BooleanNode, NoneNode, ListNode, DictNode, IndexNode, AttributeNode,
        ImportNode, TryExceptNode, WithStatementNode, LambdaNode, ListCompNode, SliceNode,
        TernaryNode
    )


# Mapping Hebrew built-in functions to Python
BUILTIN_MAPPING = {
    'הדפס': 'print',
    'קלט': 'input',
    'אורך': 'len',
    'סוג': 'type',
    'טווח': 'range',
    'מספר_שלם': 'int',
    'מספר_עשרוני': 'float',
    'מחרוזת': 'str',
    'רשימה': 'list',
    'מילון': 'dict',
    'קבוצה': 'set',
    'בוליאני': 'bool',
    'ערך_מוחלט': 'abs',
    'סכום': 'sum',
    'מינימום': 'min',
    'מקסימום': 'max',
    'ממוין': 'sorted',
    'הפוך': 'reversed',
    'מספר_אינדקס': 'enumerate',
    'צמד': 'zip',
    'מפה': 'map',
    'סנן': 'filter',
    'פתח': 'open',
}

# Mapping Hebrew magic methods to Python
MAGIC_METHOD_MAPPING = {
    '__אתחל__': '__init__',
    '__מחרוזת__': '__str__',
    '__ייצוג__': '__repr__',
    '__אורך__': '__len__',
    '__קרא__': '__call__',
    '__השווה__': '__eq__',
    '__לא_שווה__': '__ne__',
    '__גדול__': '__gt__',
    '__קטן__': '__lt__',
    '__גדול_שווה__': '__ge__',
    '__קטן_שווה__': '__le__',
    '__חיבור__': '__add__',
    '__חיסור__': '__sub__',
    '__כפל__': '__mul__',
    '__חילוק__': '__truediv__',
    '__מודולו__': '__mod__',
    '__חזקה__': '__pow__',
    '__פריט__': '__getitem__',
    '__הגדר_פריט__': '__setitem__',
    '__מחק_פריט__': '__delitem__',
    '__מכיל__': '__contains__',
    '__איטרטור__': '__iter__',
    '__הבא__': '__next__',
    '__כניסה__': '__enter__',
    '__יציאה__': '__exit__',
}


class TranspilerError(Exception):
    """Error during transpilation - שגיאת המרה"""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"שגיאת המרה בשורה {line}: {message}" if line else f"שגיאת המרה: {message}")


class Transpiler:
    """Transpiler from Nachshon AST to Python code - ממיר מנחשון לפייתון"""
    
    def __init__(self, ast: ProgramNode):
        self.ast = ast
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces
        self.local_scopes = []  # Stack of sets tracking local variables in each scope
    
    def push_scope(self, variables: list = None):
        """Push a new scope with optional initial variables (e.g., function parameters)"""
        self.local_scopes.append(set(variables or []))
    
    def pop_scope(self):
        """Pop the current scope"""
        if self.local_scopes:
            self.local_scopes.pop()
    
    def add_local(self, name: str):
        """Add a variable to the current scope"""
        if self.local_scopes:
            self.local_scopes[-1].add(name)
    
    def is_local(self, name: str) -> bool:
        """Check if a name is defined as a local variable in any active scope"""
        for scope in self.local_scopes:
            if name in scope:
                return True
        return False
    
    def indent(self) -> str:
        """Return current indentation string"""
        return self.indent_str * self.indent_level
    
    def transpile(self) -> str:
        """Transpile the entire program to Python code"""
        lines = []
        
        # Add encoding comment and helper imports
        lines.append("# -*- coding: utf-8 -*-")
        lines.append("# קוד זה נוצר אוטומטית מנחשון")
        lines.append("# This code was auto-generated from Nachshon")
        lines.append("")
        
        # Push module-level scope
        self.push_scope()
        
        for node in self.ast.body:
            code = self.transpile_node(node)
            if code:
                lines.append(code)
        
        # Pop module-level scope
        self.pop_scope()
        
        return '\n'.join(lines)
    
    def transpile_node(self, node: ASTNode) -> str:
        """Transpile a single AST node"""
        if isinstance(node, FunctionDefNode):
            return self.transpile_function_def(node)
        elif isinstance(node, ClassDefNode):
            return self.transpile_class_def(node)
        elif isinstance(node, IfStatementNode):
            return self.transpile_if_statement(node)
        elif isinstance(node, WhileStatementNode):
            return self.transpile_while_statement(node)
        elif isinstance(node, ForStatementNode):
            return self.transpile_for_statement(node)
        elif isinstance(node, ReturnStatementNode):
            return self.transpile_return_statement(node)
        elif isinstance(node, BreakStatementNode):
            return f"{self.indent()}break"
        elif isinstance(node, ContinueStatementNode):
            return f"{self.indent()}continue"
        elif isinstance(node, PassStatementNode):
            return f"{self.indent()}pass"
        elif isinstance(node, AssignmentNode):
            return self.transpile_assignment(node)
        elif isinstance(node, AugmentedAssignmentNode):
            return self.transpile_augmented_assignment(node)
        elif isinstance(node, ExpressionStatementNode):
            return f"{self.indent()}{self.transpile_expression(node.expression)}"
        elif isinstance(node, ImportNode):
            return self.transpile_import(node)
        elif isinstance(node, TryExceptNode):
            return self.transpile_try_except(node)
        elif isinstance(node, WithStatementNode):
            return self.transpile_with_statement(node)
        else:
            raise TranspilerError(f"צומת לא מוכר: {type(node).__name__}", 
                                 node.line if hasattr(node, 'line') else 0)
    
    def transpile_function_def(self, node: FunctionDefNode) -> str:
        """Transpile function definition"""
        lines = []
        
        # Add decorators
        for decorator in node.decorators:
            decorator_str = self.transpile_expression(decorator)
            lines.append(f"{self.indent()}@{decorator_str}")
        
        # Push scope with function parameters
        self.push_scope(node.params)
        
        # Build parameter list with defaults
        params = []
        num_defaults = len(node.defaults)
        num_regular = len(node.params) - num_defaults
        
        for i, param in enumerate(node.params):
            # Translate עצמי to self
            param_name = 'self' if param == 'עצמי' else param
            if i >= num_regular and node.defaults:
                default_idx = i - num_regular
                default_val = self.transpile_expression(node.defaults[default_idx])
                params.append(f"{param_name}={default_val}")
            else:
                params.append(param_name)
        
        # Translate magic method names
        func_name = MAGIC_METHOD_MAPPING.get(node.name, node.name)
        
        params_str = ', '.join(params)
        lines.append(f"{self.indent()}def {func_name}({params_str}):")
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self.indent()}pass")
        else:
            for stmt in node.body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        # Pop scope when done with function
        self.pop_scope()
        
        return '\n'.join(lines)
    
    def transpile_class_def(self, node: ClassDefNode) -> str:
        """Transpile class definition"""
        lines = []
        
        if node.base:
            lines.append(f"{self.indent()}class {node.name}({node.base}):")
        else:
            lines.append(f"{self.indent()}class {node.name}:")
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self.indent()}pass")
        else:
            for stmt in node.body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def transpile_if_statement(self, node: IfStatementNode) -> str:
        """Transpile if statement"""
        lines = []
        
        condition = self.transpile_expression(node.condition)
        lines.append(f"{self.indent()}if {condition}:")
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self.indent()}pass")
        else:
            for stmt in node.body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        # Elif clauses
        for elif_cond, elif_body in node.elif_clauses:
            elif_cond_str = self.transpile_expression(elif_cond)
            lines.append(f"{self.indent()}elif {elif_cond_str}:")
            
            self.indent_level += 1
            if not elif_body:
                lines.append(f"{self.indent()}pass")
            else:
                for stmt in elif_body:
                    code = self.transpile_node(stmt)
                    if code:
                        lines.append(code)
            self.indent_level -= 1
        
        # Else clause
        if node.else_body:
            lines.append(f"{self.indent()}else:")
            self.indent_level += 1
            for stmt in node.else_body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
            self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def transpile_while_statement(self, node: WhileStatementNode) -> str:
        """Transpile while statement"""
        lines = []
        
        condition = self.transpile_expression(node.condition)
        lines.append(f"{self.indent()}while {condition}:")
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self.indent()}pass")
        else:
            for stmt in node.body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def transpile_for_statement(self, node: ForStatementNode) -> str:
        """Transpile for statement"""
        lines = []
        
        # Add loop variable to current scope
        self.add_local(node.variable)
        
        iterable = self.transpile_expression(node.iterable)
        lines.append(f"{self.indent()}for {node.variable} in {iterable}:")
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self.indent()}pass")
        else:
            for stmt in node.body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def transpile_return_statement(self, node: ReturnStatementNode) -> str:
        """Transpile return statement"""
        if node.value:
            value = self.transpile_expression(node.value)
            return f"{self.indent()}return {value}"
        return f"{self.indent()}return"
    
    def transpile_assignment(self, node: AssignmentNode) -> str:
        """Transpile assignment"""
        target = self.transpile_expression(node.target)
        value = self.transpile_expression(node.value)
        return f"{self.indent()}{target} = {value}"
    
    def transpile_augmented_assignment(self, node: AugmentedAssignmentNode) -> str:
        """Transpile augmented assignment"""
        target = self.transpile_expression(node.target)
        value = self.transpile_expression(node.value)
        return f"{self.indent()}{target} {node.op} {value}"
    
    def transpile_import(self, node: ImportNode) -> str:
        """Transpile import statement"""
        if node.from_module:
            # from X import Y
            names = []
            for name, alias in node.names:
                if alias:
                    names.append(f"{name} as {alias}")
                else:
                    names.append(name)
            names_str = ', '.join(names)
            return f"{self.indent()}from {node.from_module} import {names_str}"
        else:
            # import X
            if node.alias:
                return f"{self.indent()}import {node.module} as {node.alias}"
            return f"{self.indent()}import {node.module}"
    
    def transpile_try_except(self, node: TryExceptNode) -> str:
        """Transpile try-except statement"""
        lines = []
        
        lines.append(f"{self.indent()}try:")
        self.indent_level += 1
        for stmt in node.try_body:
            code = self.transpile_node(stmt)
            if code:
                lines.append(code)
        self.indent_level -= 1
        
        for exc_type, exc_var, exc_body in node.except_clauses:
            if exc_type and exc_var:
                lines.append(f"{self.indent()}except {exc_type} as {exc_var}:")
            elif exc_type:
                lines.append(f"{self.indent()}except {exc_type}:")
            else:
                lines.append(f"{self.indent()}except:")
            
            self.indent_level += 1
            for stmt in exc_body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
            self.indent_level -= 1
        
        if node.finally_body:
            lines.append(f"{self.indent()}finally:")
            self.indent_level += 1
            for stmt in node.finally_body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
            self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def transpile_with_statement(self, node: WithStatementNode) -> str:
        """Transpile with statement"""
        lines = []
        
        context = self.transpile_expression(node.context)
        if node.target:
            lines.append(f"{self.indent()}with {context} as {node.target}:")
        else:
            lines.append(f"{self.indent()}with {context}:")
        
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self.indent()}pass")
        else:
            for stmt in node.body:
                code = self.transpile_node(stmt)
                if code:
                    lines.append(code)
        self.indent_level -= 1
        
        return '\n'.join(lines)
    
    def transpile_expression(self, node: ASTNode) -> str:
        """Transpile an expression node"""
        if isinstance(node, BinaryOpNode):
            left = self.transpile_expression(node.left)
            right = self.transpile_expression(node.right)
            return f"({left} {node.op} {right})"
        
        elif isinstance(node, UnaryOpNode):
            operand = self.transpile_expression(node.operand)
            if node.op == 'not':
                return f"(not {operand})"
            return f"({node.op}{operand})"
        
        elif isinstance(node, ComparisonNode):
            result = self.transpile_expression(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                comp = self.transpile_expression(comparator)
                result += f" {op} {comp}"
            return f"({result})"
        
        elif isinstance(node, LogicalOpNode):
            left = self.transpile_expression(node.left)
            right = self.transpile_expression(node.right)
            return f"({left} {node.op} {right})"
        
        elif isinstance(node, TernaryNode):
            true_val = self.transpile_expression(node.true_value)
            condition = self.transpile_expression(node.condition)
            false_val = self.transpile_expression(node.false_value)
            return f"({true_val} if {condition} else {false_val})"
        
        elif isinstance(node, CallNode):
            return self.transpile_call(node)
        
        elif isinstance(node, IdentifierNode):
            # Map Hebrew built-in names to Python
            name = node.name
            # Translate עצמי to self
            if name == 'עצמי':
                return 'self'
            # Only map to builtin if NOT a local variable
            if name in BUILTIN_MAPPING and not self.is_local(name):
                return BUILTIN_MAPPING[name]
            return name
        
        elif isinstance(node, NumberNode):
            return str(node.value)
        
        elif isinstance(node, StringNode):
            # Escape special characters properly for Python output
            escaped = node.value.replace('\\', '\\\\')  # Backslash first
            escaped = escaped.replace('\n', '\\n')      # Newlines
            escaped = escaped.replace('\t', '\\t')      # Tabs
            escaped = escaped.replace('\r', '\\r')      # Carriage returns
            escaped = escaped.replace('"', '\\"')       # Double quotes
            return f'"{escaped}"'
        
        elif isinstance(node, BooleanNode):
            return 'True' if node.value else 'False'
        
        elif isinstance(node, NoneNode):
            return 'None'
        
        elif isinstance(node, ListNode):
            elements = [self.transpile_expression(e) for e in node.elements]
            return f"[{', '.join(elements)}]"
        
        elif isinstance(node, DictNode):
            pairs = [f"{self.transpile_expression(k)}: {self.transpile_expression(v)}" 
                    for k, v in node.pairs]
            return f"{{{', '.join(pairs)}}}"
        
        elif isinstance(node, IndexNode):
            obj = self.transpile_expression(node.obj)
            index = self.transpile_expression(node.index)
            return f"{obj}[{index}]"
        
        elif isinstance(node, SliceNode):
            obj = self.transpile_expression(node.obj)
            start = self.transpile_expression(node.start) if node.start else ""
            end = self.transpile_expression(node.end) if node.end else ""
            if node.step:
                step = self.transpile_expression(node.step)
                return f"{obj}[{start}:{end}:{step}]"
            return f"{obj}[{start}:{end}]"
        
        elif isinstance(node, AttributeNode):
            obj = self.transpile_expression(node.obj)
            return f"{obj}.{node.attr}"
        
        elif isinstance(node, LambdaNode):
            params = ', '.join(node.params)
            body = self.transpile_expression(node.body)
            return f"(lambda {params}: {body})"
        
        elif isinstance(node, ListCompNode):
            element = self.transpile_expression(node.element)
            iterable = self.transpile_expression(node.iterable)
            if node.condition:
                condition = self.transpile_expression(node.condition)
                return f"[{element} for {node.variable} in {iterable} if {condition}]"
            return f"[{element} for {node.variable} in {iterable}]"
        
        else:
            raise TranspilerError(f"ביטוי לא מוכר: {type(node).__name__}")
    
    def transpile_call(self, node: CallNode) -> str:
        """Transpile function call"""
        callee = self.transpile_expression(node.callee)
        
        # Transpile positional arguments
        args = [self.transpile_expression(arg) for arg in node.args]
        
        # Transpile keyword arguments
        for key, value in node.kwargs.items():
            args.append(f"{key}={self.transpile_expression(value)}")
        
        return f"{callee}({', '.join(args)})"


def transpile(code: str) -> str:
    """Convenience function to transpile Nachshon code to Python"""
    try:
        from .lexer import Lexer
        from .parser import Parser
    except ImportError:
        from nachshon.lexer import Lexer
        from nachshon.parser import Parser
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    transpiler = Transpiler(ast)
    return transpiler.transpile()


if __name__ == "__main__":
    # Test the transpiler
    test_code = '''הגדר שלום(שם):
    הדפס("שלום, " + שם)
    החזר אמת

אם 5 > 3:
    הדפס("חמש גדול משלוש")
אחרת:
    הדפס("לא ייתכן")

עבור i בתוך טווח(5):
    הדפס(i)

שלום("עולם")
'''
    
    try:
        python_code = transpile(test_code)
        print("=== קוד פייתון שנוצר ===")
        print(python_code)
        print("\n=== הרצת הקוד ===")
        exec(python_code)
    except Exception as e:
        print(f"שגיאה: {e}")
