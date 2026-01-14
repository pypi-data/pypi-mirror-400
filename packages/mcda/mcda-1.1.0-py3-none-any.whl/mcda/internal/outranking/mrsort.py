"""This module implements the MR-Sort algorithm.

Implementation and naming conventions are taken from
:cite:p:`leroy2011mrsort`.
"""
from typing import Any, Dict, List, Union, cast

from deprecated.sphinx import versionadded
from pandas import Series

from ..core.categories import BoundedCategoryProfile
from ..core.interfaces import Assignator, Ranker
from ..core.matrices import PerformanceTable
from ..core.scales import (
    DiscreteQuantitativeScale,
    OrdinalScale,
    QualitativeScale,
)
from ..core.utils import set_module
from ..core.values import CommensurableValues, Values


@set_module("mcda.outranking.mrsort")
@versionadded(version="1.1.0")
class MRSort(Assignator, Ranker):
    """
    This class implements the MR-Sort algorithm.

    :param performance_table:
    :param criteria_weights:
    :param profiles: profiles in ascending dominance order
    :param threshold:
    :param categories: categories in ascending ranking order
    :raise ValueError:
        * if length of `categories` is not length of `profiles` + 1
        * if the profiles are not in ascending dominance order
        * if the profiles and performance table do not share the same scales
    :raise IndexError: if profiles and alternatives share some labels

    :attr category_profiles:
        category profiles formed using `categories` and `profiles`
    :attr categories:
        ordered categories defined as a :class:`mcda.scales.QualitativeScale`
        if `categories` set, a :class:`mcda.scales.DiscreteQuantitativeScale`
        scale otherwise

    .. note::
        Implementation and naming conventions are taken from
        :cite:p:`leroy2011mrsort`.
    """

    def __init__(
        self,
        performance_table: PerformanceTable[OrdinalScale],
        criteria_weights: Dict[Any, float],
        profiles: PerformanceTable[OrdinalScale],
        threshold: float,
        categories: Union[List, None] = None,
    ):
        self.performance_table = performance_table
        self.criteria_weights = criteria_weights
        self.threshold = threshold
        self.categories: Union[DiscreteQuantitativeScale, QualitativeScale]
        if categories is None:
            categories = list(range(len(profiles.alternatives) + 1))
            self.categories = DiscreteQuantitativeScale(categories)
        else:
            self.categories = QualitativeScale(
                Series({c: i for i, c in enumerate(categories)})
            )

        if len(categories) != len(profiles.alternatives) + 1:
            raise ValueError(
                "there must be exactly one more category than profiles"
            )
        common_labels = set(performance_table.alternatives).intersection(
            set(profiles.alternatives)
        )
        if len(common_labels) != 0:
            raise IndexError(
                "profiles and alternatives must have different labels. "
                f"Common labels: {common_labels}"
            )
        if profiles.scales != performance_table.scales:
            raise ValueError(
                "performance table and profiles must share the same scales"
            )
        self.profiles = profiles
        self.category_profiles: Dict[Any, BoundedCategoryProfile] = dict(
            zip(
                categories,
                BoundedCategoryProfile.profiles_partition(self.profiles),
            )
        )

    def assign(
        self,
        **kwargs,
    ) -> CommensurableValues[
        Union[DiscreteQuantitativeScale, QualitativeScale]
    ]:
        """Assign alternatives to categories.

        :return: alternative assignments

        .. note::
            the category profiles defining the categories are the ones from
            :attr:`category_profiles`
        """
        rest = {
            a: av
            for a, av in self.performance_table.alternatives_values.items()
        }
        categories = list(self.category_profiles.keys())
        res = Series({a: categories[0] for a in rest})
        for category, cat_profiles in list(self.category_profiles.items())[1:]:
            remaining = set()
            for alternative, alternative_value in rest.items():
                profile = cast(Values[OrdinalScale], cat_profiles.lower)
                score = sum(
                    [
                        self.criteria_weights[c]
                        if alternative_value[c] >= profile[c]
                        else 0
                        for c in alternative_value
                    ]
                )
                if score >= self.threshold:
                    res[alternative] = category
                    remaining.add(alternative)
            rest = {a: rest[a] for a in remaining}
        return CommensurableValues(res, scale=self.categories)

    def rank(
        self,
        **kwargs,
    ) -> CommensurableValues[
        Union[DiscreteQuantitativeScale, QualitativeScale]
    ]:
        """Rank alternatives by their assigned ordered category.

        :return: alternative assignments

        .. note::
            the category profiles defining the categories are the ones from
            :attr:`category_profiles`

            .. seealso:: :meth:`assign`
        """
        return self.assign()
