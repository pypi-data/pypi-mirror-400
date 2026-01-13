# -*- encoding: utf-8 -*-

"""
Abstract Base Constructor Definition for Financial Calculations

The abstract base classes are :mod:`pydantic` model which are defined
to provide inline model and field validation. In addition, abstract
methods are provided such that all the methods uses the same attribute
and APIs can be used to switch between different methods without the
need to modify the core attributes.
"""

from typing import Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class FincyAbstractBase(BaseModel, ABC):
    """
    The abstract base class is defined to generalize all the models
    and provide constant attrbutes that is available for all the
    inherited class of the same submodules.

    :type  name: str
    :param name: Name of the model or method that is being currently
        used. This method is simply defined to provide unique names
        for a model and does not have any functional implications.

    :type  currency: str
    :param currency: The calculators are not dependent on the currency
        symbol but is defined for formatting purposes.

    Locale Currency
    ---------------

    The local currency for the region can also be set, but is excluded
    to reduce external module dependency. To fetch the locale currency
    symbol, one can use the following:

    .. code-block:: python

        import locale

        # set the default, using "" for system defaults
        locale.setlocale(locale.LC_ALL, "")

        # get/print the monetary symbol for the locale
        print(locale.localeconv()["currency_symbol"])
        >> "₹" # Locale currency symbol for India

    The currency symbol may alternatively used for string formatting,
    for example thousands seperators, decimals etc. which are mostly
    dependent on the currency.
    """

    name : Optional[str] = Field(
        None, description = "Model/Method Name"
    )

    currency : Optional[str] = Field(
        "₹", description = "Currency Symbol"
    )


    @property
    @abstractmethod
    def premium(self) -> bool:
        """
        The package provides premium models which are delivered to
        endusers as per the pricing policy. The property is defined to
        set the value and alert endusers if there is an alternate
        premium version available which provides more features. Check
        individual model's ``premium`` attribute for more information
        on its usages and features.
        """

        pass


    @abstractmethod
    def calculate(self, *args, **kwargs) -> object:
        """
        Abstarct method that is unified across the module to provide
        one single method class ``.calculate(...)`` which can be used
        by connectors and also provide flexibilty to switch between
        methods of same submodules easily.
        """

        pass
