from __future__ import annotations

import sys
from abc import ABC
from typing import Any, Dict, Iterator, List, Mapping, Tuple, Type, Union

from numpy import fill_diagonal
from pandas import DataFrame, Series

from .matrices import (
    OutrankingMatrix,
    create_outranking_matrix,
    requires_graphviz,
)
from .scales import PreferenceDirection, QuantitativeScale
from .utils import set_module
from .values import CommensurableValues, Ranking

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:
    from typing_extensions import Self


try:
    from graphviz import Digraph
except ImportError:  # pragma: nocover
    import warnings

    warnings.warn(
        "Graph plotting features not available. "
        "If you need those, please install 'graphviz' or this package "
        "optional plotting dependencies 'mcda[plot]'."
    )


@set_module("mcda.types")
class Relation(ABC):
    """This class represents a pairwise relation between two elements.

    :param a: first element
    :param b: second element

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances
    """

    _RELATION_TYPE = ""
    DRAW_STYLE: Dict[str, Any] = {"style": "invis"}

    def __init__(self, a: Any, b: Any):
        self.a = a
        self.b = b
        self._validate()

    def __str__(self) -> str:
        """Return string representation of object.

        :return:
        """
        return f"{self.a} {self._RELATION_TYPE} {self.b}"

    def __repr__(self) -> str:  # pragma: nocover
        """Return representation of object.

        :return:
        """
        return f"{self.__class__.__name__}({self.a}, {self.b})"

    @property
    def elements(self) -> Tuple[Any, Any]:
        """Return elements of the relation"""
        return self.a, self.b

    def _validate(self):
        """Check whether a relation is valid or not."""
        pass

    def same_elements(self, relation: Relation) -> bool:
        """Check whether the relations are about the same pair of alternatives.

        :param relation: second relation
        :return:
            ``True`` if both relations share the same elements pair, ``False``
            otherwise

        .. warning:: Does not check for relations' validity!
        """
        return set(self.elements) == set(relation.elements)

    def __eq__(self, other: Any) -> bool:
        """Check whether relations are equal.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        if type(other) == type(self):
            return self.elements == other.elements
        return False

    def __add__(self, other: Relation) -> PreferenceStructure:
        """Build new preference structure as addition of both relations.

        :return: relations added to new preference structure
        """
        if not isinstance(other, Relation):
            raise TypeError("can only add one other Relation object")
        return PreferenceStructure([self, other])

    def __hash__(self) -> int:
        """Hash object based on its unordered list of elements"""
        return hash(self.a) + hash(self.b)

    def compatible(self, other: Relation) -> bool:
        """Check whether both relations can coexist in the same preference
        structure.

        Relations are compatible if equal or having different elements pair.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        return self == other or not self.same_elements(other)

    @staticmethod
    def types() -> List:
        """Return list of relation types.

        :return:
        """
        return Relation.__subclasses__()

    @requires_graphviz
    def _draw(self, graph: Digraph):
        """Draw relation on provided graph"""
        graph.edge(str(self.a), str(self.b), **self.DRAW_STYLE)


@set_module("mcda.relations")
class PreferenceRelation(Relation):
    """This class represents a preference relation between two elements.

    A relation is read `aPb`.

    :param a: first element
    :param b: second element
    :raise ValueError: if relation is reflexive

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances

    .. note:: this relation is antisymmetric and irreflexive
    """

    _RELATION_TYPE = "P"
    DRAW_STYLE: Dict[str, Any] = {}

    def _validate(self):
        """Check whether a relation is valid or not.

        :raise ValueError: if relation is reflexive
        """
        if self.a == self.b:
            raise ValueError(
                f"Preference relations are irreflexive: {self.a} == {self.b}"
            )


