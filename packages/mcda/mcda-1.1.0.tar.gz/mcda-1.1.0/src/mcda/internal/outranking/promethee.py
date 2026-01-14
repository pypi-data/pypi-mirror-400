"""This module implements Promethee algorithms in a heavily modular way.

.. todo:: Implement commented-out classes
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Union, cast, overload

import matplotlib.pyplot as plt
from pandas import DataFrame, Series
from sklearn.decomposition import PCA

from ..core.aggregators import Aggregator, NormalizedWeightedSum
from ..core.aliases import NumericFunction
from ..core.compatibility import dataframe_map
from ..core.interfaces import Ranker
from ..core.matrices import (
    AdjacencyValueMatrix,
    PartialValueMatrix,
    PerformanceTable,
)
from ..core.relations import (
    IncomparableRelation,
    IndifferenceRelation,
    PreferenceRelation,
    PreferenceStructure,
    Relation,
)
from ..core.scales import PreferenceDirection, QuantitativeScale
from ..core.utils import set_module
from ..core.values import CommensurableValues, Values


@set_module("mcda.functions")
class UShapeFunction:
    """This class implements the u-shape preference function.

    :param q: the indifference threshold
    """

    def __init__(self, p: float = 0):
        self.p = p

    def __call__(self, x: float) -> float:
        """Return preference degree on a criterion of two alternatives.

        :param x: criteria values difference
        :return:
        """
        return 1 if x > self.p else 0


@set_module("mcda.functions")
class VShapeFunction:
    """This class implements the linear level preference function.

    :param p: preference threshold
    :param q: indifference threshold
    """

    def __init__(self, p: float, q: float = 0):
        if q > p:
            raise ValueError("'q' cannot be bigger than 'p'")
        self.p = p
        self.q = q

    def __call__(self, x: float) -> float:
        """Return preference degree on a criterion of two alternatives.

        :param x: criteria values difference
        :return:
        """
        return (
            1
            if x > self.p
            else (abs(x) - self.q) / (self.p - self.q)
            if x > self.q
            else 0
        )


@set_module("mcda.functions")
class LevelFunction:
    """This class implements the level preference function.

    :param p: preference threshold
    :param q: indifference threshold
    """

    def __init__(self, p: float, q: float):
        if q > p:
            raise ValueError("'q' cannot be bigger than 'p'")
        self.p = p
        self.q = q

    def __call__(self, x: float) -> float:
        """Return preference degree on a criterion of two alternatives.

        :param x: criteria values difference
        :return:
        """
        return 1 if x > self.p else 0.5 if x > self.q else 0


@set_module("mcda.functions")
class GaussianFunction:
    """This class implements the gaussian preference function.

    :param s: standard deviation
    """

    def __init__(self, s: float):
        self.s = s

    def __call__(self, x: float) -> float:
        """Return preference degree on a criterion of two alternatives.

        :param x: criteria values difference
        :return:
        """
        return 1 - math.exp(-(x**2) / (2 * self.s**2)) if x > 0 else 0


class GeneralizedCriterion:
    """This class defines a generalized criterion which is used to compare
    alternatives according to a criterion.

    Implementations naming conventions are taken from
    :cite:p:`figueira2005mcda`.

    :param preference_function:
        function applied on alternative values difference
    :param scale: input scale (inferred from input if not provided)

    .. note::
        Alternatives values comparisons are transformed so that a positive
        difference implies the first alternative is preferred.
        :attr:`preference_function` is then applied on this difference.
    .. warning::
        :attr:`scale` is only declarative, and not use
        for checking/transforming data.
    """

    def __init__(
        self,
        preference_function: NumericFunction,
        scale: Union[QuantitativeScale, None] = None,
    ):
        self.preference_function = preference_function
        self.scale = scale

    def within_scale(
        self,
        data: Union[float, Series, CommensurableValues[QuantitativeScale]],
    ) -> bool:
        """Check potential input is inside input scale.

        :param data:
        :return: ``True`` if `data` is within :attr:`scale`
        """
        if isinstance(data, Series):
            v = CommensurableValues(data, scale=self.scale)
            return v.is_within_scales
        if isinstance(data, CommensurableValues):
            v = CommensurableValues(data.data, scale=self.scale)
            return v.is_within_scales
        return data in self.scale if self.scale else True

    def _apply_pair(
        self,
        alternative_value1: float,
        alternative_value2: float,
        preference_direction: Union[PreferenceDirection, None] = None,
    ) -> float:
        """Apply generalized criterion to compare both alternative values.

        :param alternative_value1:
        :param alternative_value2:
        :param preference_direction:
        :return: how much `x` is preferred to `y`
        """
        return self.preference_function(
            alternative_value2 - alternative_value1
            if preference_direction == PreferenceDirection.MIN
            else alternative_value1 - alternative_value2
        )

    def _apply_series(
        self,
        series: Series,
        preference_direction: Union[PreferenceDirection, None] = None,
    ) -> DataFrame:
        """Apply generalized criterion to each pair of criterion values.

        :param series: criterion values
        :param preference_direction:
        :return:
            dataframe showing criterion preference over any pair of alternative
        """
        return cast(
            DataFrame,
            series.apply(
                lambda x: series.apply(
                    lambda y, xx=x: self._apply_pair(
                        xx, y, preference_direction
                    )
                )
            ),
        )

    def _apply_values(
        self, criterion_values: CommensurableValues[QuantitativeScale]
    ) -> AdjacencyValueMatrix[QuantitativeScale]:
        """Apply generalized criterion to each pair of criterion values.

        :param criterion_values:
        :return:
            matrix showing criterion preference over any pair of alternative
        """
        return AdjacencyValueMatrix(
            self._apply_series(
                criterion_values.data,
                criterion_values.scale.preference_direction,
            ),
            stype=QuantitativeScale,
        )

    @overload
    def __call__(
        self,
        x: float,
        y: float,
        /,
        *,
        preference_direction: Union[PreferenceDirection, None] = None,
    ) -> float:  # pragma: nocover
        ...

    @overload
    def __call__(
        self,
        x: Series,
        /,
        *,
        preference_direction: Union[PreferenceDirection, None] = None,
    ) -> DataFrame:  # pragma: nocover
        ...

    @overload
    def __call__(
        self,
        x: CommensurableValues[QuantitativeScale],
        /,
    ) -> AdjacencyValueMatrix[QuantitativeScale]:  # pragma: nocover
        ...

    def __call__(
        self,
        x: Union[float, Series, CommensurableValues[QuantitativeScale]],
        y: Union[float, None] = None,
        /,
        *,
        preference_direction: Union[PreferenceDirection, None] = None,
    ) -> Union[float, DataFrame, AdjacencyValueMatrix[QuantitativeScale]]:
        """Apply generalized criterion to inputs.

        :param x: first input
        :param y: second input (only if comparing two criterion values)
        :param preference_direction:
        :raises TypeError:
            if arguments don't match one of the implemented `apply_` method
        :return: result
        """
        if isinstance(x, Series):
            return self._apply_series(x, preference_direction)
        if isinstance(x, CommensurableValues):
            return self._apply_values(x)
        if y is not None:
            return self._apply_pair(cast(float, x), y, preference_direction)
        raise TypeError("not supported arguments")


class GeneralizedCriteria:
    """This class defines generalized criteria.

    :param generalized_criterions:
    """

    def __init__(
        self, generalized_criterions: Mapping[Any, GeneralizedCriterion]
    ):
        self.generalized_criterions = generalized_criterions
        self.scales: Mapping[Any, QuantitativeScale] = {
            criterion: f.scale
            for criterion, f in self.generalized_criterions.items()
            if f.scale
        }

    def within_in_scales(
        self,
        data: Union[
            Series,
            Values[QuantitativeScale],
            DataFrame,
            PerformanceTable[QuantitativeScale],
        ],
    ) -> bool:
        """Check potential input is inside input scales.

        :param data:
        :return: ``True`` if `data` is within :attr:`scales`
        """
        if isinstance(data, Series):
            v = Values(data, scales=self.scales)
            return v.is_within_scales
        if isinstance(data, Values):
            v = Values(data.data, scales=self.scales)
            return v.is_within_scales
        if isinstance(data, DataFrame):
            m = PerformanceTable(data, scales=self.scales)
            return m.is_within_scales
        m = PerformanceTable(data.data, scales=self.scales)
        return m.is_within_scales

    def _apply_series_pair(
        self,
        series1: Series,
        series2: Series,
        preference_directions: Union[
            Mapping[Any, Union[PreferenceDirection, None]], None
        ] = None,
    ) -> Series:
        """Return partial preferences between alternative values pair.

        :param series1:
        :param series2:
        :param preference_directions:
        :return:
        """
        _preference_directions: Mapping[
            Any, Union[PreferenceDirection, None]
        ] = ({} if preference_directions is None else preference_directions)
        return Series(
            {
                criterion: g(
                    series1[criterion],
                    series2[criterion],
                    preference_direction=_preference_directions.get(criterion),
                )
                for criterion, g in self.generalized_criterions.items()
            }
        )

    def _apply_values_pair(
        self,
        alternative_values1: Values[QuantitativeScale],
        alternative_values2: Values[QuantitativeScale],
    ) -> Values[QuantitativeScale]:
        """Return partial preferences between alternative values pair.

        :param alternative_values1:
        :param alternative_values2:
        :return:
        """
        preference_directions: Mapping[
            Any, Union[PreferenceDirection, None]
        ] = {
            criterion: alternative_values1.scales[
                criterion
            ].preference_direction
            for criterion in alternative_values1.labels
        }
        return Values(
            self._apply_series_pair(
                alternative_values1.data,
                alternative_values2.data,
                preference_directions,
            ),
            stype=QuantitativeScale,
        )

    def _apply_dataframe(
        self,
        df: DataFrame,
        preference_directions: Union[
            Mapping[Any, Union[PreferenceDirection, None]], None
        ] = None,
    ) -> DataFrame:
        """Return partial preferences between each alternative values pair.

        :param df:
        :param preference_directions:
        :return:
        """
        return DataFrame(
            [
                [
                    self._apply_series_pair(
                        df.loc[i], df.loc[j], preference_directions
                    )
                    for j in df.index.tolist()
                ]
                for i in df.index.tolist()
            ],
            index=df.index.tolist(),
            columns=df.index.tolist(),
        )

    def _apply_performance_table(
        self, performance_table: PerformanceTable[QuantitativeScale]
    ) -> PartialValueMatrix[QuantitativeScale]:
        """Return partial preferences between each alternative values pair.

        :param performance_table:
        :return:
        """
        preference_directions: Mapping[
            Any, Union[PreferenceDirection, None]
        ] = {
            criterion: performance_table.scales[criterion].preference_direction
            for criterion in performance_table.criteria
        }
        return PartialValueMatrix(
            self._apply_dataframe(
                performance_table.data, preference_directions
            ),
            stype=QuantitativeScale,
        )

    @overload
    def __call__(
        self,
        x: Series,
        y: Series,
        /,
        *,
        preference_directions: Union[
            Mapping[Any, Union[PreferenceDirection, None]], None
        ] = None,
    ) -> Series:  # pragma: nocover
        ...

    @overload
    def __call__(
        self,
        x: DataFrame,
        /,
        *,
        preference_directions: Union[
            Mapping[Any, Union[PreferenceDirection, None]], None
        ] = None,
    ) -> DataFrame:  # pragma: nocover
        ...

    @overload
    def __call__(
        self,
        x: Values[QuantitativeScale],
        y: Values[QuantitativeScale],
        /,
    ) -> Values[QuantitativeScale]:  # pragma: nocover
        ...

    @overload
    def __call__(
        self,
        x: PerformanceTable[QuantitativeScale],
        /,
    ) -> PartialValueMatrix[QuantitativeScale]:  # pragma: nocover
        ...

    def __call__(
        self,
        x: Union[
            Series,
            Values[QuantitativeScale],
            DataFrame,
            PerformanceTable[QuantitativeScale],
        ],
        y: Union[Series, Values[QuantitativeScale], None] = None,
        /,
        *,
        preference_directions: Union[
            Mapping[Any, Union[PreferenceDirection, None]], None
        ] = None,
    ) -> Union[
        Series,
        Values[QuantitativeScale],
        DataFrame,
        PartialValueMatrix[QuantitativeScale],
    ]:
        """Apply generalized criteria to inputs.

        :param x: first input
        :param y:
            second input (only if comparing one pair of alternative values)
        :param preference_directions:
        :raises TypeError:
            if arguments don't match one of the implemented `apply_` method
        :return: result
        """
        if isinstance(x, DataFrame):
            return self._apply_dataframe(x, preference_directions)
        if isinstance(x, PerformanceTable):
            return self._apply_performance_table(x)
        if isinstance(x, Series) and isinstance(y, Series):
            return self._apply_series_pair(x, y, preference_directions)
        if isinstance(x, Values) and isinstance(y, Values):
            return self._apply_values_pair(x, y)
        raise TypeError("not supported arguments")


"""
class ReinforcedPreference(GeneralizedCriteriaWeightedSum):
    def __init__(
        self,
        criteria_weights: Dict[Any, float],
        preference_thresholds: Dict[Any, float],
        indifference_thresholds: Dict[Any, float],
        reinforced_factors: Dict[Any, float],
        **kwargs,
    ):
        super().__init__(criteria_weights, **kwargs)
        self.preference_thresholds = preference_thresholds
        self.indifference_thresholds = indifference_thresholds
        self.reinforced_factors = reinforced_factors

    def _pairwise_preference(
        self,
        partial_preferences: Series,
    ) -> float:
        # weights = Series(self.criteria_weights)
        pass


