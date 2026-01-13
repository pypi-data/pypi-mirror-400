# -*- encoding: utf-8 -*-

"""
A simple Python tool for calculating financial metrics. This tool can
be used both as a standalone application and for forward integration
with external modules via connectors. The core functionality is built
using native Python libraries, with standard constructor classes
implemented using the :mod:`abc` module. Additionally, the
:mod:`pydantic` library is utilized for model and field validation to
ensure data integrity.

This tool is suitable for financial analysis, reporting, and further
development in a modular, flexible environment.
"""

import os

# ? package follows https://peps.python.org/pep-0440/
# ? check contributing guidelines for more information
__version__ = open(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "VERSION"
), "r").read()

# init-time Option Registrations
