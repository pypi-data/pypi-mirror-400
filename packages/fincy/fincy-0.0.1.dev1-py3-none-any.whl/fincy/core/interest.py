# -*- encoding: utf-8 -*-

"""
In finance, appreciation is the term used to refer to the increase in
the asset's value over time and is the most sought after value. The
module provides methods to calculate values that appreciate over time
for example returns from investments.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator

from fincy.core.base import FincyAbstractBase


class InterestCalculator(FincyAbstractBase):
    """
    An interest is the monetary charge for borrowing money or the
    compensation received for lending or depositing money from/to a
    financial institution or service providers.
    """

    principal : float = Field(
        ..., description = "Principal Amount (in the currency unit)"
    )

    rate : float = Field(
        ..., description = "Interest Rate (in %)", gt = 0.0
    )

    time : float = Field(
        ..., description = "Investment Time (in years)"
    )

    method : Optional[Literal["simple", "compound"]] = Field(
        None, description = "Compunding Frequency for Interest"
    )

    frequency : Optional[Literal[
        "daily", "weekly", "quarterly", "yearly"
    ]] = Field(
        "simple", description = "Interest Calculation Method"
    )

    # set the default model name, this is extended attribute
    name : Optional[str] = Field(
        "Interest Calculator", description = "Model/Method Name"
    )

    @property
    def premium(self) -> bool:
        """
        A premium version is not available for an interest calculator
        and all the functionalities are available under the open source
        license aggrement, check module's LICENSE file which was
        shipped with the module for more information.
        """

        return False


    def calculate(self) -> float:
        """
        Calculate the interest and final payable amount based on the
        type of interest calculation method.

        :rtype: float
        :returns: Final payable amount over the lended/borrowed
            period. The result attributes are also populated on the
            function call which provides more informaton.
        """

        return self.principal * (1 + self.rate * self.time)