class CriteriaPreferenceInteraction(ABC):
    @abstractmethod
    def __call__(
        self, preference1: float, preference2: float
    ) -> float:  # pragma: nocover
        pass


class MutualStrengtheningInteraction(CriteriaPreferenceInteraction):
    pass


class MutualWeakeningInteraction(CriteriaPreferenceInteraction):
    pass


class MutualAntagonisticInteraction(CriteriaPreferenceInteraction):
    pass


class GeneralizedCriteriaInteractions(GeneralizedCriteriaAggregator):
    def __init__(self, interaction_matrix: DataFrame):
        self.interaction_matrix = interaction_matrix


class Discordance(GeneralizedCriteriaAggregator):
    def _pairwise_preference(self, partial_preferences: Series) -> float:
        return 1 - self.pairwise_discordance(partial_preferences)

    def pairwise_discordance(self, partial_preferences: Series) -> float:
        pass

    def discordance_from_partial(
        self, partial_preferences: AdjacencyMatrix
    ) -> AdjacencyMatrix:
        data = partial_preferences.data.map(self.pairwise_discordance)
        return partial_preferences.__class__(data)


class Veto(GeneralizedCriteriaAggregator):
    def __init__(
        self,
        veto_thresholds: Dict[Any, float],
        **kwargs,
    ):
        self.veto_thresholds = veto_thresholds
        super().__init__(**kwargs)

    def _pairwise_preference(self, partial_preferences: Series) -> float:
        return 1 - self.pairwise_veto(partial_preferences)

    def pairwise_veto(self, partial_preferences: Series) -> float:
        pass

    def veto_from_partial(
        self, partial_preferences: AdjacencyMatrix
    ) -> AdjacencyMatrix:
        data = partial_preferences.data.map(self.pairwise_veto)
        return partial_preferences.__class__(data)


