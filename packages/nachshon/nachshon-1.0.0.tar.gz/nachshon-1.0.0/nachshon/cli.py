# cli.py
# Command-line interface for Nachshon
# ממשק שורת פקודה לנחשון

import sys
import os
import argparse
import traceback
import readline  # For history support
from typing import Optional

try:
    from .lexer import Lexer, LexerError
    from .parser import Parser, ParserError
    from .transpiler import Transpiler, TranspilerError
    from .loader import install_loader, import_nachshon_module, ייבא_נחשון
except ImportError:
    from nachshon.lexer import Lexer, LexerError
    from nachshon.parser import Parser, ParserError
    from nachshon.transpiler import Transpiler, TranspilerError
    from nachshon.loader import install_loader, import_nachshon_module, ייבא_נחשון


VERSION = "1.0.0"
EXTENSION = ".נח"
HISTORY_FILE = os.path.expanduser("~/.nachshon_history")


class NachshonError(Exception):
    """Base error for Nachshon - שגיאת נחשון"""
    pass


def print_error(message: str) -> None:
    """Print error message in Hebrew"""
    print(f"❌ שגיאה: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print success message in Hebrew"""
    print(f"✅ {message}")


def read_file(filename: str) -> str:
    """Read source file with UTF-8 encoding"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise NachshonError(f"קובץ לא נמצא: {filename}")
    except IOError as e:
        raise NachshonError(f"שגיאת קריאה מקובץ: {e}")


def write_file(filename: str, content: str) -> None:
    """Write output file with UTF-8 encoding"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    except IOError as e:
        raise NachshonError(f"שגיאת כתיבה לקובץ: {e}")


def compile_code(source: str) -> str:
    """Compile Nachshon source code to Python"""
    # Tokenize
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Parse
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Transpile
    transpiler = Transpiler(ast)
    return transpiler.transpile()


def run_command(filename: str, show_python: bool = False) -> None:
    """Run a Nachshon file - הרצת קובץ נחשון"""
    print(f"🚀 מריץ: {filename}")
    
    source = read_file(filename)
    python_code = compile_code(source)
    
    if show_python:
        print("\n--- קוד פייתון ---")
        print(python_code)
        print("--- סוף קוד ---\n")
    
    # Execute the Python code
    try:
        # Import the loader to enable importing other .nach modules
        try:
            from .loader import install_loader, ייבא_נחשון
        except ImportError:
            from nachshon.loader import install_loader, ייבא_נחשון
        
        # Install the loader with the file's directory in search path
        file_dir = os.path.dirname(os.path.abspath(filename))
        install_loader([file_dir, '.'])
        
        # Create a fresh namespace for execution
        exec_globals = {
            "__name__": "__main__", 
            "__file__": filename,
            "ייבא_נחשון": ייבא_נחשון  # Make available for dynamic imports
        }
        exec(python_code, exec_globals)
    except Exception as e:
        print_error(f"שגיאת הרצה: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()


def build_command(filename: str, output: Optional[str] = None) -> None:
    """Build a Nachshon file to Python - בניית קובץ פייתון"""
    print(f"🔨 בונה: {filename}")
    
    source = read_file(filename)
    python_code = compile_code(source)
    
    # Determine output filename
    if output is None:
        base = os.path.splitext(filename)[0]
        output = base + ".py"
    
    write_file(output, python_code)
    print_success(f"נוצר קובץ: {output}")


def repl_command() -> None:
    """Interactive REPL - מצב אינטראקטיבי"""
    print(f"🐍 נחשון {VERSION} - מצב אינטראקטיבי")
    print("הקלד 'יציאה' או 'exit' לסיום")
    print("הקלד 'עזרה' לקבלת עזרה")
    print("הקלד 'היסטוריה' לצפייה בהיסטוריה")
    print("הקלד 'נקה' לניקוי המסך")
    print("-" * 40)
    
    # Load command history
    try:
        readline.read_history_file(HISTORY_FILE)
        readline.set_history_length(1000)
    except (FileNotFoundError, PermissionError):
        pass
    
    # Keep track of defined variables/functions
    exec_globals = {"__name__": "__main__"}
    
    # Command history (for display)
    history_num = 1
    
    # Multi-line input handling
    buffer = []
    in_block = False
    
    while True:
        try:
            # Prompt
            if in_block:
                prompt = "...   "
            else:
                prompt = f"[{history_num}] נחשון> "
            
            line = input(prompt)
            
            # Check for exit
            if line.strip() in ('יציאה', 'exit', 'quit'):
                print("להתראות! 👋")
                # Save history
                try:
                    readline.write_history_file(HISTORY_FILE)
                except (PermissionError, IOError):
                    pass
                break
            
            # Check for help
            if line.strip() in ('עזרה', 'help'):
                print_repl_help()
                continue
            
            # Check for history command
            if line.strip() in ('היסטוריה', 'history'):
                print_history()
                continue
            
            # Check for clear command
            if line.strip() in ('נקה', 'clear'):
                os.system('clear' if os.name != 'nt' else 'cls')
                print(f"🐍 נחשון {VERSION} - מצב אינטראקטיבי")
                continue
            
            # Check for vars command - show defined variables
            if line.strip() in ('משתנים', 'vars'):
                print_vars(exec_globals)
                continue
            
            # Check for reset command
            if line.strip() in ('איפוס', 'reset'):
                exec_globals = {"__name__": "__main__"}
                print("✅ הסביבה אופסה")
                continue
            
            # Handle multi-line input
            if line.strip().endswith(':'):
                buffer.append(line)
                in_block = True
                continue
            
            if in_block:
                if line.strip() == '':
                    # End of block
                    in_block = False
                    source = '\n'.join(buffer)
                    buffer = []
                else:
                    buffer.append(line)
                    continue
            else:
                source = line
            
            if not source.strip():
                continue
            
            history_num += 1
            
            # Compile and execute
            try:
                python_code = compile_code(source)
                result = exec_with_result(python_code, exec_globals)
                if result is not None:
                    print(f"=> {result}")
            except (LexerError, ParserError, TranspilerError) as e:
                print_error(str(e))
            except Exception as e:
                print_error(f"שגיאת הרצה: {e}")
                
        except KeyboardInterrupt:
            print("\n(השתמש ב־'יציאה' לסיום)")
            buffer = []
            in_block = False
        except EOFError:
            print("\nלהתראות! 👋")
            try:
                readline.write_history_file(HISTORY_FILE)
            except (PermissionError, IOError):
                pass
            break


def exec_with_result(code: str, globals_dict: dict):
    """Execute code and try to get result of last expression"""
    lines = code.strip().split('\n')
    
    # Check if last non-comment line is an expression
    for line in reversed(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            # Simple heuristic: if it doesn't have = (assignment) and isn't 
            # a control structure, try to eval it
            if (not any(stripped.startswith(kw) for kw in ['def ', 'class ', 'if ', 'while ', 'for ', 'try:', 'with ']) 
                and '=' not in stripped or '==' in stripped or '!=' in stripped):
                try:
                    # Try to separate and eval the last expression
                    exec('\n'.join(lines[:-1]), globals_dict)
                    return eval(stripped, globals_dict)
                except:
                    pass
            break
    
    exec(code, globals_dict)
    return None


def print_history() -> None:
    """Print command history"""
    history_length = readline.get_current_history_length()
    print(f"📜 היסטוריה ({history_length} פקודות):")
    for i in range(1, min(21, history_length + 1)):  # Show last 20
        item = readline.get_history_item(i)
        if item:
            print(f"  {i}: {item}")
    if history_length > 20:
        print(f"  ... ועוד {history_length - 20} פקודות")


def print_vars(globals_dict: dict) -> None:
    """Print user-defined variables"""
    user_vars = {k: v for k, v in globals_dict.items() 
                 if not k.startswith('_') and k not in ('__name__', '__builtins__')}
    if user_vars:
        print("📊 משתנים מוגדרים:")
        for name, value in user_vars.items():
            val_type = type(value).__name__
            val_str = repr(value)
            if len(val_str) > 50:
                val_str = val_str[:47] + "..."
            print(f"  {name} ({val_type}): {val_str}")
    else:
        print("אין משתנים מוגדרים")


def print_repl_help() -> None:
    """Print REPL help - עזרה למצב אינטראקטיבי"""
    help_text = """
╔════════════════════════════════════════════════════════════╗
║                    עזרה - נחשון                            ║
╠════════════════════════════════════════════════════════════╣
║  מילות מפתח:                                               ║
║    אם, אחרת, אחרת_אם  - תנאים                              ║
║    בעוד              - לולאת while                         ║
║    עבור...בתוך       - לולאת for                           ║
║    הגדר              - הגדרת פונקציה                       ║
║    החזר              - החזרת ערך                           ║
║    הפסק, המשך        - בקרת לולאה                          ║
║    מחלקה             - הגדרת מחלקה                         ║
║    נסה, תפוס, זרוק   - טיפול בשגיאות                       ║
║    עם...בתור         - מנהל הקשר                           ║
║    @מעטר             - מעטר לפונקציה                       ║
╠════════════════════════════════════════════════════════════╣
║  פונקציות מובנות:                                          ║
║    הדפס()  - הדפסה                                         ║
║    קלט()   - קריאת קלט                                     ║
║    אורך()  - אורך רשימה/מחרוזת                             ║
║    טווח()  - טווח מספרים                                   ║
║    סוג()   - סוג משתנה                                     ║
║    מפה(), סנן(), ממוין() - פונקציות פונקציונליות          ║
╠════════════════════════════════════════════════════════════╣
║  ערכים מיוחדים:                                            ║
║    אמת, שקר  - ערכים בוליאניים                             ║
║    ריק       - None                                        ║
╠════════════════════════════════════════════════════════════╣
║  תחביר מתקדם:                                              ║
║    [x עבור x בתוך ר] - הבנת רשימות                         ║
║    ר[1:5]           - חיתוך                                ║
║    פונקציה_אנונימית x: x*2 - למבדה                         ║
╠════════════════════════════════════════════════════════════╣
║  פקודות REPL:                                              ║
║    יציאה / exit    - יציאה                                 ║
║    עזרה / help     - הצגת עזרה                             ║
║    היסטוריה        - הצגת היסטוריית פקודות                 ║
║    משתנים / vars   - הצגת משתנים מוגדרים                   ║
║    נקה / clear     - ניקוי מסך                             ║
║    איפוס / reset   - איפוס סביבה                           ║
╠════════════════════════════════════════════════════════════╣
║  מקשים:                                                    ║
║    ↑/↓              - ניווט בהיסטוריה                      ║
║    Ctrl+R           - חיפוש בהיסטוריה                      ║
║    Ctrl+C           - ביטול שורה נוכחית                    ║
║    Ctrl+D           - יציאה                                ║
╚════════════════════════════════════════════════════════════╝
"""
    print(help_text)


def check_command(filename: str) -> None:
    """Check syntax without running - בדיקת תחביר"""
    print(f"🔍 בודק: {filename}")
    
    source = read_file(filename)
    
    try:
        compile_code(source)
        print_success("אין שגיאות תחביר!")
    except (LexerError, ParserError, TranspilerError) as e:
        print_error(str(e))
        sys.exit(1)


def show_tokens_command(filename: str) -> None:
    """Show tokens for debugging - הצגת טוקנים"""
    print(f"🔤 טוקנים: {filename}")
    
    source = read_file(filename)
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(f"  {token}")


def show_ast_command(filename: str) -> None:
    """Show AST for debugging - הצגת עץ תחביר"""
    print(f"🌳 עץ תחביר: {filename}")
    
    source = read_file(filename)
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    def print_node(node, indent=0):
        prefix = "  " * indent
        if hasattr(node, 'type'):
            print(f"{prefix}{node.type.name}", end="")
            if hasattr(node, 'name') and node.name:
                print(f" ({node.name})", end="")
            if hasattr(node, 'value') and node.value is not None:
                print(f" = {node.value}", end="")
            print()
        
        # Print children
        for attr in ['body', 'else_body', 'condition', 'expression', 
                     'left', 'right', 'operand', 'callee', 'args', 
                     'elements', 'pairs', 'target', 'value']:
            if hasattr(node, attr):
                child = getattr(node, attr)
                if isinstance(child, list):
                    for item in child:
                        if hasattr(item, 'type'):
                            print_node(item, indent + 1)
                elif hasattr(child, 'type'):
                    print_node(child, indent + 1)
    
    for node in ast.body:
        print_node(node)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog='nachshon',
        description='נחשון - שפת תכנות עברית מבוססת פייתון',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
דוגמאות:
  nachshon run program.נח      # הרצת תוכנית
  nachshon build program.נח    # בניית קובץ פייתון
  nachshon repl                # מצב אינטראקטיבי
  nachshon check program.נח    # בדיקת תחביר
'''
    )
    
    parser.add_argument('--version', '-v', action='version', 
                       version=f'נחשון {VERSION}')
    
    subparsers = parser.add_subparsers(dest='command', help='פקודות')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='הרצת קובץ נחשון')
    run_parser.add_argument('file', help='קובץ להרצה')
    run_parser.add_argument('--show-python', '-p', action='store_true',
                           help='הצג קוד פייתון לפני הרצה')
    run_parser.add_argument('--debug', '-d', action='store_true',
                           help='הצג מידע דיבאג')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='בניית קובץ פייתון')
    build_parser.add_argument('file', help='קובץ לבנייה')
    build_parser.add_argument('--output', '-o', help='שם קובץ פלט')
    
    # REPL command
    subparsers.add_parser('repl', help='מצב אינטראקטיבי')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='בדיקת תחביר')
    check_parser.add_argument('file', help='קובץ לבדיקה')
    
    # Tokens command (debug)
    tokens_parser = subparsers.add_parser('tokens', help='הצגת טוקנים (דיבאג)')
    tokens_parser.add_argument('file', help='קובץ')
    
    # AST command (debug)
    ast_parser = subparsers.add_parser('ast', help='הצגת עץ תחביר (דיבאג)')
    ast_parser.add_argument('file', help='קובץ')
    
    # Check if the first argument is a .נח file (direct execution without 'run' command)
    if len(sys.argv) > 1 and sys.argv[1].endswith(EXTENSION) and os.path.isfile(sys.argv[1]):
        # Direct file execution: nachshon file.נח [--show-python] [--debug]
        try:
            show_python = '--show-python' in sys.argv or '-p' in sys.argv
            run_command(sys.argv[1], show_python)
            return
        except NachshonError as e:
            print_error(str(e))
            sys.exit(1)
        except (LexerError, ParserError, TranspilerError) as e:
            print_error(str(e))
            sys.exit(1)
    
    args = parser.parse_args()
    
    try:
        if args.command == 'run':
            run_command(args.file, args.show_python)
        elif args.command == 'build':
            build_command(args.file, args.output)
        elif args.command == 'repl':
            repl_command()
        elif args.command == 'check':
            check_command(args.file)
        elif args.command == 'tokens':
            show_tokens_command(args.file)
        elif args.command == 'ast':
            show_ast_command(args.file)
        else:
            # Default: show help or start REPL
            if len(sys.argv) == 1:
                repl_command()
            else:
                parser.print_help()
                
    except NachshonError as e:
        print_error(str(e))
        sys.exit(1)
    except (LexerError, ParserError, TranspilerError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nבוטל על ידי המשתמש")
        sys.exit(130)


if __name__ == "__main__":
    main()
