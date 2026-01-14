"""Common utilities for the project.

This module contains shared utility functions that can be used across all nodes.
"""


def example_helper() -> str:
    """An example helper function.
    
    Returns:
        str: A demo message
    """
    return "Helper function called"


def format_output(data: dict) -> str:
    """Format output data as string.
    
    Args:
        data: Dictionary to format
        
    Returns:
        str: Formatted string representation
    """
    return str(data)
