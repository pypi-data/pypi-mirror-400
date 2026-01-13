from dataclasses import dataclass, field
from typing import List, Optional

class SandboxPolicyViolationError(PermissionError):
    """Raised when an operation violates the sandbox policy."""
    pass

@dataclass
class SandboxPolicy:
    """Policy for controlling sandbox operations."""
    
    allow_exec: List[str] = field(default_factory=list)
    """List of allowed executables (glob patterns)."""
    
    deny_exec: List[str] = field(default_factory=list)
    """List of denied executables (glob patterns)."""
    
    allow_read: List[str] = field(default_factory=list)
    """List of allowed read paths (glob patterns)."""
    
    deny_read: List[str] = field(default_factory=list)
    """List of denied read paths (glob patterns)."""
    
    allow_write: List[str] = field(default_factory=list)
    """List of allowed write paths (glob patterns)."""
    
    deny_write: List[str] = field(default_factory=list)
    """List of denied write paths (glob patterns)."""

    # Note: Logic to check these will be implemented in the wrapper
    # or helper methods can be added here if complex matching is needed.
    # For now, lets keep it simple data storage as per requirements.
