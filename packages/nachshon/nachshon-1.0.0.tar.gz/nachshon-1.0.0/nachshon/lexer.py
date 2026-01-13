# lexer.py
# Tokenizer for Nachshon (Hebrew keywords + Unicode variables)
# מנתח לקסיקלי לשפת נחשון

import re
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto


class TokenType(Enum):
    """Token types for Nachshon language"""
    # Keywords - מילות מפתח
    IF = auto()          # אם
    ELSE = auto()        # אחרת
    ELIF = auto()        # אחרת_אם
    WHILE = auto()       # בעוד
    FOR = auto()         # עבור
    IN = auto()          # בתוך
    DEF = auto()         # הגדר
    RETURN = auto()      # החזר
    BREAK = auto()       # הפסק
    CONTINUE = auto()    # המשך
    CLASS = auto()       # מחלקה
    IMPORT = auto()      # ייבא
    FROM = auto()        # מתוך
    AS = auto()          # בתור
    TRY = auto()         # נסה
    EXCEPT = auto()      # תפוס
    FINALLY = auto()     # לבסוף
    RAISE = auto()       # זרוק
    AND = auto()         # וגם
    OR = auto()          # או
    NOT = auto()         # לא
    PASS = auto()        # עבור_הלאה
    LAMBDA = auto()      # פונקציה_אנונימית
    WITH = auto()        # עם
    ASSERT = auto()      # וודא
    GLOBAL = auto()      # גלובלי
    YIELD = auto()       # הנב
    
    # Built-in functions - פונקציות מובנות
    PRINT = auto()       # הדפס
    INPUT = auto()       # קלט
    LEN = auto()         # אורך
    TYPE = auto()        # סוג
    RANGE = auto()       # טווח
    INT = auto()         # מספר_שלם
    FLOAT = auto()       # מספר_עשרוני
    STR = auto()         # מחרוזת
    LIST = auto()        # רשימה
    DICT = auto()        # מילון
    SET = auto()         # קבוצה
    BOOL = auto()        # בוליאני
    ABS = auto()         # ערך_מוחלט
    SUM = auto()         # סכום
    MIN = auto()         # מינימום
    MAX = auto()         # מקסימום
    SORTED = auto()      # ממוין
    REVERSED = auto()    # הפוך
    ENUMERATE = auto()   # מספר
    ZIP = auto()         # צמד
    MAP = auto()         # מפה
    FILTER = auto()      # סנן
    OPEN = auto()        # פתח
    
    # Literals - ליטרלים
    TRUE = auto()        # אמת
    FALSE = auto()       # שקר
    NONE = auto()        # ריק
    
    # Identifiers and literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    
    # Operators - אופרטורים
    PLUS = auto()        # +
    MINUS = auto()       # -
    MULTIPLY = auto()    # *
    DIVIDE = auto()      # /
    FLOOR_DIV = auto()   # //
    MODULO = auto()      # %
    POWER = auto()       # **
    ASSIGN = auto()      # =
    EQUALS = auto()      # ==
    NOT_EQUALS = auto()  # !=
    LESS = auto()        # <
    GREATER = auto()     # >
    LESS_EQ = auto()     # <=
    GREATER_EQ = auto()  # >=
    PLUS_ASSIGN = auto() # +=
    MINUS_ASSIGN = auto()# -=
    MUL_ASSIGN = auto()  # *=
    DIV_ASSIGN = auto()  # /=
    NOT_IN = auto()      # לא_בתוך (not in)
    
    # Delimiters - תוחמים
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    COMMA = auto()       # ,
    COLON = auto()       # :
    DOT = auto()         # .
    AT = auto()          # @
    
    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


