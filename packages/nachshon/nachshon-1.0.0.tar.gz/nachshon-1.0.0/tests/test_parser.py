# test_parser.py
# Unit tests for Nachshon parser - בדיקות יחידה למנתח התחבירי

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from nachshon.lexer import Lexer, LexerError
from nachshon.parser import (
    Parser, ParserError, parse, NodeType,
    ProgramNode, FunctionDefNode, IfStatementNode, WhileStatementNode,
    ForStatementNode, ReturnStatementNode, AssignmentNode,
    ExpressionStatementNode, BinaryOpNode, CallNode, IdentifierNode,
    NumberNode, StringNode, BooleanNode, NoneNode, ListNode, DictNode
)


class TestParserBasics(unittest.TestCase):
    """Test basic parser functionality - בדיקות בסיסיות"""
    
    def test_empty_program(self):
        """Test empty program parsing"""
        ast = parse("")
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.body), 0)
    
    def test_program_type(self):
        """Test program returns correct type"""
        ast = parse("x = 1")
        self.assertEqual(ast.type, NodeType.PROGRAM)


class TestParserExpressions(unittest.TestCase):
    """Test expression parsing - בדיקות ביטויים"""
    
    def test_number_literal(self):
        """Test number literal parsing"""
        ast = parse("42")
        stmt = ast.body[0]
        self.assertIsInstance(stmt, ExpressionStatementNode)
        self.assertIsInstance(stmt.expression, NumberNode)
        self.assertEqual(stmt.expression.value, 42)
    
    def test_float_literal(self):
        """Test float literal parsing"""
        ast = parse("3.14")
        stmt = ast.body[0]
        self.assertEqual(stmt.expression.value, 3.14)
    
    def test_string_literal(self):
        """Test string literal parsing"""
        ast = parse('"שלום"')
        stmt = ast.body[0]
        self.assertIsInstance(stmt.expression, StringNode)
        self.assertEqual(stmt.expression.value, "שלום")
    
    def test_boolean_true(self):
        """Test אמת (True) parsing"""
        ast = parse("אמת")
        stmt = ast.body[0]
        self.assertIsInstance(stmt.expression, BooleanNode)
        self.assertTrue(stmt.expression.value)
    
    def test_boolean_false(self):
        """Test שקר (False) parsing"""
        ast = parse("שקר")
        stmt = ast.body[0]
        self.assertIsInstance(stmt.expression, BooleanNode)
        self.assertFalse(stmt.expression.value)
    
    def test_none_literal(self):
        """Test ריק (None) parsing"""
        ast = parse("ריק")
        stmt = ast.body[0]
        self.assertIsInstance(stmt.expression, NoneNode)
    
    def test_identifier(self):
        """Test identifier parsing"""
        ast = parse("משתנה")
        stmt = ast.body[0]
        self.assertIsInstance(stmt.expression, IdentifierNode)
        self.assertEqual(stmt.expression.name, "משתנה")


class TestParserBinaryOps(unittest.TestCase):
    """Test binary operations - בדיקות פעולות בינאריות"""
    
    def test_addition(self):
        """Test addition parsing"""
        ast = parse("1 + 2")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertIsInstance(expr, BinaryOpNode)
        self.assertEqual(expr.op, '+')
    
    def test_subtraction(self):
        """Test subtraction parsing"""
        ast = parse("5 - 3")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.op, '-')
    
    def test_multiplication(self):
        """Test multiplication parsing"""
        ast = parse("4 * 2")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.op, '*')
    
    def test_division(self):
        """Test division parsing"""
        ast = parse("10 / 2")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.op, '/')
    
    def test_power(self):
        """Test power operator parsing"""
        ast = parse("2 ** 3")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.op, '**')
    
    def test_operator_precedence(self):
        """Test operator precedence"""
        ast = parse("1 + 2 * 3")
        stmt = ast.body[0]
        expr = stmt.expression
        # Should be 1 + (2 * 3)
        self.assertEqual(expr.op, '+')
        self.assertIsInstance(expr.right, BinaryOpNode)
        self.assertEqual(expr.right.op, '*')


class TestParserComparisons(unittest.TestCase):
    """Test comparison operations - בדיקות השוואות"""
    
    def test_equals(self):
        """Test equals comparison"""
        ast = parse("x == 5")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.ops[0], '==')
    
    def test_not_equals(self):
        """Test not equals comparison"""
        ast = parse("x != 5")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.ops[0], '!=')
    
    def test_less_than(self):
        """Test less than comparison"""
        ast = parse("x < 5")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.ops[0], '<')
    
    def test_greater_than(self):
        """Test greater than comparison"""
        ast = parse("x > 5")
        stmt = ast.body[0]
        expr = stmt.expression
        self.assertEqual(expr.ops[0], '>')


