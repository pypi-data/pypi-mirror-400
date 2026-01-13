# parser.py
# Parser for Nachshon language - converts tokens to AST
# מנתח תחבירי לשפת נחשון - ממיר טוקנים לעץ תחביר מופשט

from dataclasses import dataclass, field
from typing import List, Optional, Any, Union
from enum import Enum, auto

try:
    from .lexer import Token, TokenType, Lexer, LexerError
except ImportError:
    from nachshon.lexer import Token, TokenType, Lexer, LexerError

# Built-in function tokens that can also be used as identifiers (variable/parameter names)
# טוקנים של פונקציות מובנות שיכולים לשמש גם כשמות משתנים/פרמטרים
BUILTIN_FUNCTION_TOKENS = {
    TokenType.PRINT, TokenType.INPUT, TokenType.LEN, TokenType.TYPE,
    TokenType.RANGE, TokenType.INT, TokenType.FLOAT, TokenType.STR,
    TokenType.LIST, TokenType.DICT, TokenType.SET, TokenType.BOOL,
    TokenType.ABS, TokenType.SUM, TokenType.MIN, TokenType.MAX,
    TokenType.SORTED, TokenType.REVERSED, TokenType.ENUMERATE,
    TokenType.ZIP, TokenType.MAP, TokenType.FILTER, TokenType.OPEN,
}

# Tokens that can be used as attribute/method names (after a dot)
# These include builtins plus keywords that might be used as method names
ATTRIBUTE_TOKENS = BUILTIN_FUNCTION_TOKENS | {
    TokenType.NONE,  # ריק - can be a method name
    TokenType.TRUE,  # אמת
    TokenType.FALSE, # שקר
}


class NodeType(Enum):
    """AST Node types - סוגי צמתים בעץ התחביר"""
    PROGRAM = auto()
    FUNCTION_DEF = auto()
    CLASS_DEF = auto()
    IF_STATEMENT = auto()
    WHILE_STATEMENT = auto()
    FOR_STATEMENT = auto()
    RETURN_STATEMENT = auto()
    BREAK_STATEMENT = auto()
    CONTINUE_STATEMENT = auto()
    PASS_STATEMENT = auto()
    ASSIGNMENT = auto()
    AUGMENTED_ASSIGNMENT = auto()
    EXPRESSION_STATEMENT = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    COMPARISON = auto()
    LOGICAL_OP = auto()
    TERNARY = auto()
    CALL = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NONE = auto()
    LIST = auto()
    DICT = auto()
    INDEX = auto()
    ATTRIBUTE = auto()
    IMPORT = auto()
    TRY_EXCEPT = auto()
    RAISE = auto()
    WITH_STATEMENT = auto()
    ASSERT = auto()
    LAMBDA = auto()
    LIST_COMP = auto()
    SLICE = auto()


@dataclass
class ASTNode:
    """Base AST Node"""
    type: NodeType
    line: int = 0
    column: int = 0


@dataclass
class ProgramNode(ASTNode):
    """Root node containing all statements"""
    body: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, body: List[ASTNode] = None):
        super().__init__(NodeType.PROGRAM)
        self.body = body or []


