"""
Code Source Inspector - Show implementation of any RL function.

This module allows you to see the actual implementation code of any function
by calling function_name.show() - perfect for when you need to copy code manually!
"""

import inspect
import textwrap


class ShowableFunction:
    """
    Wrapper that adds .show() method to functions.
    
    Usage:
    >>> rl.policy_iteration.show()
    # Shows the complete implementation code
    """
    
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        # Copy all attributes from original function
        for attr in dir(func):
            if not attr.startswith('_') and attr not in ['show', 'func']:
                try:
                    setattr(self, attr, getattr(func, attr))
                except:
                    pass
    
    def __call__(self, *args, **kwargs):
        """Call the original function."""
        return self.func(*args, **kwargs)
    
    def show(self, include_imports=True, clean=True):
        """
        Display the source code of this function.
        
        Parameters:
        -----------
        include_imports : bool, optional (default=True)
            Whether to show required imports
        clean : bool, optional (default=True)
            If True, removes docstrings and keeps only code with humanized comments
        
        Example:
        --------
        >>> from sohail_mlsuite import rl
        >>> rl.policy_iteration.show()
        # Only clean code is printed, ready to copy!
        """
        print("=" * 80)
        print(f"CODE: {self.__name__}")
        print("=" * 80)
        
        # Get source code
        try:
            source = inspect.getsource(self.func)
            
            # Remove leading indentation
            source = textwrap.dedent(source)
            
            # Show required imports
            if include_imports:
                imports = self._get_required_imports()
                if imports:
                    print("\n# Required imports:")
                    for imp in imports:
                        print(imp)
                    print()
            
            # Clean the code if requested
            if clean:
                source = self._clean_code(source)
            
            # Show the code
            print(source)
            
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"Error: Could not retrieve source code - {e}")
            print("The function might be built-in or compiled.")
    
    def _clean_code(self, source):
        """Remove docstrings but keep inline comments."""
        lines = source.split('\n')
        cleaned_lines = []
        in_docstring = False
        docstring_char = None
        skip_next = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip if we marked this line to skip
            if skip_next:
                skip_next = False
                continue
            
            # Detect start of docstring
            if not in_docstring:
                # Check for docstring after function definition
                if '"""' in stripped or "'''" in stripped:
                    # Check if it's a docstring (not a regular string)
                    if i > 0 and ('def ' in lines[i-1] or cleaned_lines and 'def ' in cleaned_lines[-1]):
                        in_docstring = True
                        docstring_char = '"""' if '"""' in stripped else "'''"
                        # Check if docstring ends on same line
                        if stripped.count(docstring_char) >= 2:
                            in_docstring = False
                        continue
                    else:
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            else:
                # We're inside a docstring, look for end
                if docstring_char in stripped:
                    in_docstring = False
                continue
        
        # Join and clean up extra blank lines
        cleaned = '\n'.join(cleaned_lines)
        
        # Remove excessive blank lines (more than 2 consecutive)
        while '\n\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n\n', '\n\n')
        
        return cleaned.strip()
    
    def _get_required_imports(self):
        """Determine which imports this function needs."""
        imports = []
        source = inspect.getsource(self.func)
        
        # Check for common imports
        if 'np.' in source or 'numpy.' in source:
            imports.append("import numpy as np")
        
        if 'plt.' in source or 'matplotlib' in source:
            imports.append("import matplotlib.pyplot as plt")
        
        if 'gym.' in source or 'gymnasium' in source:
            imports.append("import gymnasium as gym")
        
        return imports
    
    def __repr__(self):
        return f"<ShowableFunction: {self.__name__}>"


def make_showable(func):
    """
    Decorator to add .show() method to a function.
    
    Usage:
    @make_showable
    def my_function():
        pass
    
    Then: my_function.show() will display the source code
    """
    return ShowableFunction(func)


def add_show_to_module(module):
    """
    Add .show() method to all functions in a module.
    
    Parameters:
    -----------
    module : module
        Python module to enhance
    
    Returns:
    --------
    module : module
        Enhanced module with .show() on all functions
    """
    for name in dir(module):
        obj = getattr(module, name)
        
        # Only wrap functions (not classes or private attributes)
        if callable(obj) and not name.startswith('_') and not inspect.isclass(obj):
            try:
                # Wrap with ShowableFunction
                wrapped = ShowableFunction(obj)
                setattr(module, name, wrapped)
            except:
                pass  # Skip if wrapping fails
    
    return module
