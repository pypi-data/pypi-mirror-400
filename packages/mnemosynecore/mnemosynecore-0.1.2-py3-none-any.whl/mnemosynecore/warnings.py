import warnings

def old_function():
    warnings.warn(
        "old_function устарела, используй new_function",
        DeprecationWarning,
        stacklevel=2
    )