@set_module("mcda.relations")
class IndifferenceRelation(Relation):
    """This class represents an indifference relation between two elements.

    A relation is read `aIb`.

    :param a: first element
    :param b: second element

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances

    .. note:: this relation is symmetric and reflexive
    """

    _RELATION_TYPE = "I"
    DRAW_STYLE = {"arrowhead": "none"}

    __hash__ = Relation.__hash__

    def __eq__(self, other):
        """Check whether relations are equal.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        if type(other) == type(self):
            return self.same_elements(other)
        return False


@set_module("mcda.relations")
class IncomparableRelation(Relation):
    """This class represents an incomparable relation between two elements.

    A relation is read `aRb`.

    :param a: first element
    :param b: second element
    :raise ValueError: if relation is reflexive

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances

    .. note:: this relation is symmetric and irreflexive
    """

    _RELATION_TYPE = "R"
    DRAW_STYLE = {"arrowhead": "none", "style": "dotted"}

    __hash__ = Relation.__hash__

    def __eq__(self, other):
        """Check whether relations are equal.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        if type(other) == type(self):
            return self.same_elements(other)
        return False

    def _validate(self):
        """Check whether a relation is valid or not.

        :raise ValueError: if relation is reflexive
        """
        if self.a == self.b:
            raise ValueError(
                f"Incomparable relations are irreflexive: {self.a} == {self.b}"
            )


class RelationTypeView(Mapping[Type[Relation], "PreferenceStructure"]):
    """This class is a view of a :class:`PreferenceStructure` per type of
    relation.

    :param obj: preference structure
    """

    def __init__(self, obj: PreferenceStructure):
        self._preference_structure = obj

    def __len__(self) -> int:
        """Number of relation types"""
        return len(Relation.types())

    def __getitem__(self, key: Type[Relation]) -> PreferenceStructure:
        """Return preference structure with selected relation type.

        :param key: type of relation
        :return:
        """
        res = PreferenceStructure()
        for r in self._preference_structure.relations:
            if isinstance(r, key):
                res += r
        return res

    def __iter__(self) -> Iterator[Type[Relation]]:
        """Iterate on the relation types"""
        return iter(Relation.types())


class ElementView(Mapping[Any, "PreferenceStructure"]):
    """This class is a view of a :class:`PreferenceStructure` per element.

    :param obj: preference structure
    """

    def __init__(self, obj: PreferenceStructure):
        self._preference_structure = obj

    def __len__(self) -> int:
        """Number of elements"""
        return len(self._preference_structure.elements)

    def __getitem__(self, key: Any) -> PreferenceStructure:
        """Return preference structure pertaining to one element.

        :param key: element
        :return:
        """
        relations: List[Relation] = []
        for r in self._preference_structure.relations:
            if key in r.elements:
                relations.append(r)
        return PreferenceStructure(relations)

    def __iter__(self) -> Iterator:
        """Iterate on the elements"""
        return iter(self._preference_structure.elements)


class ElementsPairView(Mapping[Tuple[Any, Any], Union[Relation, None]]):
    """This class is a view of a :class:`PreferenceStructure` per pair of
    elements.

    :param obj: preference structure
    """

    def __init__(self, obj: PreferenceStructure):
        self._preference_structure = obj

    def __len__(self) -> int:
        """Number of relations"""
        return len(self._preference_structure.relations)

    def __getitem__(self, pair: Tuple[Any, Any]) -> Relation | None:
        """Return relation between elements.

        :param a:
        :param b:
        :return: relation between `a` and `b` if existing, else ``None``
        """
        _pair = set(pair)
        for r in self._preference_structure.relations:
            if set(r.elements) == _pair:
                return r
        return None

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        """Iterate on the elements pairs with an existing relation"""
        for r in self._preference_structure.relations:
            yield r.elements


