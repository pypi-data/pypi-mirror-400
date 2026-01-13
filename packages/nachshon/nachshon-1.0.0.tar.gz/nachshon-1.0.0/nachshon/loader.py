# loader.py
# Module loader for Nachshon - מטען מודולים לנחשון

import sys
import os
import importlib.abc
import importlib.machinery
import importlib.util

try:
    from .lexer import Lexer, LexerError
    from .parser import Parser, ParserError
    from .transpiler import Transpiler, TranspilerError
except ImportError:
    from nachshon.lexer import Lexer, LexerError
    from nachshon.parser import Parser, ParserError
    from nachshon.transpiler import Transpiler, TranspilerError


class NachshonLoader(importlib.abc.SourceLoader):
    """Custom loader for .נח files"""
    
    def __init__(self, path):
        self.path = path
    
    def get_filename(self, fullname):
        return self.path
    
    def get_data(self, path):
        """Read and compile .נח file to Python"""
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Compile to Python
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            transpiler = Transpiler(ast)
            python_code = transpiler.transpile()
            return python_code.encode('utf-8')
        except (LexerError, ParserError, TranspilerError) as e:
            raise ImportError(f"שגיאה בייבוא מודול נחשון: {e}")


class NachshonFinder(importlib.abc.MetaPathFinder):
    """Finder that locates .נח modules"""
    
    def __init__(self, search_paths=None):
        self.search_paths = search_paths or ['.']
    
    def find_spec(self, fullname, path, target=None):
        """Find a .נח module"""
        # Get module name (last part of dotted name)
        mod_name = fullname.rsplit('.', 1)[-1]
        
        # Search in paths
        search_paths = list(path or []) + self.search_paths
        
        for search_path in search_paths:
            # Try Hebrew extension first (primary)
            nach_path = os.path.join(search_path, mod_name + '.נח')
            if os.path.isfile(nach_path):
                return importlib.machinery.ModuleSpec(
                    fullname,
                    NachshonLoader(nach_path),
                    origin=nach_path
                )
            
            # Try legacy .nach extension for backwards compatibility
            nach_path = os.path.join(search_path, mod_name + '.nach')
            if os.path.isfile(nach_path):
                return importlib.machinery.ModuleSpec(
                    fullname,
                    NachshonLoader(nach_path),
                    origin=nach_path
                )
            
            # Try package (directory with __init__.נח)
            package_path = os.path.join(search_path, mod_name)
            if os.path.isdir(package_path):
                init_path = os.path.join(package_path, '__init__.נח')
                if os.path.isfile(init_path):
                    return importlib.machinery.ModuleSpec(
                        fullname,
                        NachshonLoader(init_path),
                        origin=init_path,
                        is_package=True,
                        submodule_search_locations=[package_path]
                    )
        
        return None


def install_loader(search_paths=None):
    """Install the Nachshon import system"""
    finder = NachshonFinder(search_paths)
    sys.meta_path.insert(0, finder)
    return finder


def uninstall_loader(finder):
    """Uninstall a Nachshon finder"""
    if finder in sys.meta_path:
        sys.meta_path.remove(finder)


def import_nachshon_module(module_name: str, search_paths=None):
    """Import a Nachshon module by name
    
    Args:
        module_name: Name of the module (without .נח extension)
        search_paths: Optional list of directories to search
    
    Returns:
        The imported module
    """
    if search_paths is None:
        search_paths = ['.', os.getcwd()]
    
    finder = NachshonFinder(search_paths)
    spec = finder.find_spec(module_name, None)
    
    if spec is None:
        raise ImportError(f"לא נמצא מודול נחשון: {module_name}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module


# Helper function for use in transpiled code
def ייבא_נחשון(שם_מודול, נתיבים=None):
    """Import a Nachshon module (Hebrew API)
    
    Usage in Nachshon:
        מודול = ייבא_נחשון("שם_המודול")
    """
    return import_nachshon_module(שם_מודול, נתיבים)


if __name__ == "__main__":
    # Test the loader
    import sys
    
    # Install the loader
    install_loader(['.', './examples'])
    
    # Try importing a test module
    try:
        print("Testing Nachshon module import system...")
        # This would work if there's a module to import
        print("✅ Module loader installed successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
