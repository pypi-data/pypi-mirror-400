# נחשון - שפת תכנות עברית
# Nachshon - Hebrew Programming Language

# Lazy imports to avoid circular import issues when running tests
# or when the package isn't properly installed
def __getattr__(name):
    if name == 'main':
        from .cli import main
        return main
    if name == 'run_command':
        from .cli import run_command
        return run_command
    raise AttributeError(f"module 'src' has no attribute '{name}'")

__all__ = ['main', 'run_command']