# Hebrew keyword mappings - מיפוי מילות מפתח עבריות
HEBREW_KEYWORDS = {
    # Control flow - זרימת בקרה
    'אם': TokenType.IF,
    'אחרת': TokenType.ELSE,
    'אחרת_אם': TokenType.ELIF,
    'בעוד': TokenType.WHILE,
    'כל_עוד': TokenType.WHILE,  # Alternative for while
    'עבור': TokenType.FOR,
    'בתוך': TokenType.IN,
    
    # Functions and classes - פונקציות ומחלקות
    'הגדר': TokenType.DEF,
    'החזר': TokenType.RETURN,
    'הפסק': TokenType.BREAK,
    'המשך': TokenType.CONTINUE,
    'מחלקה': TokenType.CLASS,
    
    # Imports - ייבוא
    'ייבא': TokenType.IMPORT,
    'מתוך': TokenType.FROM,
    'בתור': TokenType.AS,
    
    # Exception handling - טיפול בחריגות
    'נסה': TokenType.TRY,
    'תפוס': TokenType.EXCEPT,
    'לבסוף': TokenType.FINALLY,
    'זרוק': TokenType.RAISE,
    
    # Logical operators - אופרטורים לוגיים
    'וגם': TokenType.AND,
    'או': TokenType.OR,
    'לא': TokenType.NOT,
    'לא_בתוך': TokenType.NOT_IN,  # not in
    
    # Other keywords - מילות מפתח נוספות
    'עבור_הלאה': TokenType.PASS,
    'עם': TokenType.WITH,
    'וודא': TokenType.ASSERT,
    'גלובלי': TokenType.GLOBAL,
    'הנב': TokenType.YIELD,
    'פונקציה_אנונימית': TokenType.LAMBDA,
    'למבדה': TokenType.LAMBDA,  # Short form for lambda
    
    # Built-in functions - פונקציות מובנות
    'הדפס': TokenType.PRINT,
    'קלט': TokenType.INPUT,
    'אורך': TokenType.LEN,
    'סוג': TokenType.TYPE,
    'טווח': TokenType.RANGE,
    'מספר_שלם': TokenType.INT,
    'מספר_עשרוני': TokenType.FLOAT,
    'מחרוזת': TokenType.STR,
    'רשימה': TokenType.LIST,
    'מילון': TokenType.DICT,
    'קבוצה': TokenType.SET,
    'בוליאני': TokenType.BOOL,
    'ערך_מוחלט': TokenType.ABS,
    'סכום': TokenType.SUM,
    'מינימום': TokenType.MIN,
    'מקסימום': TokenType.MAX,
    'ממוין': TokenType.SORTED,
    'הפוך': TokenType.REVERSED,
    'מספר_אינדקס': TokenType.ENUMERATE,
    'צמד': TokenType.ZIP,
    'מפה': TokenType.MAP,
    'סנן': TokenType.FILTER,
    'פתח': TokenType.OPEN,
    
    # Literals - ליטרלים
    'אמת': TokenType.TRUE,
    'שקר': TokenType.FALSE,
    'ריק': TokenType.NONE,
}

# Operator mappings
OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '//': TokenType.FLOOR_DIV,
    '%': TokenType.MODULO,
    '**': TokenType.POWER,
    '=': TokenType.ASSIGN,
    '==': TokenType.EQUALS,
    '!=': TokenType.NOT_EQUALS,
    '<': TokenType.LESS,
    '>': TokenType.GREATER,
    '<=': TokenType.LESS_EQ,
    '>=': TokenType.GREATER_EQ,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.MUL_ASSIGN,
    '/=': TokenType.DIV_ASSIGN,
}

DELIMITERS = {
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    ',': TokenType.COMMA,
    ':': TokenType.COLON,
    '.': TokenType.DOT,
    '@': TokenType.AT,
}


@dataclass
class Token:
    """Represents a single token"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', שורה:{self.line}, עמודה:{self.column})"


class LexerError(Exception):
    """Error during lexical analysis - שגיאת ניתוח לקסיקלי"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"שגיאה בשורה {line}, עמודה {column}: {message}")


