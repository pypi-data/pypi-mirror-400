# test_transpiler.py
# Unit tests for Nachshon transpiler - בדיקות יחידה לממיר

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from nachshon.transpiler import transpile, Transpiler, TranspilerError, BUILTIN_MAPPING
from nachshon.parser import parse


class TestTranspilerBasics(unittest.TestCase):
    """Test basic transpiler functionality - בדיקות בסיסיות"""
    
    def test_empty_program(self):
        """Test empty program transpilation"""
        result = transpile("")
        self.assertIn("# -*- coding: utf-8 -*-", result)
    
    def test_header_comment(self):
        """Test header comments in output"""
        result = transpile("")
        self.assertIn("נחשון", result)


class TestTranspilerExpressions(unittest.TestCase):
    """Test expression transpilation - בדיקות המרת ביטויים"""
    
    def test_number(self):
        """Test number transpilation"""
        result = transpile("42")
        self.assertIn("42", result)
    
    def test_string(self):
        """Test string transpilation"""
        result = transpile('"שלום"')
        self.assertIn('"שלום"', result)
    
    def test_boolean_true(self):
        """Test אמת transpilation"""
        result = transpile("אמת")
        self.assertIn("True", result)
    
    def test_boolean_false(self):
        """Test שקר transpilation"""
        result = transpile("שקר")
        self.assertIn("False", result)
    
    def test_none(self):
        """Test ריק transpilation"""
        result = transpile("ריק")
        self.assertIn("None", result)


class TestTranspilerBuiltins(unittest.TestCase):
    """Test built-in function mapping - בדיקות מיפוי פונקציות מובנות"""
    
    def test_print_mapping(self):
        """Test הדפס → print mapping"""
        result = transpile('הדפס("שלום")')
        self.assertIn('print("שלום")', result)
    
    def test_input_mapping(self):
        """Test קלט → input mapping"""
        result = transpile('קלט("הכנס: ")')
        self.assertIn('input("הכנס: ")', result)
    
    def test_len_mapping(self):
        """Test אורך → len mapping"""
        result = transpile('אורך([1, 2, 3])')
        self.assertIn('len([1, 2, 3])', result)
    
    def test_range_mapping(self):
        """Test טווח → range mapping"""
        result = transpile('טווח(10)')
        self.assertIn('range(10)', result)
    
    def test_type_mapping(self):
        """Test סוג → type mapping"""
        result = transpile('סוג(x)')
        self.assertIn('type(x)', result)
    
    def test_int_mapping(self):
        """Test מספר_שלם → int mapping"""
        result = transpile('מספר_שלם("5")')
        self.assertIn('int("5")', result)
    
    def test_str_mapping(self):
        """Test מחרוזת → str mapping"""
        result = transpile('מחרוזת(42)')
        self.assertIn('str(42)', result)
    
    def test_all_builtins_mapped(self):
        """Test all built-in functions have mappings"""
        expected_mappings = [
            ('הדפס', 'print'),
            ('קלט', 'input'),
            ('אורך', 'len'),
            ('סוג', 'type'),
            ('טווח', 'range'),
            ('מספר_שלם', 'int'),
            ('מספר_עשרוני', 'float'),
            ('מחרוזת', 'str'),
            ('רשימה', 'list'),
            ('מילון', 'dict'),
            ('סכום', 'sum'),
            ('מינימום', 'min'),
            ('מקסימום', 'max'),
        ]
        for hebrew, python in expected_mappings:
            self.assertEqual(BUILTIN_MAPPING.get(hebrew), python)


class TestTranspilerAssignment(unittest.TestCase):
    """Test assignment transpilation - בדיקות המרת השמה"""
    
    def test_simple_assignment(self):
        """Test simple assignment"""
        result = transpile("x = 5")
        self.assertIn("x = 5", result)
    
    def test_hebrew_variable(self):
        """Test Hebrew variable assignment"""
        result = transpile("משתנה = 10")
        self.assertIn("משתנה = 10", result)
    
    def test_augmented_assignment(self):
        """Test augmented assignment"""
        result = transpile("x += 1")
        self.assertIn("x += 1", result)


class TestTranspilerFunctions(unittest.TestCase):
    """Test function transpilation - בדיקות המרת פונקציות"""
    
    def test_simple_function(self):
        """Test simple function definition"""
        code = """הגדר שלום():
    הדפס("שלום")
"""
        result = transpile(code)
        self.assertIn("def שלום():", result)
        self.assertIn('print("שלום")', result)
    
    def test_function_with_params(self):
        """Test function with parameters"""
        code = """הגדר ברך(שם):
    הדפס(שם)
"""
        result = transpile(code)
        self.assertIn("def ברך(שם):", result)
    
    def test_function_with_return(self):
        """Test function with return"""
        code = """הגדר כפול(מספר):
    החזר מספר * 2
"""
        result = transpile(code)
        self.assertIn("return", result)


