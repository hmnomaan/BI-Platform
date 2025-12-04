"""
Compatibility shim for pkgutil.find_loader in Python 3.12+
This fixes the issue where some dependencies still use the deprecated pkgutil.find_loader
"""
import sys
import pkgutil

# Python 3.12+ removed pkgutil.find_loader, so we provide a compatibility shim
if sys.version_info >= (3, 12):
    if not hasattr(pkgutil, 'find_loader'):
        def find_loader(fullname):
            """Compatibility shim for pkgutil.find_loader removed in Python 3.12+"""
            try:
                # Try to find the loader using the new API
                spec = pkgutil.resolve_name(fullname) if hasattr(pkgutil, 'resolve_name') else None
                if spec is not None and spec.loader is not None:
                    return spec.loader
                
                # Fallback: try to import and get the loader
                try:
                    module = __import__(fullname, fromlist=[''])
                    if hasattr(module, '__loader__'):
                        return module.__loader__
                except (ImportError, AttributeError):
                    pass
                
                # Return None if not found (matching old behavior)
                return None
            except Exception:
                return None
        
        # Add the compatibility function to pkgutil
        pkgutil.find_loader = find_loader

