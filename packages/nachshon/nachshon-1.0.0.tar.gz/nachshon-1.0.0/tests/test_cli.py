# test_cli.py
# Unit tests for Nachshon CLI - בדיקות יחידה ל-CLI

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import tempfile
import io
from contextlib import redirect_stdout, redirect_stderr
from nachshon.cli import compile_code, read_file, write_file, NachshonError


class TestCLICompile(unittest.TestCase):
    """Test compile_code function - בדיקות קומפילציה"""
    
    def test_compile_simple(self):
        """Test simple compilation"""
        code = 'הדפס("שלום")'
        result = compile_code(code)
        self.assertIn('print("שלום")', result)
    
    def test_compile_function(self):
        """Test function compilation"""
        code = """הגדר שלום():
    הדפס("שלום")
"""
        result = compile_code(code)
        self.assertIn('def שלום():', result)
    
    def test_compile_with_syntax_error(self):
        """Test compilation with syntax error"""
        code = "הגדר שלום\n    הדפס()"  # Missing parentheses
        # Should raise an error
        with self.assertRaises(Exception):
            compile_code(code)


class TestCLIFileOperations(unittest.TestCase):
    """Test file operations - בדיקות קבצים"""
    
    def test_read_file(self):
        """Test reading file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nach', 
                                         encoding='utf-8', delete=False) as f:
            f.write('הדפס("בדיקה")')
            temp_path = f.name
        
        try:
            content = read_file(temp_path)
            self.assertEqual(content, 'הדפס("בדיקה")')
        finally:
            os.unlink(temp_path)
    
    def test_read_nonexistent_file(self):
        """Test reading non-existent file raises error"""
        with self.assertRaises(NachshonError) as context:
            read_file("/nonexistent/path/file.nach")
        self.assertIn("קובץ לא נמצא", str(context.exception))
    
    def test_write_file(self):
        """Test writing file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', 
                                         encoding='utf-8', delete=False) as f:
            temp_path = f.name
        
        try:
            write_file(temp_path, "print('test')")
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, "print('test')")
        finally:
            os.unlink(temp_path)


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI - בדיקות אינטגרציה"""
    
    def test_compile_and_execute(self):
        """Test compile and execute flow"""
        code = """x = 5
y = 10
z = x + y
"""
        python_code = compile_code(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['z'], 15)
    
    def test_hebrew_program_execution(self):
        """Test full Hebrew program execution"""
        code = """הגדר חישוב_שטח(ר, א):
    החזר ר * א

שטח = חישוב_שטח(5, 10)
"""
        python_code = compile_code(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['שטח'], 50)


class TestCLIUnicode(unittest.TestCase):
    """Test Unicode handling - בדיקות יוניקוד"""
    
    def test_hebrew_identifiers(self):
        """Test Hebrew identifiers work correctly"""
        code = """שם = "יוסי"
גיל = 30
משכורת = 15000.5
"""
        python_code = compile_code(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['שם'], "יוסי")
        self.assertEqual(namespace['גיל'], 30)
        self.assertEqual(namespace['משכורת'], 15000.5)
    
    def test_hebrew_strings(self):
        """Test Hebrew strings work correctly"""
        code = 'הודעה = "שלום עולם, זו בדיקה!"'
        python_code = compile_code(code)
        namespace = {}
        exec(python_code, namespace)
        self.assertEqual(namespace['הודעה'], "שלום עולם, זו בדיקה!")


class TestCLIErrorMessages(unittest.TestCase):
    """Test error messages are in Hebrew - בדיקות הודעות שגיאה"""
    
    def test_lexer_error_in_hebrew(self):
        """Test lexer errors are in Hebrew"""
        from nachshon.lexer import Lexer, LexerError
        
        try:
            lexer = Lexer('"מחרוזת לא סגורה')
            lexer.tokenize()
            self.fail("Should have raised LexerError")
        except LexerError as e:
            # Error message should be in Hebrew
            self.assertIn("מחרוזת לא נסגרה", str(e))
    
    def test_parser_error_in_hebrew(self):
        """Test parser errors are in Hebrew"""
        from nachshon.parser import ParserError, parse
        
        try:
            parse("הגדר שלום\n    הדפס()")  # Missing ()
            self.fail("Should have raised ParserError")
        except ParserError as e:
            # Error message should be in Hebrew
            self.assertIn("ציפיתי", str(e))


if __name__ == '__main__':
    unittest.main(verbosity=2)