class TestTranspilerControlFlow(unittest.TestCase):
    """Test control flow transpilation - בדיקות המרת בקרת זרימה"""
    
    def test_if_statement(self):
        """Test if statement"""
        code = """אם x > 5:
    הדפס("גדול")
"""
        result = transpile(code)
        self.assertIn("if (x > 5):", result)
        self.assertIn('print("גדול")', result)
    
    def test_if_else(self):
        """Test if-else statement"""
        code = """אם x > 5:
    הדפס("גדול")
אחרת:
    הדפס("קטן")
"""
        result = transpile(code)
        self.assertIn("if", result)
        self.assertIn("else:", result)
    
    def test_if_elif_else(self):
        """Test if-elif-else statement"""
        code = """אם x > 10:
    הדפס("מאוד גדול")
אחרת_אם x > 5:
    הדפס("גדול")
אחרת:
    הדפס("קטן")
"""
        result = transpile(code)
        self.assertIn("if", result)
        self.assertIn("elif", result)
        self.assertIn("else:", result)
    
    def test_while_loop(self):
        """Test while loop"""
        code = """בעוד x < 10:
    x = x + 1
"""
        result = transpile(code)
        self.assertIn("while (x < 10):", result)
    
    def test_for_loop(self):
        """Test for loop"""
        code = """עבור i בתוך טווח(10):
    הדפס(i)
"""
        result = transpile(code)
        self.assertIn("for i in range(10):", result)
        self.assertIn("print(i)", result)


class TestTranspilerBreakContinue(unittest.TestCase):
    """Test break/continue transpilation - בדיקות הפסק/המשך"""
    
    def test_break(self):
        """Test break statement"""
        code = """בעוד אמת:
    הפסק
"""
        result = transpile(code)
        self.assertIn("break", result)
    
    def test_continue(self):
        """Test continue statement"""
        code = """עבור i בתוך טווח(10):
    המשך
"""
        result = transpile(code)
        self.assertIn("continue", result)


class TestTranspilerCollections(unittest.TestCase):
    """Test collection transpilation - בדיקות המרת אוספים"""
    
    def test_list(self):
        """Test list transpilation"""
        result = transpile("[1, 2, 3]")
        self.assertIn("[1, 2, 3]", result)
    
    def test_dict(self):
        """Test dictionary transpilation"""
        result = transpile('{"א": 1, "ב": 2}')
        self.assertIn('"א": 1', result)
        self.assertIn('"ב": 2', result)


class TestTranspilerLogical(unittest.TestCase):
    """Test logical operator transpilation - בדיקות אופרטורים לוגיים"""
    
    def test_and_operator(self):
        """Test וגם → and"""
        code = """אם x > 0 וגם x < 10:
    הדפס("בטווח")
"""
        result = transpile(code)
        self.assertIn("and", result)
    
    def test_or_operator(self):
        """Test או → or"""
        code = """אם x < 0 או x > 10:
    הדפס("מחוץ לטווח")
"""
        result = transpile(code)
        self.assertIn("or", result)
    
    def test_not_operator(self):
        """Test לא → not"""
        code = """אם לא x:
    הדפס("ריק")
"""
        result = transpile(code)
        self.assertIn("not", result)


class TestTranspilerExecution(unittest.TestCase):
    """Test that transpiled code actually runs - בדיקות הרצת קוד"""
    
    def test_hello_world_execution(self):
        """Test hello world executes correctly"""
        code = 'הדפס("שלום")'
        python_code = transpile(code)
        # Should not raise
        exec(python_code)
    
    def test_arithmetic_execution(self):
        """Test arithmetic executes correctly"""
        code = """x = 5 + 3
y = x * 2
"""
        python_code = transpile(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['x'], 8)
        self.assertEqual(namespace['y'], 16)
    
    def test_function_execution(self):
        """Test function executes correctly"""
        code = """הגדר כפול(מספר):
    החזר מספר * 2

תוצאה = כפול(5)
"""
        python_code = transpile(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['תוצאה'], 10)
    
    def test_loop_execution(self):
        """Test loop executes correctly"""
        code = """ס = 0
עבור i בתוך טווח(5):
    ס = ס + i
"""
        python_code = transpile(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['ס'], 10)  # 0+1+2+3+4
    
    def test_condition_execution(self):
        """Test condition executes correctly"""
        code = """x = 10
אם x > 5:
    תוצאה = "גדול"
אחרת:
    תוצאה = "קטן"
"""
        python_code = transpile(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['תוצאה'], "גדול")
    
    def test_list_operations_execution(self):
        """Test list operations execute correctly"""
        code = """רשימה = [1, 2, 3, 4, 5]
אורך_רשימה = אורך(רשימה)
סכום_רשימה = סכום(רשימה)
"""
        python_code = transpile(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['אורך_רשימה'], 5)
        self.assertEqual(namespace['סכום_רשימה'], 15)


class TestTranspilerIndentation(unittest.TestCase):
    """Test indentation handling - בדיקות הזחה"""
    
    def test_proper_indentation(self):
        """Test proper indentation in output"""
        code = """הגדר פונקציה():
    אם אמת:
        הדפס("כן")
    אחרת:
        הדפס("לא")
"""
        result = transpile(code)
        lines = result.split('\n')
        
        # Find lines with if/else
        for i, line in enumerate(lines):
            if 'if True:' in line:
                # Next line should be more indented
                self.assertIn('        print', lines[i + 1])


class TestTranspilerComplexPrograms(unittest.TestCase):
    """Test complex programs - בדיקות תוכניות מורכבות"""
    
    def test_factorial(self):
        """Test factorial function"""
        code = """הגדר עצרת(נ):
    אם נ <= 1:
        החזר 1
    אחרת:
        החזר נ * עצרת(נ - 1)

תוצאה = עצרת(5)
"""
        python_code = transpile(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['תוצאה'], 120)
    
    def test_fibonacci(self):
        """Test fibonacci function"""
        code = """הגדר פיבונאצי(נ):
    אם נ <= 1:
        החזר נ
    החזר פיבונאצי(נ - 1) + פיבונאצי(נ - 2)

תוצאה = פיבונאצי(10)
"""
        python_code = transpile(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['תוצאה'], 55)


if __name__ == '__main__':
    unittest.main(verbosity=2)