@dataclass
class FunctionDefNode(ASTNode):
    """Function definition - הגדרת פונקציה"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    defaults: List[ASTNode] = field(default_factory=list)
    decorators: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, name: str, params: List[str], body: List[ASTNode], 
                 defaults: List[ASTNode] = None, decorators: List[ASTNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.FUNCTION_DEF, line, column)
        self.name = name
        self.params = params
        self.body = body
        self.defaults = defaults or []
        self.decorators = decorators or []


@dataclass
class ClassDefNode(ASTNode):
    """Class definition - הגדרת מחלקה"""
    name: str = ""
    base: Optional[str] = None
    body: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, name: str, body: List[ASTNode], base: str = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.CLASS_DEF, line, column)
        self.name = name
        self.base = base
        self.body = body


@dataclass
class IfStatementNode(ASTNode):
    """If statement - משפט אם"""
    condition: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)
    elif_clauses: List[tuple] = field(default_factory=list)  # List of (condition, body) tuples
    else_body: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, condition: ASTNode, body: List[ASTNode], 
                 elif_clauses: List[tuple] = None, else_body: List[ASTNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.IF_STATEMENT, line, column)
        self.condition = condition
        self.body = body
        self.elif_clauses = elif_clauses or []
        self.else_body = else_body or []


@dataclass
class WhileStatementNode(ASTNode):
    """While loop - לולאת בעוד"""
    condition: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, condition: ASTNode, body: List[ASTNode],
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.WHILE_STATEMENT, line, column)
        self.condition = condition
        self.body = body


@dataclass
class ForStatementNode(ASTNode):
    """For loop - לולאת עבור"""
    variable: str = ""
    iterable: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, variable: str, iterable: ASTNode, body: List[ASTNode],
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.FOR_STATEMENT, line, column)
        self.variable = variable
        self.iterable = iterable
        self.body = body


@dataclass
class ReturnStatementNode(ASTNode):
    """Return statement - החזר"""
    value: Optional[ASTNode] = None
    
    def __init__(self, value: ASTNode = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.RETURN_STATEMENT, line, column)
        self.value = value


@dataclass
class BreakStatementNode(ASTNode):
    """Break statement - הפסק"""
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(NodeType.BREAK_STATEMENT, line, column)


@dataclass
class ContinueStatementNode(ASTNode):
    """Continue statement - המשך"""
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(NodeType.CONTINUE_STATEMENT, line, column)


@dataclass
class PassStatementNode(ASTNode):
    """Pass statement - עבור_הלאה"""
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(NodeType.PASS_STATEMENT, line, column)


@dataclass
class AssignmentNode(ASTNode):
    """Variable assignment - השמה"""
    target: ASTNode = None
    value: ASTNode = None
    
    def __init__(self, target: ASTNode, value: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.target = target
        self.value = value


@dataclass
class AugmentedAssignmentNode(ASTNode):
    """Augmented assignment (+=, -=, etc.)"""
    target: ASTNode = None
    op: str = ""
    value: ASTNode = None
    
    def __init__(self, target: ASTNode, op: str, value: ASTNode, 
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.AUGMENTED_ASSIGNMENT, line, column)
        self.target = target
        self.op = op
        self.value = value


@dataclass
class ExpressionStatementNode(ASTNode):
    """Expression used as statement"""
    expression: ASTNode = None
    
    def __init__(self, expression: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.EXPRESSION_STATEMENT, line, column)
        self.expression = expression


@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation - פעולה בינארית"""
    left: ASTNode = None
    op: str = ""
    right: ASTNode = None
    
    def __init__(self, left: ASTNode, op: str, right: ASTNode,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.BINARY_OP, line, column)
        self.left = left
        self.op = op
        self.right = right


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation - פעולה אונרית"""
    op: str = ""
    operand: ASTNode = None
    
    def __init__(self, op: str, operand: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.UNARY_OP, line, column)
        self.op = op
        self.operand = operand


@dataclass
class ComparisonNode(ASTNode):
    """Comparison operation - השוואה"""
    left: ASTNode = None
    ops: List[str] = field(default_factory=list)
    comparators: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, left: ASTNode, ops: List[str], comparators: List[ASTNode],
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.COMPARISON, line, column)
        self.left = left
        self.ops = ops
        self.comparators = comparators


@dataclass
class LogicalOpNode(ASTNode):
    """Logical operation (and, or) - פעולה לוגית"""
    left: ASTNode = None
    op: str = ""
    right: ASTNode = None
    
    def __init__(self, left: ASTNode, op: str, right: ASTNode,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.LOGICAL_OP, line, column)
        self.left = left
        self.op = op
        self.right = right


@dataclass
class CallNode(ASTNode):
    """Function call - קריאה לפונקציה"""
    callee: ASTNode = None
    args: List[ASTNode] = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)
    
    def __init__(self, callee: ASTNode, args: List[ASTNode], kwargs: dict = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.CALL, line, column)
        self.callee = callee
        self.args = args
        self.kwargs = kwargs or {}


@dataclass
class IdentifierNode(ASTNode):
    """Identifier - מזהה"""
    name: str = ""
    
    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name


@dataclass
class NumberNode(ASTNode):
    """Number literal - מספר"""
    value: Union[int, float] = 0
    
    def __init__(self, value: Union[int, float], line: int = 0, column: int = 0):
        super().__init__(NodeType.NUMBER, line, column)
        self.value = value


@dataclass
class StringNode(ASTNode):
    """String literal - מחרוזת"""
    value: str = ""
    
    def __init__(self, value: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.STRING, line, column)
        self.value = value


@dataclass
class BooleanNode(ASTNode):
    """Boolean literal - בוליאני"""
    value: bool = False
    
    def __init__(self, value: bool, line: int = 0, column: int = 0):
        super().__init__(NodeType.BOOLEAN, line, column)
        self.value = value


@dataclass
class NoneNode(ASTNode):
    """None literal - ריק"""
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(NodeType.NONE, line, column)


@dataclass
class ListNode(ASTNode):
    """List literal - רשימה"""
    elements: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, elements: List[ASTNode], line: int = 0, column: int = 0):
        super().__init__(NodeType.LIST, line, column)
        self.elements = elements


@dataclass
class DictNode(ASTNode):
    """Dictionary literal - מילון"""
    pairs: List[tuple] = field(default_factory=list)
    
    def __init__(self, pairs: List[tuple], line: int = 0, column: int = 0):
        super().__init__(NodeType.DICT, line, column)
        self.pairs = pairs


@dataclass
class IndexNode(ASTNode):
    """Index/subscript access - גישה באינדקס"""
    obj: ASTNode = None
    index: ASTNode = None
    
    def __init__(self, obj: ASTNode, index: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.INDEX, line, column)
        self.obj = obj
        self.index = index


@dataclass
class SliceNode(ASTNode):
    """Slice access - גישה בחיתוך"""
    obj: ASTNode = None
    start: Optional[ASTNode] = None
    end: Optional[ASTNode] = None
    step: Optional[ASTNode] = None
    
    def __init__(self, obj: ASTNode, start: ASTNode = None, end: ASTNode = None, 
                 step: ASTNode = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.SLICE, line, column)
        self.obj = obj
        self.start = start
        self.end = end
        self.step = step


@dataclass
class AttributeNode(ASTNode):
    """Attribute access - גישה לתכונה"""
    obj: ASTNode = None
    attr: str = ""
    
    def __init__(self, obj: ASTNode, attr: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.ATTRIBUTE, line, column)
        self.obj = obj
        self.attr = attr


@dataclass
class ImportNode(ASTNode):
    """Import statement - ייבוא"""
    module: str = ""
    alias: Optional[str] = None
    from_module: Optional[str] = None
    names: List[tuple] = field(default_factory=list)  # List of (name, alias) tuples
    
    def __init__(self, module: str = "", alias: str = None, from_module: str = None,
                 names: List[tuple] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.IMPORT, line, column)
        self.module = module
        self.alias = alias
        self.from_module = from_module
        self.names = names or []


@dataclass
class TryExceptNode(ASTNode):
    """Try-except statement - נסה-תפוס"""
    try_body: List[ASTNode] = field(default_factory=list)
    except_clauses: List[tuple] = field(default_factory=list)
    finally_body: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, try_body: List[ASTNode], except_clauses: List[tuple] = None,
                 finally_body: List[ASTNode] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.TRY_EXCEPT, line, column)
        self.try_body = try_body
        self.except_clauses = except_clauses or []
        self.finally_body = finally_body or []


@dataclass
class WithStatementNode(ASTNode):
    """With statement - עם"""
    context: ASTNode = None
    target: Optional[str] = None
    body: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, context: ASTNode, body: List[ASTNode], target: str = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.WITH_STATEMENT, line, column)
        self.context = context
        self.target = target
        self.body = body


@dataclass
class LambdaNode(ASTNode):
    """Lambda expression - פונקציה אנונימית"""
    params: List[str] = field(default_factory=list)
    body: ASTNode = None
    
    def __init__(self, params: List[str], body: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.LAMBDA, line, column)
        self.params = params
        self.body = body


@dataclass
class ListCompNode(ASTNode):
    """List comprehension - הבנת רשימה"""
    element: ASTNode = None  # The expression to evaluate
    variable: str = ""       # The loop variable
    iterable: ASTNode = None # The iterable
    condition: Optional[ASTNode] = None  # Optional if condition
    
    def __init__(self, element: ASTNode, variable: str, iterable: ASTNode,
                 condition: ASTNode = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.LIST_COMP, line, column)
        self.element = element
        self.variable = variable
        self.iterable = iterable
        self.condition = condition


@dataclass
class TernaryNode(ASTNode):
    """Ternary conditional expression - ביטוי תנאי (value אם condition אחרת alternative)"""
    true_value: ASTNode = None   # The value if condition is true
    condition: ASTNode = None    # The condition to evaluate
    false_value: ASTNode = None  # The value if condition is false
    
    def __init__(self, true_value: ASTNode, condition: ASTNode, false_value: ASTNode,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.TERNARY, line, column)
        self.true_value = true_value
        self.condition = condition
        self.false_value = false_value


class ParserError(Exception):
    """Error during parsing - שגיאת ניתוח תחבירי"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"שגיאה בשורה {line}, עמודה {column}: {message}")


