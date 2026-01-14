"""This module implements the UTA algorithms.

Implementation and naming conventions are taken from :cite:p:`siskos2005uta`.
"""
from typing import Any, Dict, List, Union

import numpy as np
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, lpSum
from pulp import value as pulp_value

from ..core.aggregators import AdditiveValueFunctions
from ..core.aliases import Function
from ..core.criteria_functions import CriterionFunction
from ..core.functions import DiscreteFunction, PieceWiseFunction
from ..core.interfaces import Learner, Ranker
from ..core.matrices import PerformanceTable
from ..core.relations import (
    IncomparableRelation,
    PreferenceRelation,
    PreferenceStructure,
)
from ..core.scales import (
    DiscreteQuantitativeScale,
    NormalScale,
    OrdinalScale,
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
)
from ..core.transformers import Transformer
from ..core.utils import set_module
from ..core.values import Ranking, Values


@set_module("mcda.mavt.uta")
class UTA(Learner[AdditiveValueFunctions[OrdinalScale]], Ranker):
    """This class represents the UTA disaggregator.

    :param performance_table:
    :param preference_structure:
    :param criteria_segments: number of segments per criteria
    :param delta: discrimination threshold for preference relations
    :param post_optimality: if ``True``, post-optimality is applied
    :param post_optimality_coeff:
        coefficient used to compute threshold on UTA objective function cost
        when performing post-optimality
    :param solver_args: extra arguments supplied to the solver

    :raise TypeError:
        if `relations` contains a
        :class:`mcda.api.core.relations.IncomparableRelation` instance

    :attribute relations:
        `preference_structure` given in input as a
        :class:`mcda.core.relations.PreferenceStructure`
    :attribute problem: UTA base LP problem
    :attribute post_optimality_problem: UTA post optimal LP problem

    .. note::
        Post-optimality threshold is computed as follows:
        (1 + `post_optimality_coeff`) * F_star
        where F_star is the optimum objective cost computed by UTA

    .. note::
        criteria functions are computed for normal scales, so when
        applying aggregation you must provide normalized values (
        :class:`mcda.api.core.PerformanceTable` alone are automatically
        normalized)
    """

    def __init__(
        self,
        performance_table: PerformanceTable[OrdinalScale],
        preference_structure: PreferenceStructure,
        criteria_segments: Union[Dict[Any, int], None] = None,
        delta: float = 0.001,
        post_optimality: bool = False,
        post_optimality_coeff: float = 0,
        solver_args: Union[Dict, None] = None,
    ):
        if (
            len(preference_structure.typed_structures[IncomparableRelation])
            > 0
        ):
            raise TypeError(
                f"{self.__class__} does not support IncomparableRelation "
                "structures"
            )
        self.performance_table = performance_table
        self.preference_structure = preference_structure
        self.criteria_segments = (
            {criterion: 2 for criterion in performance_table.criteria}
            if criteria_segments is None
            else criteria_segments
        )
        self.delta = delta
        self.post_optimality = post_optimality
        self.post_optimality_coeff = post_optimality_coeff
        self.solver_args = {} if solver_args is None else solver_args

        # Create LP Problem
        self.problem = LpProblem("UTA", LpMinimize)
        self.post_optimality_problem = LpProblem("Post-Optimality", LpMinimize)

    @property
    def objective(self):
        """Return objective function final value.

        Objective taken from base `problem` or `post_optimality_problem`.
        """
        if self.post_optimality:
            return pulp_value(self.post_optimality_problem.objective)
        return pulp_value(self.problem.objective)

    def disaggregate(
        self,
    ) -> AdditiveValueFunctions[OrdinalScale]:
        """Perform disaggregation and return result.

        :return: basic ranker with additive value functions
        """
        # Create all UTA variables
        g = self._generate_criteria_values_matrix(self.criteria_segments)
        u_var = self._generate_marginal_utility_variables(
            self.criteria_segments
        )
        sigma_var = self._generate_alternatives_errors_variables(
            self.performance_table.alternatives
        )

        # Create LP Problem
        self.problem = LpProblem("UTA", LpMinimize)

        # Add objective function
        self.problem += lpSum(sigma_var.values())

        # Add constraints
        self._add_uta_constraints(
            self.problem,
            Transformer.normalize(self.performance_table),
            u_var,
            sigma_var,
            g,
            self.preference_structure,
            self.delta,
        )

        # Solve problem
        self.problem.solve(**self.solver_args)

        # Compute optimum solution
        u_star = {
            criterion: [u_ij.varValue for u_ij in u_i]
            for criterion, u_i in u_var.items()
        }
        F_star = pulp_value(self.problem.objective)

        if not self.post_optimality:
            # Return optimum utility functions
            return self._compute_functions(g, u_star)

        # Compute post-optimal utility functions
        max_cost = F_star * (1 + self.post_optimality_coeff)

        u = {
            criterion: [0.0 for _ in range(n + 1)]
            for criterion, n in self.criteria_segments.items()
        }
        for ci, criterion in enumerate(g.keys()):
            for k, sense in zip(["min", "max"], [LpMinimize, LpMaximize]):
                # Create all UTA variables
                u_var = self._generate_marginal_utility_variables(
                    self.criteria_segments
                )
                sigma_var = self._generate_alternatives_errors_variables(
                    self.performance_table.alternatives
                )

                # Create post-optimality subproblem
                prob = LpProblem(f"post-Optimality-{ci}-{k}", sense)

                # Add objective function
                prob += u_var[criterion][-1]

                # Add post-optimality constraint on UTA objective value
                prob += lpSum(sigma_var.values()) <= max_cost

                # Add regular UTA constraints
                self._add_uta_constraints(
                    prob,
                    Transformer.normalize(self.performance_table),
                    u_var,
                    sigma_var,
                    g,
                    self.preference_structure,
                    self.delta,
                )

                # Solve post-optimality subproblem
                prob.solve(**self.solver_args)

                # Add solution to compounded post-optimality solution
                for i, u_i in u_var.items():
                    for j, u_ij in enumerate(u_i):
                        u[i][j] += u_ij.varValue
        # Average solutions
        for i in u:
            for j in range(len(u[i])):
                u[i][j] /= 2 * len(g)

        functions = self._compute_functions(g, u)

        # Compute post-optimality cost
        self.post_optimality_problem = LpProblem("Post-Optimality", LpMinimize)
        self.post_optimality_problem += lpSum(sigma_var.values())
        u_a = functions.aggregate(functions(self.performance_table)).data
        for relation in self.preference_structure:
            if isinstance(relation, PreferenceRelation):
                self.post_optimality_problem += (
                    u_a[relation.a]
                    + sigma_var[relation.a]
                    - u_a[relation.b]
                    - sigma_var[relation.b]
                    >= self.delta
                )
            else:
                self.post_optimality_problem += (
                    u_a[relation.a]
                    + sigma_var[relation.a]
                    - u_a[relation.b]
                    - sigma_var[relation.b]
                    == 0
                )
        self.post_optimality_problem.solve(**self.solver_args)

        return functions

    def learn(self) -> AdditiveValueFunctions[OrdinalScale]:
        """Perform disaggregation using UTA and return result.

        :return: basic ranker with additive value functions
        """
        return self.disaggregate()

    def rank(self, **kwargs) -> Ranking:
        """Rank alternatives.

        Rank alternatives in :attr:`performance_table` according to learned
        additive value functions.

        :return:
        """
        functions = self.learn()
        table = functions(self.performance_table)
        return functions.aggregate(table)

    def _compute_functions(
        self, x: Dict[Any, List[float]], y: Dict[Any, List]
    ) -> AdditiveValueFunctions[OrdinalScale]:
        """Create criteria functions from normalized points lists.

        :param x: list of normalized abscissa
        :param y: list of normalized ordinates
        :return: additive criteria functions created

        .. note::
            * Original scales are used for inputs
            * Function types are adapted to said input scales
            * Output scales are the normal scales (marginal ones and aggregated
              one)
        """
        criterion_functions: Dict[
            Any, CriterionFunction[OrdinalScale, QuantitativeScale]
        ] = {}
        for criterion, scale in self.performance_table.scales.items():
            points = [
                [x_ij, y_ij] for x_ij, y_ij in zip(x[criterion], y[criterion])
            ]
            segments = [[p1, p2] for p1, p2 in zip(points[:-1], points[1:])]
            function = PieceWiseFunction(segments=segments)
            if isinstance(scale, DiscreteQuantitativeScale):
                f: Function = DiscreteFunction(
                    {
                        v: function(Transformer.normalize(v, scale))
                        for v in scale.values
                    }
                )
            elif isinstance(scale, QualitativeScale):
                f = DiscreteFunction(
                    {
                        v: function(Transformer.normalize(v, scale))
                        for v in scale.labels
                    }
                )
            else:
                npoints = [
                    [
                        Transformer.transform(
                            x_ij, scale, QuantitativeScale.normal()
                        ),
                        y_ij,
                    ]
                    for x_ij, y_ij in zip(x[criterion], y[criterion])
                ]
                if scale.preference_direction == PreferenceDirection.MIN:
                    npoints = npoints[::-1]
                nsegments = [
                    [p1, p2] for p1, p2 in zip(npoints[:-1], npoints[1:])
                ]
                f = PieceWiseFunction(segments=nsegments)
            criterion_functions[criterion] = CriterionFunction(
                f, scale, QuantitativeScale.normal()
            )
        return AdditiveValueFunctions(
            criterion_functions,
            aggregator_scale=QuantitativeScale.normal(),
        )

    @classmethod
    def _generate_criteria_values_matrix(
        cls,
        criteria_segments: Dict[str, int],
    ) -> Dict[Any, List[float]]:
        """Compute criteria values matrix.

        :param criteria_segments: number of segments per criteria
        :return:
        """
        return {
            criterion: np.linspace(0, 1, nb_segments + 1).tolist()
            for criterion, nb_segments in criteria_segments.items()
        }

    @classmethod
    def _generate_marginal_utility_variables(
        cls,
        criteria_segments: Dict[str, int],
    ) -> Dict[Any, List[LpVariable]]:
        """Return initial marginal utility functions variables.

        :param criteria_segments: number of segments per criteria
        :return:
        """
        return {
            criterion: [
                LpVariable(f"u_{i}_{j}", lowBound=0, cat="continuous")
                for j in range(criteria_segments[criterion] + 1)
            ]
            for i, criterion in enumerate(criteria_segments.keys())
        }

    @classmethod
    def _generate_alternatives_errors_variables(
        cls, alternatives: List, prefix: str = "sigma"
    ) -> Dict[Any, LpVariable]:
        """Return initial alternatives errors variables.

        :param alternatives:
        :param prefix: prefix for :class:`pulp.LpVariable` name
        :return:
        """
        return {
            alternative: LpVariable(
                f"{prefix}_{k}", lowBound=0, cat="continuous"
            )
            for k, alternative in enumerate(alternatives)
        }

    @classmethod
    def _generate_utility_variable(
        cls,
        alternative_values: Values[NormalScale],
        u_var: Dict[Any, List[LpVariable]],
        g_matrix: Dict[Any, List[float]],
    ) -> Any:
        """Generate initial utility variable for a given alternative.

        :param alternative_values: performances of the given alternative
        :param u_var: utility function variables
        :param g_matrix: criteria values matrix
        :return:

        .. note:: Used by UTA algorithm
        """
        u_i_var = []
        for criterion, val in alternative_values.data.items():
            g_i = g_matrix[criterion]
            u_i = u_var[criterion]
            j = 0
            while val > g_i[j + 1]:
                j += 1
            u_i_var.append(
                u_i[j]
                + (val - g_i[j])
                * (u_i[j + 1] - u_i[j])
                / (g_i[j + 1] - g_i[j])
            )
        return lpSum(u_i_var)

    @classmethod
    def _add_uta_constraints(
        cls,
        problem: LpProblem,
        performance_table: PerformanceTable[NormalScale],
        u_var: Dict[Any, List[LpVariable]],
        sigma_var: Dict[Any, LpVariable],
        g_matrix: Dict[Any, List[float]],
        relations: PreferenceStructure,
        delta: float = 0.001,
    ):
        """Add UTA constraints to LP problem.

        :param problem:
        :param performance_table:
        :param u_var: utility function variables
        :param sigma_var: alternatives errors variables
        :param g_matrix: criteria values matrix
        :param relations: pairwise relations between alternatives
        :param delta: discrimination threshold for preference relations
        :return:
        """
        # Preference constraints
        u_a = {}
        for relation in relations:
            for k in relation.elements:
                if k not in u_a:
                    u_a[k] = UTA._generate_utility_variable(
                        performance_table.alternatives_values[k],
                        u_var,
                        g_matrix,
                    )
            if isinstance(relation, PreferenceRelation):
                problem += (
                    u_a[relation.a]
                    + sigma_var[relation.a]
                    - u_a[relation.b]
                    - sigma_var[relation.b]
                    >= delta
                )
            else:
                problem += (
                    u_a[relation.a]
                    + sigma_var[relation.a]
                    - u_a[relation.b]
                    - sigma_var[relation.b]
                    == 0
                )

        # Marginal utility monotonicity constraints
        for u_i in u_var.values():
            problem += u_i[0] == 0
            for u_ij, u_ij1 in zip(u_i[:-1], u_i[1:]):
                problem += u_ij1 - u_ij >= 0

        # Utility normalization constraint
        problem += lpSum(u_i[-1] for u_i in u_var.values()) == 1