class TestParserAssignment(unittest.TestCase):
    """Test assignment parsing - בדיקות השמה"""
    
    def test_simple_assignment(self):
        """Test simple assignment"""
        ast = parse("x = 5")
        stmt = ast.body[0]
        self.assertIsInstance(stmt, AssignmentNode)
        self.assertEqual(stmt.target.name, "x")
        self.assertEqual(stmt.value.value, 5)
    
    def test_hebrew_variable_assignment(self):
        """Test Hebrew variable assignment"""
        ast = parse("משתנה = 10")
        stmt = ast.body[0]
        self.assertIsInstance(stmt, AssignmentNode)
        self.assertEqual(stmt.target.name, "משתנה")
    
    def test_string_assignment(self):
        """Test string assignment"""
        ast = parse('שם = "יוסי"')
        stmt = ast.body[0]
        self.assertEqual(stmt.value.value, "יוסי")


class TestParserFunctionDef(unittest.TestCase):
    """Test function definition parsing - בדיקות הגדרת פונקציה"""
    
    def test_simple_function(self):
        """Test simple function definition"""
        code = """הגדר שלום():
    הדפס("שלום")
"""
        ast = parse(code)
        func = ast.body[0]
        self.assertIsInstance(func, FunctionDefNode)
        self.assertEqual(func.name, "שלום")
        self.assertEqual(len(func.params), 0)
    
    def test_function_with_params(self):
        """Test function with parameters"""
        code = """הגדר ברך(שם):
    הדפס(שם)
"""
        ast = parse(code)
        func = ast.body[0]
        self.assertEqual(func.params, ["שם"])
    
    def test_function_multiple_params(self):
        """Test function with multiple parameters"""
        code = """הגדר חיבור(א, ב):
    החזר א + ב
"""
        ast = parse(code)
        func = ast.body[0]
        self.assertEqual(func.params, ["א", "ב"])
    
    def test_function_with_return(self):
        """Test function with return statement"""
        code = """הגדר כפול(מספר):
    החזר מספר * 2
"""
        ast = parse(code)
        func = ast.body[0]
        self.assertEqual(len(func.body), 1)
        self.assertIsInstance(func.body[0], ReturnStatementNode)


class TestParserIfStatement(unittest.TestCase):
    """Test if statement parsing - בדיקות משפט תנאי"""
    
    def test_simple_if(self):
        """Test simple if statement"""
        code = """אם אמת:
    הדפס("כן")
"""
        ast = parse(code)
        if_stmt = ast.body[0]
        self.assertIsInstance(if_stmt, IfStatementNode)
        self.assertEqual(len(if_stmt.body), 1)
    
    def test_if_else(self):
        """Test if-else statement"""
        code = """אם x > 5:
    הדפס("גדול")
אחרת:
    הדפס("קטן")
"""
        ast = parse(code)
        if_stmt = ast.body[0]
        self.assertIsInstance(if_stmt, IfStatementNode)
        self.assertEqual(len(if_stmt.else_body), 1)
    
    def test_if_elif_else(self):
        """Test if-elif-else statement"""
        code = """אם x > 10:
    הדפס("גדול מ-10")
אחרת_אם x > 5:
    הדפס("גדול מ-5")
אחרת:
    הדפס("קטן")
"""
        ast = parse(code)
        if_stmt = ast.body[0]
        self.assertEqual(len(if_stmt.elif_clauses), 1)
        self.assertEqual(len(if_stmt.else_body), 1)


class TestParserLoops(unittest.TestCase):
    """Test loop parsing - בדיקות לולאות"""
    
    def test_while_loop(self):
        """Test while loop parsing"""
        code = """בעוד x < 10:
    x = x + 1
"""
        ast = parse(code)
        while_stmt = ast.body[0]
        self.assertIsInstance(while_stmt, WhileStatementNode)
        self.assertEqual(len(while_stmt.body), 1)
    
    def test_for_loop(self):
        """Test for loop parsing"""
        code = """עבור i בתוך טווח(10):
    הדפס(i)
"""
        ast = parse(code)
        for_stmt = ast.body[0]
        self.assertIsInstance(for_stmt, ForStatementNode)
        self.assertEqual(for_stmt.variable, "i")
        self.assertEqual(len(for_stmt.body), 1)


class TestParserFunctionCalls(unittest.TestCase):
    """Test function call parsing - בדיקות קריאה לפונקציה"""
    
    def test_no_args_call(self):
        """Test function call with no arguments"""
        ast = parse("שלום()")
        stmt = ast.body[0]
        call = stmt.expression
        self.assertIsInstance(call, CallNode)
        self.assertEqual(len(call.args), 0)
    
    def test_single_arg_call(self):
        """Test function call with single argument"""
        ast = parse('הדפס("שלום")')
        stmt = ast.body[0]
        call = stmt.expression
        self.assertEqual(len(call.args), 1)
    
    def test_multiple_args_call(self):
        """Test function call with multiple arguments"""
        ast = parse("חיבור(1, 2, 3)")
        stmt = ast.body[0]
        call = stmt.expression
        self.assertEqual(len(call.args), 3)
    
    def test_hebrew_builtin_call(self):
        """Test Hebrew built-in function call"""
        ast = parse("טווח(10)")
        stmt = ast.body[0]
        call = stmt.expression
        self.assertIsInstance(call, CallNode)