class Parser:
    """Parser for Nachshon language - מנתח תחבירי לשפת נחשון"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        """Get current token"""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead without consuming"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.tokens):
            return None
        return self.tokens[peek_pos]
    
    def advance(self) -> Token:
        """Move to next token and return current"""
        token = self.current_token()
        self.pos += 1
        return token
    
    def expect(self, token_type: TokenType, message: str = None) -> Token:
        """Expect specific token type"""
        token = self.current_token()
        if token.type != token_type:
            msg = message or f"ציפיתי ל־{token_type.name}, אבל מצאתי {token.type.name}"
            raise ParserError(msg, token.line, token.column)
        return self.advance()
    
    def expect_identifier_or_builtin(self, message: str = None) -> Token:
        """Expect identifier or builtin function token (which can be used as identifier)"""
        token = self.current_token()
        if token.type == TokenType.IDENTIFIER or token.type in BUILTIN_FUNCTION_TOKENS:
            return self.advance()
        msg = message or f"ציפיתי לשם, אבל מצאתי {token.type.name}"
        raise ParserError(msg, token.line, token.column)
    
    def expect_attribute_name(self, message: str = None) -> Token:
        """Expect identifier or any token that can be used as attribute/method name"""
        token = self.current_token()
        if token.type == TokenType.IDENTIFIER or token.type in ATTRIBUTE_TOKENS:
            return self.advance()
        msg = message or f"ציפיתי לשם תכונה, אבל מצאתי {token.type.name}"
        raise ParserError(msg, token.line, token.column)
    
    def skip_newlines(self) -> None:
        """Skip newline tokens"""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> ProgramNode:
        """Parse entire program"""
        statements = []
        self.skip_newlines()
        
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return ProgramNode(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        token = self.current_token()
        
        # Handle decorators
        if token.type == TokenType.AT:
            return self.parse_decorated()
        elif token.type == TokenType.DEF:
            return self.parse_function_def()
        elif token.type == TokenType.CLASS:
            return self.parse_class_def()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif token.type == TokenType.BREAK:
            self.advance()
            return BreakStatementNode(token.line, token.column)
        elif token.type == TokenType.CONTINUE:
            self.advance()
            return ContinueStatementNode(token.line, token.column)
        elif token.type == TokenType.PASS:
            self.advance()
            return PassStatementNode(token.line, token.column)
        elif token.type == TokenType.IMPORT:
            return self.parse_import()
        elif token.type == TokenType.FROM:
            return self.parse_from_import()
        elif token.type == TokenType.TRY:
            return self.parse_try_except()
        elif token.type == TokenType.WITH:
            return self.parse_with_statement()
        elif token.type in (TokenType.NEWLINE, TokenType.DEDENT):
            self.advance()
            return None
        else:
            return self.parse_expression_or_assignment()
    
    def parse_function_def(self, decorators: List[ASTNode] = None) -> FunctionDefNode:
        """Parse function definition - הגדר"""
        token = self.expect(TokenType.DEF)
        name_token = self.expect_attribute_name("ציפיתי לשם פונקציה")
        name = name_token.value
        
        self.expect(TokenType.LPAREN, "ציפיתי ל־'('")
        params = []
        defaults = []
        
        while self.current_token().type != TokenType.RPAREN:
            # Check for *args or **kwargs
            prefix = ""
            if self.current_token().type == TokenType.MULTIPLY:
                self.advance()
                if self.current_token().type == TokenType.MULTIPLY:
                    self.advance()
                    prefix = "**"
                else:
                    prefix = "*"
            
            param_token = self.expect_identifier_or_builtin("ציפיתי לשם פרמטר")
            params.append(prefix + param_token.value)
            
            # Check for default value
            if self.current_token().type == TokenType.ASSIGN:
                self.advance()
                defaults.append(self.parse_expression())
            elif defaults:
                # After a default, all params must have defaults
                pass  # Python allows this, we'll let Python handle the error
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
        
        self.expect(TokenType.RPAREN, "ציפיתי ל־')'")
        self.expect(TokenType.COLON, "ציפיתי ל־':'")
        
        body = self.parse_block()
        
        return FunctionDefNode(name, params, body, defaults, decorators or [], 
                              token.line, token.column)
    
    def parse_decorated(self) -> FunctionDefNode:
        """Parse decorated function definition - @מעטר"""
        decorators = []
        
        # Collect all decorators
        while self.current_token().type == TokenType.AT:
            self.advance()  # consume @
            # Parse decorator expression (can be identifier or call)
            decorator = self.parse_expression()
            decorators.append(decorator)
            
            # Consume newline after decorator
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                self.skip_newlines()
        
        # After decorators, expect function or class definition
        if self.current_token().type == TokenType.DEF:
            return self.parse_function_def(decorators)
        else:
            raise ParserError("ציפיתי להגדרת פונקציה אחרי מעטר",
                            self.current_token().line, self.current_token().column)
    
    def parse_class_def(self) -> ClassDefNode:
        """Parse class definition - מחלקה"""
        token = self.expect(TokenType.CLASS)
        name_token = self.expect(TokenType.IDENTIFIER, "ציפיתי לשם מחלקה")
        name = name_token.value
        
        base = None
        if self.current_token().type == TokenType.LPAREN:
            self.advance()
            if self.current_token().type == TokenType.IDENTIFIER:
                base = self.advance().value
            self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.COLON, "ציפיתי ל־':'")
        body = self.parse_block()
        
        return ClassDefNode(name, body, base, token.line, token.column)
    
    def parse_if_statement(self) -> IfStatementNode:
        """Parse if statement - אם"""
        token = self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.COLON, "ציפיתי ל־':' אחרי תנאי")
        body = self.parse_block()
        
        elif_clauses = []
        else_body = []
        
        # Parse elif clauses
        while self.current_token().type == TokenType.ELIF:
            self.advance()
            elif_cond = self.parse_expression()
            self.expect(TokenType.COLON)
            elif_body = self.parse_block()
            elif_clauses.append((elif_cond, elif_body))
        
        # Parse else clause
        if self.current_token().type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.COLON)
            else_body = self.parse_block()
        
        return IfStatementNode(condition, body, elif_clauses, else_body, 
                               token.line, token.column)
    
    def parse_while_statement(self) -> WhileStatementNode:
        """Parse while statement - בעוד"""
        token = self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.COLON, "ציפיתי ל־':' אחרי תנאי")
        body = self.parse_block()
        
        return WhileStatementNode(condition, body, token.line, token.column)
    
    def parse_for_statement(self) -> ForStatementNode:
        """Parse for statement - עבור"""
        token = self.expect(TokenType.FOR)
        var_token = self.expect_identifier_or_builtin("ציפיתי לשם משתנה")
        variable = var_token.value
        
        self.expect(TokenType.IN, "ציפיתי ל־'בתוך'")
        iterable = self.parse_expression()
        self.expect(TokenType.COLON, "ציפיתי ל־':'")
        body = self.parse_block()
        
        return ForStatementNode(variable, iterable, body, token.line, token.column)
    
    def parse_return_statement(self) -> ReturnStatementNode:
        """Parse return statement - החזר"""
        token = self.expect(TokenType.RETURN)
        
        # Check if there's a value to return
        value = None
        if self.current_token().type not in (TokenType.NEWLINE, TokenType.EOF, 
                                             TokenType.DEDENT):
            value = self.parse_expression()
        
        return ReturnStatementNode(value, token.line, token.column)
    
    def parse_import(self) -> ImportNode:
        """Parse import statement - ייבא"""
        token = self.expect(TokenType.IMPORT)
        module_token = self.expect(TokenType.IDENTIFIER)
        module = module_token.value
        
        alias = None
        if self.current_token().type == TokenType.AS:
            self.advance()
            alias = self.expect(TokenType.IDENTIFIER).value
        
        return ImportNode(module=module, alias=alias, line=token.line, column=token.column)
    
    def parse_from_import(self) -> ImportNode:
        """Parse from-import statement - מתוך...ייבא"""
        token = self.expect(TokenType.FROM)
        module_token = self.expect(TokenType.IDENTIFIER)
        from_module = module_token.value
        
        self.expect(TokenType.IMPORT)
        
        names = []
        while True:
            name_token = self.expect(TokenType.IDENTIFIER)
            name = name_token.value
            alias = None
            
            if self.current_token().type == TokenType.AS:
                self.advance()
                alias = self.expect(TokenType.IDENTIFIER).value
            
            names.append((name, alias))
            
            if self.current_token().type != TokenType.COMMA:
                break
            self.advance()
        
        return ImportNode(from_module=from_module, names=names, 
                         line=token.line, column=token.column)
    
    def parse_try_except(self) -> TryExceptNode:
        """Parse try-except statement - נסה-תפוס"""
        token = self.expect(TokenType.TRY)
        self.expect(TokenType.COLON)
        try_body = self.parse_block()
        
        except_clauses = []
        while self.current_token().type == TokenType.EXCEPT:
            self.advance()
            exception_type = None
            exception_var = None
            
            if self.current_token().type == TokenType.IDENTIFIER:
                exception_type = self.advance().value
                if self.current_token().type == TokenType.AS:
                    self.advance()
                    exception_var = self.expect(TokenType.IDENTIFIER).value
            
            self.expect(TokenType.COLON)
            except_body = self.parse_block()
            except_clauses.append((exception_type, exception_var, except_body))
        
        finally_body = []
        if self.current_token().type == TokenType.FINALLY:
            self.advance()
            self.expect(TokenType.COLON)
            finally_body = self.parse_block()
        
        return TryExceptNode(try_body, except_clauses, finally_body,
                            token.line, token.column)
    
    def parse_with_statement(self) -> WithStatementNode:
        """Parse with statement - עם"""
        token = self.expect(TokenType.WITH)
        context = self.parse_expression()
        
        target = None
        if self.current_token().type == TokenType.AS:
            self.advance()
            target = self.expect(TokenType.IDENTIFIER, "ציפיתי לשם משתנה").value
        
        self.expect(TokenType.COLON, "ציפיתי ל־':'")
        body = self.parse_block()
        
        return WithStatementNode(context, body, target, token.line, token.column)
    
    def parse_block(self) -> List[ASTNode]:
        """Parse an indented block of statements"""
        self.skip_newlines()
        
        if self.current_token().type != TokenType.INDENT:
            # Single line block (error case, but we'll handle it)
            raise ParserError("ציפיתי לבלוק מוזח", 
                            self.current_token().line, self.current_token().column)
        
        self.advance()  # Skip INDENT
        
        statements = []
        while (self.current_token().type != TokenType.DEDENT and 
               self.current_token().type != TokenType.EOF):
            self.skip_newlines()
            if self.current_token().type in (TokenType.DEDENT, TokenType.EOF):
                break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        if self.current_token().type == TokenType.DEDENT:
            self.advance()
        
        return statements
    
    def parse_expression_or_assignment(self) -> ASTNode:
        """Parse expression or assignment"""
        expr = self.parse_expression()
        
        token = self.current_token()
        if token.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()
            return AssignmentNode(expr, value, token.line, token.column)
        elif token.type in (TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                           TokenType.MUL_ASSIGN, TokenType.DIV_ASSIGN):
            op_map = {
                TokenType.PLUS_ASSIGN: '+=',
                TokenType.MINUS_ASSIGN: '-=',
                TokenType.MUL_ASSIGN: '*=',
                TokenType.DIV_ASSIGN: '/=',
            }
            self.advance()
            value = self.parse_expression()
            return AugmentedAssignmentNode(expr, op_map[token.type], value,
                                          token.line, token.column)
        
        return ExpressionStatementNode(expr, expr.line, expr.column)
    
    def parse_expression(self) -> ASTNode:
        """Parse an expression (including ternary conditional)"""
        return self.parse_ternary_expression()
    
    def parse_ternary_expression(self) -> ASTNode:
        """Parse ternary conditional expression - value אם condition אחרת alternative"""
        # First parse the true value (or just the expression if not ternary)
        true_value = self.parse_or_expression()
        
        # Check for ternary: value אם condition אחרת alternative
        if self.current_token().type == TokenType.IF:
            self.advance()  # consume אם
            condition = self.parse_or_expression()
            
            self.expect(TokenType.ELSE, "ציפיתי ל־'אחרת' בביטוי תנאי")
            false_value = self.parse_ternary_expression()  # Allow chaining
            
            return TernaryNode(true_value, condition, false_value,
                              true_value.line, true_value.column)
        
        return true_value
    
    def parse_or_expression(self) -> ASTNode:
        """Parse 'or' expression - או"""
        left = self.parse_and_expression()
        
        while self.current_token().type == TokenType.OR:
            self.advance()
            right = self.parse_and_expression()
            left = LogicalOpNode(left, 'or', right, left.line, left.column)
        
        return left
    
    def parse_and_expression(self) -> ASTNode:
        """Parse 'and' expression - וגם"""
        left = self.parse_not_expression()
        
        while self.current_token().type == TokenType.AND:
            self.advance()
            right = self.parse_not_expression()
            left = LogicalOpNode(left, 'and', right, left.line, left.column)
        
        return left
    
    def parse_not_expression(self) -> ASTNode:
        """Parse 'not' expression - לא"""
        if self.current_token().type == TokenType.NOT:
            token = self.advance()
            # Check if this is 'לא בתוך' (not in) - two word form
            if self.current_token().type == TokenType.IN:
                # This is "not in" as two words, let parse_comparison handle it
                # by putting back the NOT and treating לא בתוך as a comparison op
                self.pos -= 1
                return self.parse_comparison()
            operand = self.parse_not_expression()
            return UnaryOpNode('not', operand, token.line, token.column)
        
        return self.parse_comparison()
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison expression"""
        left = self.parse_additive()
        
        comparison_ops = {
            TokenType.EQUALS: '==',
            TokenType.NOT_EQUALS: '!=',
            TokenType.LESS: '<',
            TokenType.GREATER: '>',
            TokenType.LESS_EQ: '<=',
            TokenType.GREATER_EQ: '>=',
            TokenType.IN: 'in',
            TokenType.NOT_IN: 'not in',
        }
        
        ops = []
        comparators = []
        
        while True:
            token_type = self.current_token().type
            if token_type in comparison_ops:
                op = comparison_ops[token_type]
                self.advance()
                ops.append(op)
                comparators.append(self.parse_additive())
            # Handle two-word "לא בתוך" (NOT IN)
            elif token_type == TokenType.NOT and self.peek(1) and self.peek(1).type == TokenType.IN:
                self.advance()  # consume NOT
                self.advance()  # consume IN
                ops.append('not in')
                comparators.append(self.parse_additive())
            else:
                break
        
        if ops:
            return ComparisonNode(left, ops, comparators, left.line, left.column)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        """Parse additive expression (+, -)"""
        left = self.parse_multiplicative()
        
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op = '+' if self.current_token().type == TokenType.PLUS else '-'
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOpNode(left, op, right, left.line, left.column)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplicative expression (*, /, //, %)"""
        left = self.parse_power()
        
        op_map = {
            TokenType.MULTIPLY: '*',
            TokenType.DIVIDE: '/',
            TokenType.FLOOR_DIV: '//',
            TokenType.MODULO: '%',
        }
        
        while self.current_token().type in op_map:
            op = op_map[self.current_token().type]
            self.advance()
            right = self.parse_power()
            left = BinaryOpNode(left, op, right, left.line, left.column)
        
        return left
    
    def parse_power(self) -> ASTNode:
        """Parse power expression (**)"""
        left = self.parse_unary()
        
        if self.current_token().type == TokenType.POWER:
            self.advance()
            right = self.parse_power()  # Right associative
            return BinaryOpNode(left, '**', right, left.line, left.column)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary expression (-x, +x)"""
        token = self.current_token()
        
        if token.type in (TokenType.PLUS, TokenType.MINUS):
            op = '+' if token.type == TokenType.PLUS else '-'
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(op, operand, token.line, token.column)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """Parse postfix expressions (call, index, attribute)"""
        expr = self.parse_primary()
        
        while True:
            token = self.current_token()
            
            if token.type == TokenType.LPAREN:
                # Function call
                self.advance()
                args = []
                kwargs = {}
                
                while self.current_token().type != TokenType.RPAREN:
                    # Check for keyword argument
                    if (self.current_token().type == TokenType.IDENTIFIER and
                        self.peek() and self.peek().type == TokenType.ASSIGN):
                        key = self.advance().value
                        self.advance()  # Skip =
                        value = self.parse_expression()
                        kwargs[key] = value
                    else:
                        args.append(self.parse_expression())
                    
                    if self.current_token().type == TokenType.COMMA:
                        self.advance()
                
                self.expect(TokenType.RPAREN)
                expr = CallNode(expr, args, kwargs, expr.line, expr.column)
                
            elif token.type == TokenType.LBRACKET:
                # Index access or slice
                self.advance()
                
                # Check for slice syntax: [start:end] or [start:end:step]
                start = None
                end = None
                step = None
                is_slice = False
                
                # Parse start (optional)
                if self.current_token().type != TokenType.COLON:
                    start = self.parse_expression()
                
                # Check for colon (indicates slice)
                if self.current_token().type == TokenType.COLON:
                    is_slice = True
                    self.advance()
                    
                    # Parse end (optional)
                    if self.current_token().type not in (TokenType.COLON, TokenType.RBRACKET):
                        end = self.parse_expression()
                    
                    # Check for second colon (step)
                    if self.current_token().type == TokenType.COLON:
                        self.advance()
                        if self.current_token().type != TokenType.RBRACKET:
                            step = self.parse_expression()
                
                self.expect(TokenType.RBRACKET)
                
                if is_slice:
                    expr = SliceNode(expr, start, end, step, expr.line, expr.column)
                else:
                    expr = IndexNode(expr, start, expr.line, expr.column)
                
            elif token.type == TokenType.DOT:
                # Attribute access - allow identifiers and builtins/keywords as attribute names
                self.advance()
                attr_token = self.expect_attribute_name("ציפיתי לשם תכונה")
                expr = AttributeNode(expr, attr_token.value, expr.line, expr.column)
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expression (literals, identifiers, parenthesized)"""
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            # Handle hex (0x), octal (0o), binary (0b) and decimal numbers
            val_str = token.value
            if val_str.startswith(('0x', '0X')):
                value = int(val_str, 16)
            elif val_str.startswith(('0o', '0O')):
                value = int(val_str, 8)
            elif val_str.startswith(('0b', '0B')):
                value = int(val_str, 2)
            elif '.' in val_str:
                value = float(val_str)
            else:
                value = int(val_str)
            return NumberNode(value, token.line, token.column)
        
        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(token.value, token.line, token.column)
        
        elif token.type == TokenType.TRUE:
            self.advance()
            return BooleanNode(True, token.line, token.column)
        
        elif token.type == TokenType.FALSE:
            self.advance()
            return BooleanNode(False, token.line, token.column)
        
        elif token.type == TokenType.NONE:
            self.advance()
            return NoneNode(token.line, token.column)
        
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return IdentifierNode(token.value, token.line, token.column)
        
        # Built-in functions as identifiers
        elif token.type in (TokenType.PRINT, TokenType.INPUT, TokenType.LEN,
                           TokenType.TYPE, TokenType.RANGE, TokenType.INT,
                           TokenType.FLOAT, TokenType.STR, TokenType.LIST,
                           TokenType.DICT, TokenType.SET, TokenType.BOOL,
                           TokenType.ABS, TokenType.SUM, TokenType.MIN,
                           TokenType.MAX, TokenType.SORTED, TokenType.REVERSED,
                           TokenType.ENUMERATE, TokenType.ZIP, TokenType.MAP,
                           TokenType.FILTER, TokenType.OPEN):
            self.advance()
            return IdentifierNode(token.value, token.line, token.column)
        
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "ציפיתי ל־')'")
            return expr
        
        elif token.type == TokenType.LBRACKET:
            return self.parse_list()
        
        elif token.type == TokenType.LBRACE:
            return self.parse_dict()
        
        elif token.type == TokenType.LAMBDA:
            return self.parse_lambda()
        
        else:
            raise ParserError(f"ביטוי לא צפוי: '{token.value}'",
                            token.line, token.column)
    
    def parse_list(self) -> ASTNode:
        """Parse list literal or list comprehension"""
        token = self.expect(TokenType.LBRACKET)
        
        # Check for empty list
        if self.current_token().type == TokenType.RBRACKET:
            self.advance()
            return ListNode([], token.line, token.column)
        
        # Parse first expression
        first_expr = self.parse_expression()
        
        # Check if this is a list comprehension: [expr עבור var בתוך iterable]
        if self.current_token().type == TokenType.FOR:
            self.advance()  # consume עבור
            
            # Get loop variable (allow builtins as variable names)
            if self.current_token().type != TokenType.IDENTIFIER and self.current_token().type not in BUILTIN_FUNCTION_TOKENS:
                raise ParserError("ציפיתי למשתנה לולאה", 
                                self.current_token().line, self.current_token().column)
            variable = self.current_token().value
            self.advance()
            
            # Expect בתוך
            self.expect(TokenType.IN, "ציפיתי ל־'בתוך'")
            
            # Parse iterable (use parse_or_expression to avoid consuming IF as ternary)
            iterable = self.parse_or_expression()
            
            # Check for optional condition (אם)
            condition = None
            if self.current_token().type == TokenType.IF:
                self.advance()
                # Condition also uses parse_or_expression to avoid ternary issues
                condition = self.parse_or_expression()
            
            self.expect(TokenType.RBRACKET)
            return ListCompNode(first_expr, variable, iterable, condition, token.line, token.column)
        
        # Regular list literal
        elements = [first_expr]
        
        # Skip newlines after first element
        self.skip_newlines()
        
        while self.current_token().type == TokenType.COMMA:
            self.advance()
            # Skip newlines after comma
            self.skip_newlines()
            if self.current_token().type == TokenType.RBRACKET:
                break  # Allow trailing comma
            elements.append(self.parse_expression())
            # Skip newlines after element
            self.skip_newlines()
        
        self.expect(TokenType.RBRACKET)
        return ListNode(elements, token.line, token.column)
    
    def parse_dict(self) -> DictNode:
        """Parse dictionary literal"""
        token = self.expect(TokenType.LBRACE)
        pairs = []
        
        # Skip newlines at the start
        self.skip_newlines()
        
        while self.current_token().type != TokenType.RBRACE:
            key = self.parse_expression()
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            pairs.append((key, value))
            
            # Skip newlines after value
            self.skip_newlines()
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
                # Skip newlines after comma
                self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return DictNode(pairs, token.line, token.column)
    
    def parse_lambda(self) -> LambdaNode:
        """Parse lambda expression - פונקציה_אנונימית פרמטרים: ביטוי"""
        token = self.expect(TokenType.LAMBDA)
        params = []
        
        # Parse parameters until we hit the colon (allow builtins as param names)
        while self.current_token().type != TokenType.COLON:
            if self.current_token().type == TokenType.IDENTIFIER or self.current_token().type in BUILTIN_FUNCTION_TOKENS:
                params.append(self.current_token().value)
                self.advance()
                
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
            else:
                break
        
        self.expect(TokenType.COLON, "ציפיתי ל־':' אחרי פרמטרי הלמבדה")
        
        # Parse the body expression
        body = self.parse_expression()
        
        return LambdaNode(params, body, token.line, token.column)


def parse(code: str) -> ProgramNode:
    """Convenience function to parse code"""
    try:
        from .lexer import Lexer
    except ImportError:
        from nachshon.lexer import Lexer
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Test the parser
    test_code = '''הגדר שלום(שם):
    הדפס("שלום, " + שם)
    החזר אמת

שלום("עולם")
'''
    
    try:
        ast = parse(test_code)
        print("AST נוצר בהצלחה!")
        print(f"מספר פקודות: {len(ast.body)}")
        for node in ast.body:
            print(f"  - {node.type.name}")
    except (LexerError, ParserError) as e:
        print(f"שגיאה: {e}")
