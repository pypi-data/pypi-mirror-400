"""
Authentication utilities
"""

import os


def get_api_key() -> str:
    """
    Get API key from environment variable.
    
    Looks for OCULUS_API_KEY in environment.
    """
    api_key = os.getenv("OCULUS_API_KEY")
    
    if not api_key:
        raise ValueError(
            "API key not found. Set OCULUS_API_KEY environment variable:\n"
            "export OCULUS_API_KEY=ok_your_key_here"
        )
    
    return api_key


def authenticate(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid format
    """
    if not api_key:
        return False
        
    # Check format: ok_xxxxx
    if not api_key.startswith("ok_"):
        return False
        
    if len(api_key) < 10:
        return False
        
    return True