class TestParserLists(unittest.TestCase):
    """Test list parsing - בדיקות רשימות"""
    
    def test_empty_list(self):
        """Test empty list parsing"""
        ast = parse("[]")
        stmt = ast.body[0]
        list_node = stmt.expression
        self.assertIsInstance(list_node, ListNode)
        self.assertEqual(len(list_node.elements), 0)
    
    def test_number_list(self):
        """Test list with numbers"""
        ast = parse("[1, 2, 3]")
        stmt = ast.body[0]
        list_node = stmt.expression
        self.assertEqual(len(list_node.elements), 3)
    
    def test_string_list(self):
        """Test list with strings"""
        ast = parse('["א", "ב", "ג"]')
        stmt = ast.body[0]
        list_node = stmt.expression
        self.assertEqual(len(list_node.elements), 3)


class TestParserDicts(unittest.TestCase):
    """Test dictionary parsing - בדיקות מילונים"""
    
    def test_empty_dict(self):
        """Test empty dictionary parsing"""
        ast = parse("{}")
        stmt = ast.body[0]
        dict_node = stmt.expression
        self.assertIsInstance(dict_node, DictNode)
        self.assertEqual(len(dict_node.pairs), 0)
    
    def test_simple_dict(self):
        """Test simple dictionary parsing"""
        ast = parse('{"שם": "יוסי", "גיל": 25}')
        stmt = ast.body[0]
        dict_node = stmt.expression
        self.assertEqual(len(dict_node.pairs), 2)


class TestParserErrors(unittest.TestCase):
    """Test parser error handling - בדיקות טיפול בשגיאות"""
    
    def test_missing_colon_if(self):
        """Test missing colon in if statement"""
        with self.assertRaises(ParserError) as context:
            parse("אם אמת\n    הדפס()")
        self.assertIn(":", str(context.exception))
    
    def test_missing_paren_function(self):
        """Test missing parenthesis in function definition"""
        with self.assertRaises(ParserError) as context:
            parse("הגדר שלום:\n    הדפס()")
        self.assertIn("(", str(context.exception))


class TestParserCompletePrograms(unittest.TestCase):
    """Test complete program parsing - בדיקות תוכניות מלאות"""
    
    def test_hello_world(self):
        """Test hello world program"""
        code = 'הדפס("שלום עולם!")'
        ast = parse(code)
        self.assertEqual(len(ast.body), 1)
    
    def test_calculator_function(self):
        """Test calculator function"""
        code = """הגדר חיבור(א, ב):
    החזר א + ב

תוצאה = חיבור(3, 5)
הדפס(תוצאה)
"""
        ast = parse(code)
        self.assertEqual(len(ast.body), 3)
        self.assertIsInstance(ast.body[0], FunctionDefNode)
        self.assertIsInstance(ast.body[1], AssignmentNode)


class TestParserClasses(unittest.TestCase):
    """Test class parsing - בדיקות מחלקות"""
    
    def test_simple_class(self):
        """Test simple class definition"""
        code = """מחלקה חיה:
    הגדר דבר(עצמי):
        הדפס("קול")
"""
        ast = parse(code)
        class_def = ast.body[0]
        from nachshon.parser import ClassDefNode
        self.assertIsInstance(class_def, ClassDefNode)
        self.assertEqual(class_def.name, "חיה")
    
    def test_class_with_inheritance(self):
        """Test class with inheritance"""
        code = """מחלקה כלב(חיה):
    הגדר דבר(עצמי):
        הדפס("הב!")
"""
        ast = parse(code)
        class_def = ast.body[0]
        from nachshon.parser import ClassDefNode
        self.assertIsInstance(class_def, ClassDefNode)
        self.assertEqual(class_def.base, "חיה")


class TestParserTryExcept(unittest.TestCase):
    """Test try-except parsing - בדיקות נסה-תפוס"""
    
    def test_simple_try_except(self):
        """Test simple try-except"""
        code = """נסה:
    x = 1 / 0
תפוס:
    הדפס("שגיאה")
"""
        ast = parse(code)
        from nachshon.parser import TryExceptNode
        try_stmt = ast.body[0]
        self.assertIsInstance(try_stmt, TryExceptNode)
        self.assertEqual(len(try_stmt.try_body), 1)
        self.assertEqual(len(try_stmt.except_clauses), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
