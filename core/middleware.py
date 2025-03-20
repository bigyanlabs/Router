from flask import request, redirect, session
from typing import Optional, List, Dict, Callable, Any
from functools import wraps
import re

PROTECTED_ROUTES: List[str] = []

PROTECTED_PATTERNS: List[str] = [
    r"^/user/[^/]+/edit$",  
]

def auth_required(f: Callable) -> Callable:
    """Decorator for routes that require authentication."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        path = request.path
        
        is_protected = any(path.startswith(route) for route in PROTECTED_ROUTES)
        
        if not is_protected:
            is_protected = any(re.match(pattern, path) for pattern in PROTECTED_PATTERNS)
            
        if is_protected:
            user: Optional[str] = session.get("user")
            if not user:
                return redirect("/login")
                
        return f(*args, **kwargs)
    return decorated_function

def auth_middleware(route: str) -> bool:
    """Checks if a route is protected without accessing session."""
    is_protected = any(route.startswith(protected) for protected in PROTECTED_ROUTES)
    if not is_protected:
        is_protected = any(re.match(pattern, route) for pattern in PROTECTED_PATTERNS)
    return is_protected