class StrongVeto(Veto):
    def pairwise_veto(self, partial_preferences: Series) -> float:
        pass


class ChainCriteriaAggregator(GeneralizedCriteriaAggregator):
    def __init__(
        self,
        *aggregators: GeneralizedCriteriaAggregator,
        **kwargs,
    ):
        self.aggregators = [*aggregators]
        super().__init__(**kwargs)

    def _pairwise_preference(self, partial_preferences: Series) -> float:
        res = 1.0
        for agg in self.aggregators:
            res *= agg._pairwise_preference(partial_preferences)
        return res

    def preferences(
        self, partial_preferences: AdjacencyMatrix
    ) -> AdjacencyMatrix:
        res = partial_preferences.__class__(
            1,
            vertices=partial_preferences.vertices,
        )
        for agg in self.aggregators:
            res *= agg.preferences(partial_preferences)
        return res
"""


def positive_flows(
    preferences: AdjacencyValueMatrix[QuantitativeScale],
    profiles: Union[List, None] = None,
) -> Series:
    """Compute positive flows.

    :param preferences:
    :param profiles:
    :return: computed positive flows

    .. note::
        if `profiles` is not ``None``, it will returns alternatives
        vs profiles positive flows
    """
    if profiles is None:
        data = preferences.data
    else:
        alternatives = sorted(
            set(preferences.vertices) - set(profiles),
            key=lambda a: preferences.vertices.index(a),
        )
        data = preferences.data.loc[alternatives, profiles]
    return data.sum(axis=1)


def negative_flows(
    preferences: AdjacencyValueMatrix[QuantitativeScale],
    profiles: Union[List, None] = None,
) -> Series:
    """Compute negative flows.

    :param preferences:
    :param profiles:
    :return: computed negative flows

    .. note::
        if `profiles` is not ``None``, it will returns profiles
        vs alternatives negative flows
    """
    if profiles is None:
        data = preferences.data
    else:
        alternatives = sorted(
            set(preferences.vertices) - set(profiles),
            key=lambda a: preferences.vertices.index(a),
        )
        data = preferences.data.loc[profiles, alternatives]
    return data.sum(axis=0)


def net_outranking_flows(
    preferences: AdjacencyValueMatrix[QuantitativeScale],
) -> Series:
    """Compute net outranking flows.

    :param preferences:
    :return: net outranking flows
    """
    return positive_flows(preferences) - negative_flows(preferences)


"""
class NetFlowAggregatorType(Enum):
    MAX = np.nanmax
    MIN = np.nanmin
    SUM = np.nansum

    def __call__(self, preferences: AdjacencyMatrix) -> Series:
        values = preferences.data.values
        np.fill_diagonal(values, np.NaN)
        return Series(self.value(values), index=preferences.vertices)


