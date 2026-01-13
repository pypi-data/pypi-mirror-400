# -*- encoding: utf-8 -*-

"""
Capture and define internal errors, check class definitions for more
information.
"""

class NotCalculatedError(Exception):
    """
    Error is raised when the result attributes are called without
    calling the ``.calculate()`` method. This exception is defined to
    standardize models and connectors for forward integrations.
    """

    def __init__(self, field : str) -> None:
        message = (
            f"Cannot access Attribute '{field}' as the `.calculate() "
            "method was not called; first populate the result fields."
        )

        return super().__init__(message)