@set_module("mcda.relations")
class PreferenceStructure:
    """This class represents a list of relations.

    Any type of relations is accepted, so this represents the union of P, I and
    R.

    :param data:
    :param validate: whether to check compatibility of :attr:`relations`
    :raise ValueError:
        if :attr:`relations` are not compatible and `validate` is ``True``
    """

    def __init__(
        self,
        data: Union[
            List[Relation], Relation, PreferenceStructure, None
        ] = None,
        validate: bool = True,
    ):
        data = [] if data is None else data
        if isinstance(data, Relation):
            relations = [data]
        elif isinstance(data, PreferenceStructure):
            relations = data.relations
        else:
            relations = data
        self._relations = list(set(relations))
        if validate:
            self._validate()

    @property
    def elements(self) -> List:
        """Return elements present in relations list."""
        return sorted(set(e for r in self._relations for e in r.elements))

    @property
    def relations(self) -> List[Relation]:
        """Return relations list."""
        return self._relations

    @property
    def elements_structures(self) -> Mapping[Any, PreferenceStructure]:
        """Return this preference structure viewed by each element"""
        return ElementView(self)

    @property
    def elements_pairs_relations(
        self,
    ) -> Mapping[Tuple[Any, Any], Union[Relation, None]]:
        """Return the relations keyed by elements pairs"""
        return ElementsPairView(self)

    @property
    def typed_structures(self) -> Mapping[Type[Relation], PreferenceStructure]:
        """Return the preference structures for each type of relation"""
        return RelationTypeView(self)

    def substructure(
        self,
        elements: List | None = None,
        types: List[Type[Relation]] | None = None,
    ) -> PreferenceStructure:
        """Return a new preference structure containing only set arguments.

        :param elements: if ``None`` all :attr:`elements` are used
        :param types: if ``None``, all types of relations are used
        :return:
        """
        res = PreferenceStructure()
        for r in self._relations:
            if types is not None and type(r) not in types:
                continue
            if elements is not None and (
                r.a not in elements or r.b not in elements
            ):
                continue
            res += r
        return res

    def _validate(self):
        """Check whether the relations are all valid.

        :raise ValueError: if at least two relations are incompatible
        """
        for i, r1 in enumerate(self._relations):
            for r2 in self._relations[(i + 1) :]:
                if not r1.compatible(r2):
                    raise ValueError(f"incompatible relations: {r1}, {r2}")

    @property
    def is_total_preorder(self) -> bool:
        """Check whether relations list is a total preorder or not"""
        return (
            len(self.transitive_closure.typed_structures[IncomparableRelation])
            == 0
        )

    @property
    def is_total_order(self) -> bool:
        """Check whether relations list is a total order or not"""
        return (
            len(
                self.transitive_closure.substructure(
                    types=[IndifferenceRelation, IncomparableRelation]
                )
            )
            == 0
        )

    def __eq__(self, other: Any):
        """Check if preference structure is equal to another.

        Equality is defined as having the same set of relations.

        :return:

        .. note:: `other` type is not coerced
        """
        if isinstance(other, PreferenceStructure):
            return set(other.relations) == set(self._relations)
        return False

    def __len__(self) -> int:
        """Return number of relations in the preference structure.

        :return:
        """
        return len(self._relations)

    def __str__(self) -> str:
        """Return string representation of relations.

        :return:
        """
        return "[" + ", ".join([str(r) for r in self._relations]) + "]"

    def __repr__(self) -> str:  # pragma: nocover
        """Return representation of relations contained in structure

        :return:
        """
        return f"{self.__class__.__name__}({repr(self._relations)})"

    def __contains__(self, item: Any) -> bool:
        """Check whether a relation is already in the preference structure.

        :param item: relation
        :return: check result

        .. warning:: Does not check for a relation's validity!
        """
        for r in self._relations:
            if r == item:
                return True
        return False

    def __add__(
        self, other: Relation | PreferenceStructure
    ) -> PreferenceStructure:
        """Create new preference structure with appended relations.

        :param other:
            * :class:`Relation`: relation is appended into new object
            * :class:`PreferenceStructure`: all relations are appended into new
            object
        :return:
        """
        if isinstance(other, PreferenceStructure):
            for r1 in other:
                for r2 in self:
                    if not r1.compatible(r2):
                        raise ValueError(f"incompatible relations: {r1}, {r2}")
            return self.__class__(
                self._relations + other._relations, validate=False
            )
        for r2 in self:
            if not other.compatible(r2):
                raise ValueError(f"incompatible relations: {other}, {r2}")
        return self.__class__(self._relations + [other], validate=False)

    def __sub__(
        self, other: Relation | PreferenceStructure
    ) -> PreferenceStructure:
        """Create new preference structure with deleted relations.

        :param other:
            * :class:`Relation`: relation is removed in new object
            * :class:`PreferenceStructure`: all relations are removed in new
            object
        :return:
        """
        if isinstance(other, PreferenceStructure):
            return self.__class__(
                list(set(self._relations) - {r for r in other}), validate=False
            )
        return self.__class__(
            list(set(self._relations) - {other}), validate=False
        )

    def __iter__(self) -> Iterator[Relation]:
        """Return iterator over relations

        :return:
        """
        return iter(self._relations)

    @classmethod
    def from_ranking(cls, ranking: Ranking) -> Self:
        """Convert ranking into preference structure.

        :param ranking:
        :return:

        .. note::
            The minimum number of relations representing the scores is returned
            (w.r.t transitivity of preference and indifference relations)
        """
        res: List[Relation] = []
        for i, a in enumerate(ranking.labels):
            for b in ranking.labels[(i + 1) :]:
                if ranking[a] == ranking[b]:
                    res.append(IndifferenceRelation(a, b))
                elif ranking[a] > ranking[b]:
                    res.append(PreferenceRelation(a, b))
                else:
                    res.append(PreferenceRelation(b, a))
        return cls(res)

    @classmethod
    def from_outranking_matrix(
        cls, outranking_matrix: OutrankingMatrix
    ) -> Self:
        """Convert outranking matrix to preference structure.

        :param outranking_matrix:
        :return:
        """
        relations: List[Relation] = list()
        for ii, i in enumerate(outranking_matrix.vertices):
            for j in outranking_matrix.vertices[ii + 1 :]:
                if outranking_matrix.data.at[i, j]:
                    if outranking_matrix.data.at[j, i]:
                        relations.append(IndifferenceRelation(i, j))
                    else:
                        relations.append(PreferenceRelation(i, j))
                elif outranking_matrix.data.at[j, i]:
                    relations.append(PreferenceRelation(j, i))
                else:
                    relations.append(IncomparableRelation(i, j))
        return cls(relations)

    @property
    def ranking(self) -> CommensurableValues[QuantitativeScale]:
        """Convert preference structure to ranking.

        :raises ValueError: if `preference_structure` is not a total pre-order
        :return:

        .. note:: returned ranking goes for 0 to n-1 (with 0 the best rank)
        """
        if not self.is_total_preorder:
            raise ValueError(
                "only total pre-order can be represented as Ranking"
            )
        s = Series(0, index=self.elements)
        pref_copy = self.transitive_closure
        while len(pref_copy.elements) > 0:
            bad_alternatives = set()
            for r in pref_copy.typed_structures[PreferenceRelation]:
                bad_alternatives.add(r.b)
            s[[*bad_alternatives]] += 1
            remaining_relations = []
            elements_to_delete = set(pref_copy.elements) - bad_alternatives
            for r in pref_copy.relations:
                if (
                    r.a not in elements_to_delete
                    and r.b not in elements_to_delete
                ):
                    remaining_relations.append(r)
            pref_copy = PreferenceStructure(remaining_relations)
        return CommensurableValues(
            s,
            QuantitativeScale(preference_direction=PreferenceDirection.MIN),
        )

    @property
    def outranking_matrix(self) -> OutrankingMatrix:
        """Transform a preference structure into an outranking matrix.

        :return: outranking matrix
        """
        elements = self.elements
        matrix = DataFrame(0, index=elements, columns=elements)
        fill_diagonal(matrix.values, 1)
        for r in self:
            a, b = r.elements
            if isinstance(r, PreferenceRelation):
                matrix.at[a, b] = 1
            if isinstance(r, IndifferenceRelation):
                matrix.at[a, b] = 1
                matrix.at[b, a] = 1
        return create_outranking_matrix(matrix)

    @property
    def transitive_closure(self) -> PreferenceStructure:
        """Apply transitive closure to preference structure and return result.

        .. warning:: Does not check for a valid preference structure!
        """
        return PreferenceStructure.from_outranking_matrix(
            self.outranking_matrix.transitive_closure
        )

    @property
    def transitive_reduction(self) -> PreferenceStructure:
        """Apply transitive reduction to preference structure and return result

        .. warning:: Does not check for a valid preference structure!

        .. warning:: This function may bundle together multiple elements
        """
        return PreferenceStructure.from_outranking_matrix(
            self.outranking_matrix.transitive_reduction
        )

    @requires_graphviz
    def plot(self) -> Digraph:
        """Create graph from preference structure and plot it.

        :return: graph

        .. note::
            You need an environment that will actually display the graph (such
            as a jupyter notebook), otherwise the function only returns the
            graph.
        """
        relation_graph = Digraph("relations", strict=True)
        relation_graph.attr("node", shape="box")
        for e in self.elements:
            relation_graph.node(str(e))
        for r in self._relations:
            r._draw(relation_graph)
        return relation_graph

    @requires_graphviz
    def save_plot(self) -> str:  # pragma: nocover
        """Plot preference structure as a graph and save it.

        :return: file name where plot is saved
        """
        return self.plot().render()

    def copy(self) -> PreferenceStructure:
        """Copy preference structure into new object.

        :return: copy
        """
        return PreferenceStructure(self)
