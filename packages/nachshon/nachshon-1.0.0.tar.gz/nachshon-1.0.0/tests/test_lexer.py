# test_lexer.py
# Unit tests for Nachshon lexer - בדיקות יחידה למנתח הלקסיקלי

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from nachshon.lexer import Lexer, Token, TokenType, LexerError, tokenize


class TestLexerBasics(unittest.TestCase):
    """Test basic lexer functionality - בדיקות בסיסיות"""
    
    def test_empty_input(self):
        """Test empty input returns only EOF"""
        tokens = tokenize("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_whitespace_only(self):
        """Test whitespace-only input"""
        tokens = tokenize("   \t  ")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_newlines(self):
        """Test newline handling"""
        tokens = tokenize("\n\n")
        newline_count = sum(1 for t in tokens if t.type == TokenType.NEWLINE)
        self.assertEqual(newline_count, 2)


class TestLexerNumbers(unittest.TestCase):
    """Test number tokenization - בדיקות מספרים"""
    
    def test_integer(self):
        """Test integer recognition"""
        tokens = tokenize("42")
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, "42")
    
    def test_float(self):
        """Test float recognition"""
        tokens = tokenize("3.14")
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, "3.14")
    
    def test_multiple_numbers(self):
        """Test multiple numbers"""
        tokens = tokenize("1 2 3")
        numbers = [t for t in tokens if t.type == TokenType.NUMBER]
        self.assertEqual(len(numbers), 3)
        self.assertEqual([n.value for n in numbers], ["1", "2", "3"])


class TestLexerStrings(unittest.TestCase):
    """Test string tokenization - בדיקות מחרוזות"""
    
    def test_double_quoted_string(self):
        """Test double-quoted string"""
        tokens = tokenize('"שלום"')
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "שלום")
    
    def test_single_quoted_string(self):
        """Test single-quoted string"""
        tokens = tokenize("'עולם'")
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "עולם")
    
    def test_string_with_escape(self):
        """Test string with escape characters"""
        tokens = tokenize('"שורה\\nחדשה"')
        self.assertEqual(tokens[0].value, "שורה\nחדשה")
    
    def test_unclosed_string(self):
        """Test unclosed string raises error"""
        with self.assertRaises(LexerError) as context:
            tokenize('"לא נסגר')
        self.assertIn("מחרוזת לא נסגרה", str(context.exception))


class TestLexerKeywords(unittest.TestCase):
    """Test Hebrew keyword recognition - בדיקות מילות מפתח עבריות"""
    
    def test_if_keyword(self):
        """Test 'אם' keyword"""
        tokens = tokenize("אם")
        self.assertEqual(tokens[0].type, TokenType.IF)
        self.assertEqual(tokens[0].value, "אם")
    
    def test_else_keyword(self):
        """Test 'אחרת' keyword"""
        tokens = tokenize("אחרת")
        self.assertEqual(tokens[0].type, TokenType.ELSE)
    
    def test_while_keyword(self):
        """Test 'בעוד' keyword"""
        tokens = tokenize("בעוד")
        self.assertEqual(tokens[0].type, TokenType.WHILE)
    
    def test_for_keyword(self):
        """Test 'עבור' keyword"""
        tokens = tokenize("עבור")
        self.assertEqual(tokens[0].type, TokenType.FOR)
    
    def test_def_keyword(self):
        """Test 'הגדר' keyword"""
        tokens = tokenize("הגדר")
        self.assertEqual(tokens[0].type, TokenType.DEF)
    
    def test_return_keyword(self):
        """Test 'החזר' keyword"""
        tokens = tokenize("החזר")
        self.assertEqual(tokens[0].type, TokenType.RETURN)
    
    def test_print_keyword(self):
        """Test 'הדפס' keyword"""
        tokens = tokenize("הדפס")
        self.assertEqual(tokens[0].type, TokenType.PRINT)
    
    def test_true_keyword(self):
        """Test 'אמת' keyword"""
        tokens = tokenize("אמת")
        self.assertEqual(tokens[0].type, TokenType.TRUE)
    
    def test_false_keyword(self):
        """Test 'שקר' keyword"""
        tokens = tokenize("שקר")
        self.assertEqual(tokens[0].type, TokenType.FALSE)
    
    def test_none_keyword(self):
        """Test 'ריק' keyword"""
        tokens = tokenize("ריק")
        self.assertEqual(tokens[0].type, TokenType.NONE)


class TestLexerIdentifiers(unittest.TestCase):
    """Test identifier tokenization - בדיקות מזהים"""
    
    def test_hebrew_identifier(self):
        """Test Hebrew identifier"""
        tokens = tokenize("משתנה")
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "משתנה")
    
    def test_english_identifier(self):
        """Test English identifier"""
        tokens = tokenize("variable")
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "variable")
    
    def test_mixed_identifier(self):
        """Test mixed Hebrew-English identifier"""
        tokens = tokenize("משתנה1")
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "משתנה1")
    
    def test_underscore_identifier(self):
        """Test identifier with underscore"""
        tokens = tokenize("שם_משתנה")
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "שם_משתנה")


