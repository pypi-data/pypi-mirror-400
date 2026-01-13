"""
MotionOS SDK - Configuration Decorators

Validation decorators for configuration and method parameters.
"""

from functools import wraps
from typing import Callable, Any, TypeVar, Optional
from motionos.config.validator import (
    validate_api_key,
    validate_project_id,
    is_operation_allowed,
    get_key_type,
    ConfigurationError,
)

F = TypeVar('F', bound=Callable[..., Any])


def validate_config(func: F) -> F:
    """
    Decorator that validates SDK configuration before method execution.
    
    Usage:
        @validate_config
        def some_method(self, ...):
            ...
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        from motionos.config.validator import validate_configuration
        if hasattr(self, '_config'):
            validate_configuration(self._config)
        return func(self, *args, **kwargs)
    return wrapper  # type: ignore


def require_secret_key(func: F) -> F:
    """
    Decorator that requires a secret API key for write operations.
    
    Usage:
        @require_secret_key
        def ingest(self, ...):
            ...
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, '_key_type'):
            key_type = self._key_type
        elif hasattr(self, '_config'):
            key_type = get_key_type(self._config.api_key)
        else:
            raise ConfigurationError("No API key configured", "api_key")
        
        allowed, error = is_operation_allowed("write", key_type)
        if not allowed:
            from motionos.errors.base import ForbiddenError
            raise ForbiddenError(error or "Write operation not allowed with this key type")
        
        return func(self, *args, **kwargs)
    return wrapper  # type: ignore


def require_valid_project(func: F) -> F:
    """
    Decorator that validates project ID before method execution.
    
    Usage:
        @require_valid_project
        def some_method(self, ...):
            ...
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, '_config') and hasattr(self._config, 'project_id'):
            validate_project_id(self._config.project_id)
        return func(self, *args, **kwargs)
    return wrapper  # type: ignore


def validate_input(validator: Callable[[Any], None], param_name: str = "input"):
    """
    Decorator factory that validates a specific parameter.
    
    Usage:
        @validate_input(validate_query, "query")
        def retrieve(self, query: str, ...):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the parameter value
            value = kwargs.get(param_name)
            if value is None and len(args) > 1:
                value = args[1]  # First positional is self
            
            if value is not None:
                validator(value)
            
            return func(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator


def frozen_after_init(cls):
    """
    Class decorator that makes a dataclass instance frozen after __init__.
    
    This allows mutation during initialization but prevents changes afterward.
    
    Usage:
        @frozen_after_init
        @dataclass
        class MyConfig:
            value: str
    """
    original_init = cls.__init__
    
    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        object.__setattr__(self, '_frozen', False)
        original_init(self, *args, **kwargs)
        object.__setattr__(self, '_frozen', True)
    
    def frozen_setattr(self, name, value):
        if getattr(self, '_frozen', False) and name != '_frozen':
            raise AttributeError(f"Cannot modify frozen configuration: {name}")
        object.__setattr__(self, name, value)
    
    cls.__init__ = new_init
    cls.__setattr__ = frozen_setattr
    return cls
