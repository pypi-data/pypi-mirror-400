from __future__ import annotations

from typing import Any, List, Union, cast

from .matrices import PerformanceTable
from .scales import OrdinalScale
from .utils import set_module
from .values import Values


@set_module("mcda.categories")
class BoundedCategoryProfile:
    """This class represents a category defined by profiles as its limits.

    :param lower: lower profile
    :param upper: upper profile

    :raise ValueError: if `upper` doesn't dominate `lower`
    """

    def __init__(
        self,
        lower: Union[Values[OrdinalScale], None] = None,
        upper: Union[Values[OrdinalScale], None] = None,
    ):
        if upper and lower and not upper.dominate(lower):
            raise ValueError("upper must dominate lower profile")
        self.lower = lower
        self.upper = upper

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        :param other:
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        _other = cast(BoundedCategoryProfile, other)
        return self.lower == _other.lower and self.upper == _other.upper

    @classmethod
    def profiles_partition(
        cls,
        profiles: PerformanceTable[OrdinalScale],
        lowest: bool = True,
        upmost: bool = True,
    ) -> List[BoundedCategoryProfile]:
        """Build a list of bounded category profiles.

        :param profiles:
        :param lowest:
            if ``True`` add a category profile with last profile as its upper
            bound (and no lower bound)
        :param upmost:
            if ``True`` add a category profile with first profile as its lower
            bound (and no upper bound)
        :raises ValueError: if any profile doesn't dominate its predecessor
        :return:
            list of bounded category profiles in ascending domination order
        """
        values = list(profiles.alternatives_values.values())
        try:
            res = [
                cls(p1, p2)
                for p1, p2 in zip(
                    values[:-1],
                    values[1:],
                )
            ]
            if upmost:
                res = [cls(upper=values[0])] + res
            if lowest:
                res += [cls(lower=values[-1])]
            return res
        except ValueError:
            raise ValueError("any profile must dominate its predecessor")


@set_module("mcda.categories")
class CentralCategoryProfile:
    """This class represents a category defined by a central profile.

    :param center:
    """

    def __init__(self, center: Values[OrdinalScale]):
        self.center = center

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        :param other:
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        _other = cast(CentralCategoryProfile, other)
        return self.center == _other.center