class TestLexerOperators(unittest.TestCase):
    """Test operator tokenization - בדיקות אופרטורים"""
    
    def test_arithmetic_operators(self):
        """Test arithmetic operators"""
        operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
        }
        for op, expected_type in operators.items():
            tokens = tokenize(op)
            self.assertEqual(tokens[0].type, expected_type)
    
    def test_comparison_operators(self):
        """Test comparison operators"""
        operators = {
            '==': TokenType.EQUALS,
            '!=': TokenType.NOT_EQUALS,
            '<': TokenType.LESS,
            '>': TokenType.GREATER,
            '<=': TokenType.LESS_EQ,
            '>=': TokenType.GREATER_EQ,
        }
        for op, expected_type in operators.items():
            tokens = tokenize(op)
            self.assertEqual(tokens[0].type, expected_type, f"Failed for {op}")
    
    def test_assignment_operators(self):
        """Test assignment operators"""
        operators = {
            '=': TokenType.ASSIGN,
            '+=': TokenType.PLUS_ASSIGN,
            '-=': TokenType.MINUS_ASSIGN,
        }
        for op, expected_type in operators.items():
            tokens = tokenize(op)
            self.assertEqual(tokens[0].type, expected_type)
    
    def test_power_operator(self):
        """Test power operator"""
        tokens = tokenize('**')
        self.assertEqual(tokens[0].type, TokenType.POWER)


class TestLexerDelimiters(unittest.TestCase):
    """Test delimiter tokenization - בדיקות תוחמים"""
    
    def test_parentheses(self):
        """Test parentheses"""
        tokens = tokenize('()')
        self.assertEqual(tokens[0].type, TokenType.LPAREN)
        self.assertEqual(tokens[1].type, TokenType.RPAREN)
    
    def test_brackets(self):
        """Test brackets"""
        tokens = tokenize('[]')
        self.assertEqual(tokens[0].type, TokenType.LBRACKET)
        self.assertEqual(tokens[1].type, TokenType.RBRACKET)
    
    def test_braces(self):
        """Test braces"""
        tokens = tokenize('{}')
        self.assertEqual(tokens[0].type, TokenType.LBRACE)
        self.assertEqual(tokens[1].type, TokenType.RBRACE)
    
    def test_comma(self):
        """Test comma"""
        tokens = tokenize(',')
        self.assertEqual(tokens[0].type, TokenType.COMMA)
    
    def test_colon(self):
        """Test colon"""
        tokens = tokenize(':')
        self.assertEqual(tokens[0].type, TokenType.COLON)
    
    def test_dot(self):
        """Test dot"""
        tokens = tokenize('.')
        self.assertEqual(tokens[0].type, TokenType.DOT)


class TestLexerIndentation(unittest.TestCase):
    """Test indentation handling - בדיקות הזחה"""
    
    def test_simple_indent(self):
        """Test simple indentation"""
        code = "אם:\n    הדפס()"
        tokens = tokenize(code)
        token_types = [t.type for t in tokens]
        self.assertIn(TokenType.INDENT, token_types)
    
    def test_dedent(self):
        """Test dedentation"""
        code = "אם:\n    הדפס()\nמשתנה"
        tokens = tokenize(code)
        token_types = [t.type for t in tokens]
        self.assertIn(TokenType.DEDENT, token_types)
    
    def test_multiple_indent_levels(self):
        """Test multiple indentation levels"""
        code = "אם:\n    בעוד:\n        הדפס()"
        tokens = tokenize(code)
        indent_count = sum(1 for t in tokens if t.type == TokenType.INDENT)
        self.assertEqual(indent_count, 2)


class TestLexerComments(unittest.TestCase):
    """Test comment handling - בדיקות הערות"""
    
    def test_single_line_comment(self):
        """Test single-line comment is skipped"""
        tokens = tokenize("# זו הערה\nמשתנה")
        # Comment should not appear in tokens
        values = [t.value for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertIn("משתנה", values)
        self.assertNotIn("הערה", [t.value for t in tokens])


class TestLexerCompleteCode(unittest.TestCase):
    """Test complete code snippets - בדיקות קוד מלא"""
    
    def test_function_definition(self):
        """Test function definition tokenization"""
        code = "הגדר שלום(שם):\n    הדפס(שם)"
        tokens = tokenize(code)
        
        # Check for key tokens
        token_types = [t.type for t in tokens]
        self.assertIn(TokenType.DEF, token_types)
        self.assertIn(TokenType.LPAREN, token_types)
        self.assertIn(TokenType.RPAREN, token_types)
        self.assertIn(TokenType.COLON, token_types)
        self.assertIn(TokenType.INDENT, token_types)
        self.assertIn(TokenType.PRINT, token_types)
    
    def test_if_statement(self):
        """Test if statement tokenization"""
        code = "אם x > 5:\n    הדפס(x)"
        tokens = tokenize(code)
        
        token_types = [t.type for t in tokens]
        self.assertIn(TokenType.IF, token_types)
        self.assertIn(TokenType.GREATER, token_types)
        self.assertIn(TokenType.COLON, token_types)
    
    def test_for_loop(self):
        """Test for loop tokenization"""
        code = "עבור i בתוך טווח(10):\n    הדפס(i)"
        tokens = tokenize(code)
        
        token_types = [t.type for t in tokens]
        self.assertIn(TokenType.FOR, token_types)
        self.assertIn(TokenType.IN, token_types)
        self.assertIn(TokenType.RANGE, token_types)


class TestLexerLineNumbers(unittest.TestCase):
    """Test line and column tracking - בדיקות מעקב שורות"""
    
    def test_line_numbers(self):
        """Test line number tracking"""
        code = "שורה1\nשורה2\nשורה3"
        tokens = tokenize(code)
        
        # Get identifier tokens
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        
        self.assertEqual(identifiers[0].line, 1)
        self.assertEqual(identifiers[1].line, 2)
        self.assertEqual(identifiers[2].line, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