@set_module("mcda.mavt.uta")
class UTAstar(UTA):
    """This class represents the UTA\\* disaggregator.

    :param performance_table:
    :param criteria_segments: number of segments per criteria
    :param preference_structure:
    :param delta: discrimination threshold for preference relations
    :param post_optimality: if ``True``, post-optimality is applied
    :param post_optimality_coeff:
        coefficient used to compute threshold on UTA objective function cost
        when performing post-optimality
    :param solver_args: extra arguments supplied to the solver

    :raise TypeError:
        if `relations` contains a
        :class:`mcda.api.core.relations.IncomparableRelation` instance

    :attribute relations:
        `preference_structure` given in input as a
        :class:`mcda.core.relations.PreferenceStructure`
    :attribute problem: UTA\\* base LP problem
    :attribute post_optimality_problem: UTA\\* post optimal LP problem

    .. note::
        Post-optimality threshold is computed as follows:
        (1 + `post_optimality_coeff`) * F_star
        where F_star is the optimum objective cost computed by UTA\\*

    .. note::
        criteria functions are computed for normal scales, so when
        applying aggregation you must provide normalized values (
        :class:`mcda.api.core.PerformanceTable` alone are automatically
        normalized)
    """

    def disaggregate(self) -> AdditiveValueFunctions[OrdinalScale]:
        """Perform disaggregation using UTA\\* and return result.

        :return: utility functions
        """
        # Create all UTA variables
        g = self._generate_criteria_values_matrix(self.criteria_segments)
        w_var = self._generate_marginal_utility_variables(
            self.criteria_segments
        )
        sigma_p_var = self._generate_alternatives_errors_variables(
            self.performance_table.alternatives, "sigma_p"
        )
        sigma_n_var = self._generate_alternatives_errors_variables(
            self.performance_table.alternatives, "sigma_n"
        )

        # Create LP Problem
        self.problem = LpProblem("UTA_star", LpMinimize)

        # Add objective function
        self.problem += lpSum(sigma_p_var.values()) + lpSum(
            sigma_n_var.values()
        )

        # Add constraints
        self._add_uta_star_constraints(
            self.problem,
            Transformer.normalize(self.performance_table),
            w_var,
            sigma_p_var,
            sigma_n_var,
            g,
            self.preference_structure,
            self.delta,
        )

        # Solve problem
        self.problem.solve(**self.solver_args)

        # Compute optimum solution
        w_star = {
            criterion: [w_ij.varValue for w_ij in w_i]
            for criterion, w_i in w_var.items()
        }
        F_star = pulp_value(self.problem.objective)

        if not self.post_optimality:
            # Compute optimum utility functions
            u_star = {
                criterion: [sum(w_i[: (j + 1)]) for j in range(len(w_i))]
                for criterion, w_i in w_star.items()
            }
            return self._compute_functions(g, u_star)

        # Compute post-optimal utility functions
        max_cost = F_star * (1 + self.post_optimality_coeff)

        w = {
            criterion: [0.0 for _ in range(n + 1)]
            for criterion, n in self.criteria_segments.items()
        }
        for ci, criterion in enumerate(g.keys()):
            for k, sense in zip(["min", "max"], [LpMinimize, LpMaximize]):
                # Create all UTA* variables
                w_var = self._generate_marginal_utility_variables(
                    self.criteria_segments
                )
                sigma_p_var = self._generate_alternatives_errors_variables(
                    self.performance_table.alternatives, "sigma_p"
                )
                sigma_n_var = self._generate_alternatives_errors_variables(
                    self.performance_table.alternatives, "sigma_n"
                )

                # Create post-optimality subproblem
                prob = LpProblem(f"post-Optimality-{ci}-{k}", sense)

                # Add objective function
                prob += lpSum(w_var[criterion])

                # Add post-optimality constraint on UTA* objective value
                prob += (
                    lpSum(sigma_p_var.values()) + lpSum(sigma_n_var.values())
                    <= max_cost
                )

                # Add regular UTA* constraints
                self._add_uta_star_constraints(
                    prob,
                    Transformer.normalize(self.performance_table),
                    w_var,
                    sigma_p_var,
                    sigma_n_var,
                    g,
                    self.preference_structure,
                    self.delta,
                )

                # Solve post-optimality subproblem
                prob.solve(**self.solver_args)

                # Add solution to compounded post-optimality solution
                for i, w_i in w_var.items():
                    for j, w_ij in enumerate(w_i):
                        w[i][j] += w_ij.varValue
        # Average solutions
        for i in w:
            for j in range(len(w[i])):
                w[i][j] /= 2 * len(g)

        # Compute optimum utility functions
        u = {
            criterion: [sum(w_i[: (j + 1)]) for j in range(len(w_i))]
            for criterion, w_i in w.items()
        }
        functions = self._compute_functions(g, u)

        # Compute post optimality cost
        self.post_optimality_problem = LpProblem("Post-Optimality", LpMinimize)
        self.post_optimality_problem += lpSum(sigma_p_var.values()) + lpSum(
            sigma_n_var.values()
        )
        u_a = functions.aggregate(functions(self.performance_table)).data
        for relation in self.preference_structure:
            if isinstance(relation, PreferenceRelation):
                self.post_optimality_problem += (
                    u_a[relation.a]
                    + sigma_n_var[relation.a]
                    + sigma_p_var[relation.b]
                    - u_a[relation.b]
                    - sigma_n_var[relation.b]
                    - sigma_p_var[relation.a]
                    >= self.delta
                )
            else:
                self.post_optimality_problem += (
                    u_a[relation.a]
                    + sigma_n_var[relation.a]
                    + sigma_p_var[relation.b]
                    - u_a[relation.b]
                    - sigma_n_var[relation.b]
                    - sigma_p_var[relation.a]
                    == 0
                )
        self.post_optimality_problem.solve(**self.solver_args)

        return functions

    @classmethod
    def _generate_utility_variable_star(
        cls,
        alternative_values: Values[NormalScale],
        w_var: Dict[Any, List[LpVariable]],
        g_matrix: Dict[Any, List[float]],
    ) -> Any:
        """Generate initial step utility variable for a given alternative.

        `w_var` corresponds to step increases of the utility variables.

        :param alternative_values: performances of the given alternative
        :param w_var: differential utility function variables
        :param g_matrix: criteria values matrix
        :return:
        """
        w_i_var = []
        for criterion, val in alternative_values.data.items():
            g_i = g_matrix[criterion]
            w_i = w_var[criterion]
            prev_g_ij = g_i[0]
            for g_ij, w_ij in zip(g_i, w_i):
                if val >= g_ij:
                    w_i_var.append(w_ij)
                else:
                    w_i_var.append(
                        w_ij * (val - prev_g_ij) / (g_ij - prev_g_ij)
                    )
                    break
                prev_g_ij = g_ij
        return lpSum(w_i_var)

    @classmethod
    def _add_uta_star_constraints(
        cls,
        problem: LpProblem,
        performance_table: PerformanceTable[NormalScale],
        w_var: Dict[Any, List[LpVariable]],
        sigma_p_var: Dict[Any, LpVariable],
        sigma_n_var: Dict[Any, LpVariable],
        g_matrix: Dict[Any, List[float]],
        relations: PreferenceStructure,
        delta: float = 0.001,
    ):
        """Add UTA\\* constraints to LP problem.

        :param problem:
        :param performance_table:
        :param w_var: differential utility function variables
        :param sigma_p_var: positive alternatives errors variables
        :param sigma_n_var: negative alternatives errors variables
        :param g_matrix: criteria values matrix
        :param relations: pairwise relations between alternatives
        :param delta: discrimination threshold for preference relations
        :return:
        """

        # Preference constraints
        u_a = {}
        for relation in relations:
            for k in relation.elements:
                if k not in u_a:
                    u_a[k] = UTAstar._generate_utility_variable_star(
                        performance_table.alternatives_values[k],
                        w_var,
                        g_matrix,
                    )
            if isinstance(relation, PreferenceRelation):
                problem += (
                    u_a[relation.a]
                    + sigma_n_var[relation.a]
                    + sigma_p_var[relation.b]
                    - u_a[relation.b]
                    - sigma_n_var[relation.b]
                    - sigma_p_var[relation.a]
                    >= delta
                )
            else:
                problem += (
                    u_a[relation.a]
                    + sigma_n_var[relation.a]
                    + sigma_p_var[relation.b]
                    - u_a[relation.b]
                    - sigma_n_var[relation.b]
                    - sigma_p_var[relation.a]
                    == 0
                )

        # Normalized utility function
        problem += lpSum(w_ij for w_ij in (w_i for w_i in w_var.values())) == 1