class NetFlowScore(Flows, ABC):
    def __init__(
        self,
        aggregation_type: NetFlowAggregatorType,
        **kwargs,
    ):
        self.aggregation_type = aggregation_type

    @abstractmethod
    def _aggregate(
        self, preferences: AdjacencyMatrix
    ) -> Series:  # pragma: nocover
        pass

    def flows(
        self, preferences: AdjacencyMatrix, total_order: bool = False, **kwargs
    ) -> Series:
        res = self._aggregate(preferences)
        if not total_order:
            return res
        duplicates = res.duplicated(keep=False)
        if len(duplicates) > 0:
            res[duplicates] = self.flows(
                preferences.loc[duplicates, duplicates]
            )
        return res


class NetFlowScoreFavor(NetFlowScore):
    def _aggregate(self, preferences: AdjacencyMatrix) -> Series:
        return self.aggregation_type(preferences)


class NetFlowScoreAgainst(NetFlowScore):
    def _aggregate(self, preferences: AdjacencyMatrix) -> Series:
        return -self.aggregation_type(preferences)


class NetFlowScoreDifference(NetFlowScore):
    def _aggregate(self, preferences: AdjacencyMatrix) -> Series:
        return self.aggregation_type(preferences - preferences.data.T)
"""


def criteria_flows(
    partial_preferences: PartialValueMatrix[QuantitativeScale],
) -> DataFrame:
    """Returns the criteria flows.

    :param partial_preferences:
    :return:
    """
    res = DataFrame(
        0,
        index=partial_preferences.vertices,
        columns=cast(
            Series, partial_preferences.data.iloc[0, 0]
        ).index.tolist(),
        dtype=float,
    )
    criteria_preferences = {
        c: dataframe_map(partial_preferences.data, lambda s, crit=c: s[crit])
        for c in res.columns
    }
    for a in res.index:
        for c, crit_prefs in criteria_preferences.items():
            res.loc[a, c] = (crit_prefs.loc[a] - crit_prefs[a]).mean()
    return res


class Promethee(ABC):
    """This class describes the common interface for all Promethee algorithms.

    :param performance_table:
    :param preference_functions:
    :param generalized_criteria_aggregator:
    :raise TypeError: if `performance_table` is not ordinal
    """

    def __init__(
        self,
        performance_table: PerformanceTable[QuantitativeScale],
        preference_functions: Mapping[Any, NumericFunction],
        generalized_criteria_aggregator: Aggregator[
            QuantitativeScale, QuantitativeScale
        ],
    ):
        self.performance_table = performance_table
        self.generalized_criteria = GeneralizedCriteria(
            {
                criterion: GeneralizedCriterion(
                    preference_functions[criterion],
                    cast(
                        QuantitativeScale, performance_table.scales[criterion]
                    ),
                )
                for criterion in performance_table.criteria
            }
        )
        self.generalized_criteria_aggregator = generalized_criteria_aggregator

    def partial_preferences(self) -> PartialValueMatrix[QuantitativeScale]:
        """Compute partial preferences for each alternatives' pair.

        :param performance_table:
        :return: partial preferences
        """
        return self.generalized_criteria(self.performance_table)

    def preferences(
        self, partial_preferences: PartialValueMatrix[QuantitativeScale]
    ) -> AdjacencyValueMatrix[QuantitativeScale]:
        """Compute preferences for each alternatives' pair from partial
        preferences.

        :param partial_preferences:
        :return: preferences
        """
        return AdjacencyValueMatrix(
            dataframe_map(
                partial_preferences.data, self.generalized_criteria_aggregator
            ),
            scale=self.generalized_criteria_aggregator.out_scale,
            stype=self.generalized_criteria_aggregator.out_stype,
        )

    @abstractmethod
    def flows(
        self, preferences: AdjacencyValueMatrix[QuantitativeScale], **kwargs
    ) -> Series:  # pragma: nocover
        """Compute flows.

        :param preferences:
        :return: flows
        """
        pass


@set_module("mcda.outranking.promethee")
class Promethee1(
    Promethee,
    Ranker,
):
    """This class implements Promethee I.

    Implementation and notations are based on :cite:p:`vincke1998promethee1`.

    :param performance_table:
    :param criteria_weights:
    :param preference_functions:
    :raise TypeError: if `performance_table` is not ordinal
    """

    def __init__(
        self,
        performance_table: PerformanceTable[QuantitativeScale],
        criteria_weights: Dict[Any, float],
        preference_functions: Mapping[Any, NumericFunction],
    ):
        super().__init__(
            performance_table=performance_table,
            preference_functions=preference_functions,
            generalized_criteria_aggregator=NormalizedWeightedSum(
                criteria_weights,
                cast(
                    Mapping[Any, QuantitativeScale], performance_table.scales
                ),
            ),
        )

    def flows(
        self,
        preferences: AdjacencyValueMatrix[QuantitativeScale],
        negative: bool = False,
        **kwargs,
    ) -> Series:
        """Compute outranking flows (positive or negative).

        :param preferences:
        :param negative:
            computes negative flows if ``True``, positive flows otherwise
        :return: outranking flows
        """
        return (
            negative_flows(preferences)
            if negative
            else positive_flows(preferences)
        )

    @staticmethod
    def _flow_intersection(
        a: Any,
        b: Any,
        pos_flow_a: float,
        pos_flow_b: float,
        neg_flow_a: float,
        neg_flow_b: float,
    ) -> Relation:
        """Compute the positive and negative flow intersection.

        :param a: first alternative
        :param b: second alternative
        :param pos_flow_a: the positive flow of first alternative
        :param pos_flow_b: the positive flow of second alternative
        :param neg_flow_a: the negative flow of first alternative
        :param neg_flow_b: the negative flow of second alternative
        :return: the comparison of the two alternatives in a relation
        """

        if pos_flow_a == pos_flow_b and neg_flow_a == neg_flow_b:
            return IndifferenceRelation(a, b)
        if pos_flow_a >= pos_flow_b and neg_flow_a <= neg_flow_b:
            return PreferenceRelation(a, b)
        if pos_flow_b >= pos_flow_a and neg_flow_b <= neg_flow_a:
            return PreferenceRelation(b, a)
        return IncomparableRelation(a, b)

    def rank(self, **kwargs) -> PreferenceStructure:
        """Apply Promethee I algorithm.

        :return: result as a preference structure
        """
        partial_preferences = self.partial_preferences()
        preferences = self.preferences(partial_preferences)
        pos_flow = self.flows(preferences)
        neg_flow = self.flows(preferences, negative=True)

        res = PreferenceStructure()
        for i, a in enumerate(self.performance_table.alternatives):
            for b in self.performance_table.alternatives[(i + 1) :]:
                res += self._flow_intersection(
                    a, b, pos_flow[a], pos_flow[b], neg_flow[a], neg_flow[b]
                )
        return res


@set_module("mcda.outranking.promethee")
class Promethee2(
    Promethee,
    Ranker,
):
    """This class implements Promethee II.

    Implementation and notations are based on :cite:p:`vincke1998promethee1`.

    :param performance_table:
    :param criteria_weights:
    :param preference_functions:
    :raise TypeError: if `performance_table` is not ordinal
    """

    def __init__(
        self,
        performance_table: PerformanceTable[QuantitativeScale],
        criteria_weights: Dict[Any, float],
        preference_functions: Mapping[Any, NumericFunction],
    ):
        super().__init__(
            performance_table=performance_table,
            preference_functions=preference_functions,
            generalized_criteria_aggregator=NormalizedWeightedSum(
                criteria_weights,
                cast(
                    Mapping[Any, QuantitativeScale], performance_table.scales
                ),
            ),
        )

    def flows(
        self, preferences: AdjacencyValueMatrix[QuantitativeScale], **kwargs
    ) -> Series:
        """Computes net outranking flows.

        :param preferences:
        :return: net outranking flows
        """
        return net_outranking_flows(preferences)

    def rank(self, **kwargs) -> CommensurableValues[QuantitativeScale]:
        """Apply Promethee II algorithm.

        :return: result as scores
        """
        partial_preferences = self.partial_preferences()
        preferences = self.preferences(partial_preferences)
        return CommensurableValues(
            self.flows(preferences), stype=QuantitativeScale
        )


@set_module("mcda.outranking.promethee")
class PrometheeGaia(Promethee2):
    """This class is used to represent and draw a Promethee GAIA plane.

    Implementations naming conventions are taken from
    :cite:p:`figueira2005mcda`

    :param performance_table:
    :param criteria_weights:
    :param preference_functions:
    :raise TypeError: if `performance_table` is not ordinal
    """

    def unicriterion_net_flows_matrix(self) -> DataFrame:
        """Computes the whole matrix of single criterion net flows.

        Each cell corresponds to the single criterion net flow of an
        alternative considering only one criterion.

        :param performance_table:
        :return: unicriterion net flows matrix
        """
        return criteria_flows(self.partial_preferences())

    def plot(self):  # pragma: nocover
        """Plots the GAIA plane and displays in the top-left corner
        the ratio of saved information by the PCA, delta.

        :param performance_table:
        """
        net_flows = self.unicriterion_net_flows_matrix()

        pca = PCA(n_components=2)
        pca.fit(net_flows)
        delta = (
            pca.explained_variance_ratio_[0] + pca.explained_variance_ratio_[1]
        )
        alternative_vectors = pca.transform(net_flows)
        criterions = DataFrame(
            [
                [
                    1 if i == j else 0
                    for j in range(len(self.performance_table.criteria))
                ]
                for i in range(len(self.performance_table.criteria))
            ],
            index=self.performance_table.criteria,
            columns=self.performance_table.criteria,
        )
        criterion_vectors = pca.transform(criterions)
        pi = [
            self.generalized_criteria_aggregator(
                Series(criterion_vectors[:, i])
            )
            for i in range(2)
        ]

        plt.figure(figsize=[10, 10])

        for i, alternative in enumerate(self.performance_table.alternatives):
            plt.scatter(
                alternative_vectors[i][0],
                alternative_vectors[i][1],
                s=100,
                label=alternative,
            )
        for j, criterion in enumerate(self.performance_table.criteria):
            plt.text(
                criterion_vectors[j][0],
                criterion_vectors[j][1],
                criterion,
                ha="center",
            )
            plt.arrow(
                0,
                0,
                criterion_vectors[j][0],
                criterion_vectors[j][1],
            )

        plt.arrow(0, 0, pi[0], pi[1])
        plt.scatter(pi[0], pi[1], s=150, marker="*", label=r"$\pi$")

        ax = plt.gca()
        xmin, _ = ax.get_xlim()
        _, ymax = ax.get_ylim()

        plt.text(
            xmin, ymax, r"$\delta$ = %.3f" % delta, bbox=dict(boxstyle="round")
        )

        plt.legend()
        plt.plot()
        plt.show()
