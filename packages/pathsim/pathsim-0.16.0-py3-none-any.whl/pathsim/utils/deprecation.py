#########################################################################################
##
##                              DEPRECATION UTILITIES
##                              (utils/deprecation.py)
##
##           Decorator and utilities for marking deprecated functions and classes
##
#########################################################################################

# IMPORTS ===============================================================================

import warnings
import functools


# DEPRECATION DECORATOR =================================================================

def deprecated(version=None, replacement=None, reason=None):
    """Decorator to mark functions, methods, or classes as deprecated.

    Emits a DeprecationWarning when the decorated item is called/instantiated
    and adds RST-formatted deprecation notice to the docstring.

    Parameters
    ----------
    version : str | None
        Version when the item will be removed (e.g., "1.0.0")
    replacement : str | None
        Name of the replacement to use instead (e.g., "new_function")
    reason : str | None
        Additional explanation for the deprecation

    Returns
    -------
    decorator : callable
        Decorator function

    Example
    -------
    .. code-block:: python

        @deprecated(version="1.0.0", replacement="new_function")
        def old_function():
            pass

        @deprecated(version="2.0.0", reason="No longer needed")
        class OldClass:
            pass
    """

    def decorator(obj):
        # Build warning message
        obj_name = obj.__name__
        if version:
            msg_parts = [f"'{obj_name}' is deprecated and will be removed in version {version}."]
        else:
            msg_parts = [f"'{obj_name}' is deprecated."]

        if replacement:
            msg_parts.append(f"Use '{replacement}' instead.")

        if reason:
            msg_parts.append(reason)

        warning_msg = " ".join(msg_parts)

        # Build RST docstring addition
        rst_parts = [f".. deprecated:: {version}" if version else ".. deprecated::"]
        if replacement:
            rst_parts.append(f"   Use :func:`{replacement}` instead.")
        if reason:
            rst_parts.append(f"   {reason}")
        rst_notice = "\n".join(rst_parts)

        if isinstance(obj, type):
            # Decorating a class
            original_init = obj.__init__

            @functools.wraps(original_init)
            def new_init(self, *args, **kwargs):
                warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
                return original_init(self, *args, **kwargs)

            obj.__init__ = new_init

            # Update class docstring
            obj.__doc__ = _prepend_deprecation_notice(obj.__doc__, rst_notice)

            return obj
        else:
            # Decorating a function or method
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
                return obj(*args, **kwargs)

            # Update function docstring
            wrapper.__doc__ = _prepend_deprecation_notice(obj.__doc__, rst_notice)

            return wrapper

    return decorator


def _prepend_deprecation_notice(docstring, notice):
    """Prepend deprecation notice to docstring.

    Parameters
    ----------
    docstring : str | None
        Original docstring
    notice : str
        RST-formatted deprecation notice

    Returns
    -------
    new_docstring : str
        Docstring with deprecation notice prepended
    """
    if docstring is None:
        return notice + "\n"

    # Find indentation from existing docstring
    lines = docstring.split('\n')
    indent = ""
    for line in lines[1:]:  # Skip first line
        stripped = line.lstrip()
        if stripped:
            indent = line[:len(line) - len(stripped)]
            break

    # Indent the notice to match docstring
    indented_notice = "\n".join(
        indent + line if line.strip() else line
        for line in notice.split('\n')
    )

    # Insert after first line (summary) with blank line
    if len(lines) > 1:
        return lines[0] + "\n\n" + indented_notice + "\n" + "\n".join(lines[1:])
    else:
        return docstring + "\n\n" + indented_notice
