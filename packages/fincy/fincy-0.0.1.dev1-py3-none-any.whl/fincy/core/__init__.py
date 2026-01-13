# -*- encoding: utf-8 -*-

"""
The module follows object-oriented structure and all the methods are
an instance of one of the base abstract class that follows model and
field validators using :mod:`pydantic` module. Check the ``_base.py``
for more information on the base abstract class.

The core focus is to provide unified, fast, convinent and comprehensive
Python methods to provide calculators for easy financial calculations.
For example, looking for a simple tool to calculate the interest or
the EMI on your home loan? The calculators cover it all. Check the
vast library and methods available.

The calculators are typically classified into two broad categories -
methods to calculate appreciated values typically related to your
investments while depreciation values are for calcuations whose values
depreciates over time - for example a car's value.
"""

from fincy.core.interest import (
    InterestCalculator
)