class Lexer:
    """Lexer for Nachshon language - מנתח לקסיקלי לשפת נחשון"""
    
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]  # Stack for tracking indentation
        self.bracket_depth = 0   # Track bracket nesting to suppress indentation
        
    def current_char(self) -> Optional[str]:
        """Get current character or None if at end"""
        if self.pos >= len(self.code):
            return None
        return self.code[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Look ahead without consuming"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.code):
            return None
        return self.code[peek_pos]
    
    def advance(self) -> Optional[str]:
        """Move to next character"""
        char = self.current_char()
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self) -> None:
        """Skip spaces and tabs (not newlines)"""
        while self.current_char() in (' ', '\t'):
            self.advance()
    
    def skip_comment(self) -> None:
        """Skip single-line comment starting with #"""
        while self.current_char() is not None and self.current_char() != '\n':
            self.advance()
    
    def read_string(self, quote_char: str) -> Token:
        """Read a string literal"""
        start_line = self.line
        start_col = self.column
        self.advance()  # Skip opening quote
        
        value = ""
        while self.current_char() is not None:
            char = self.current_char()
            
            if char == quote_char:
                self.advance()  # Skip closing quote
                return Token(TokenType.STRING, value, start_line, start_col)
            
            if char == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == '\\':
                    value += '\\'
                elif escape_char == quote_char:
                    value += quote_char
                else:
                    value += escape_char
                self.advance()
            else:
                value += char
                self.advance()
        
        raise LexerError("מחרוזת לא נסגרה", start_line, start_col)
    
    def read_number(self) -> Token:
        """Read a numeric literal (decimal, hex, octal, or binary)"""
        start_line = self.line
        start_col = self.column
        value = ""
        has_dot = False
        
        # Check for hex (0x), octal (0o), or binary (0b) prefix
        if self.current_char() == '0' and self.peek() in ('x', 'X', 'o', 'O', 'b', 'B'):
            value = self.current_char()
            self.advance()
            prefix_char = self.current_char().lower()
            value += self.current_char()
            self.advance()
            
            if prefix_char == 'x':
                # Hexadecimal
                while self.current_char() is not None and self.current_char() in '0123456789abcdefABCDEF':
                    value += self.current_char()
                    self.advance()
            elif prefix_char == 'o':
                # Octal
                while self.current_char() is not None and self.current_char() in '01234567':
                    value += self.current_char()
                    self.advance()
            elif prefix_char == 'b':
                # Binary
                while self.current_char() is not None and self.current_char() in '01':
                    value += self.current_char()
                    self.advance()
            
            return Token(TokenType.NUMBER, value, start_line, start_col)
        
        while self.current_char() is not None:
            char = self.current_char()
            if char.isdigit():
                value += char
                self.advance()
            elif char == '.' and not has_dot and self.peek() and self.peek().isdigit():
                value += char
                has_dot = True
                self.advance()
            else:
                break
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_identifier_or_keyword(self) -> Token:
        """Read an identifier or keyword (supports Hebrew Unicode)"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        while self.current_char() is not None:
            char = self.current_char()
            # Allow Hebrew letters, English letters, digits, and underscore
            if self._is_identifier_char(char):
                value += char
                self.advance()
            else:
                break
        
        # Check if it's a Hebrew keyword
        if value in HEBREW_KEYWORDS:
            return Token(HEBREW_KEYWORDS[value], value, start_line, start_col)
        
        return Token(TokenType.IDENTIFIER, value, start_line, start_col)
    
    def _is_identifier_start(self, char: str) -> bool:
        """Check if character can start an identifier"""
        if char is None:
            return False
        # Hebrew letters: U+0590 to U+05FF
        # English letters and underscore
        return (char.isalpha() or char == '_' or 
                '\u0590' <= char <= '\u05FF')
    
    def _is_identifier_char(self, char: str) -> bool:
        """Check if character can be part of an identifier"""
        if char is None:
            return False
        return self._is_identifier_start(char) or char.isdigit()
    
    def read_operator(self) -> Token:
        """Read an operator (possibly multi-character)"""
        start_line = self.line
        start_col = self.column
        char = self.current_char()
        
        # Check for two-character operators first
        two_char = char + (self.peek() or '')
        if two_char in OPERATORS:
            self.advance()
            self.advance()
            return Token(OPERATORS[two_char], two_char, start_line, start_col)
        
        # Single character operator
        if char in OPERATORS:
            self.advance()
            return Token(OPERATORS[char], char, start_line, start_col)
        
        raise LexerError(f"אופרטור לא מוכר: '{char}'", start_line, start_col)
    
    def handle_indentation(self) -> List[Token]:
        """Handle indentation at the start of a line"""
        tokens = []
        spaces = 0
        
        while self.current_char() in (' ', '\t'):
            if self.current_char() == ' ':
                spaces += 1
            else:  # tab
                spaces += 4  # Treat tab as 4 spaces
            self.advance()
        
        # Skip empty lines and comment-only lines
        if self.current_char() in ('\n', '#', None):
            return tokens
        
        current_indent = self.indent_stack[-1]
        
        if spaces > current_indent:
            self.indent_stack.append(spaces)
            tokens.append(Token(TokenType.INDENT, '', self.line, 1))
        elif spaces < current_indent:
            while self.indent_stack and spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, '', self.line, 1))
            
            if self.indent_stack and spaces != self.indent_stack[-1]:
                raise LexerError("הזחה לא תקינה", self.line, 1)
        
        return tokens
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        self.tokens = []
        at_line_start = True
        
        while self.current_char() is not None:
            char = self.current_char()
            
            # Handle newlines - skip NEWLINE token inside brackets
            if char == '\n':
                if self.bracket_depth == 0:
                    self.tokens.append(Token(TokenType.NEWLINE, '\\n', self.line, self.column))
                self.advance()
                at_line_start = True
                continue
            
            # Handle indentation at line start - skip inside brackets
            if at_line_start:
                if self.bracket_depth == 0:
                    indent_tokens = self.handle_indentation()
                    self.tokens.extend(indent_tokens)
                else:
                    # Inside brackets, just skip the whitespace
                    self.skip_whitespace()
                at_line_start = False
                continue
            
            # Skip spaces/tabs mid-line
            if char in (' ', '\t'):
                self.skip_whitespace()
                continue
            
            # Skip comments
            if char == '#':
                self.skip_comment()
                continue
            
            # String literals
            if char in ('"', "'"):
                self.tokens.append(self.read_string(char))
                continue
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if self._is_identifier_start(char):
                self.tokens.append(self.read_identifier_or_keyword())
                continue
            
            # Delimiters - track bracket depth
            if char in DELIMITERS:
                # Track opening brackets
                if char in '([{':
                    self.bracket_depth += 1
                elif char in ')]}':
                    self.bracket_depth = max(0, self.bracket_depth - 1)
                self.tokens.append(Token(DELIMITERS[char], char, self.line, self.column))
                self.advance()
                continue
            
            # Operators
            if char in '+-*/%=<>!':
                self.tokens.append(self.read_operator())
                continue
            
            # Unknown character
            raise LexerError(f"תו לא מוכר: '{char}'", self.line, self.column)
        
        # Add remaining DEDENT tokens
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        
        return self.tokens


def tokenize(code: str) -> List[Token]:
    """Convenience function to tokenize code"""
    lexer = Lexer(code)
    return lexer.tokenize()


if __name__ == "__main__":
    # Test the lexer
    test_code = '''הגדר שלום(שם):
    הדפס("שלום, " + שם)

שלום("עולם")
'''
    
    try:
        tokens = tokenize(test_code)
        for token in tokens:
            print(token)
    except LexerError as e:
        print(f"שגיאה: {e}")
