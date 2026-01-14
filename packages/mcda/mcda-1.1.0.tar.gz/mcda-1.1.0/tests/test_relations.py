import unittest

from graphviz import Digraph

from mcda.matrices import create_outranking_matrix
from mcda.relations import I, P, PreferenceStructure, R
from mcda.scales import PreferenceDirection, QuantitativeScale
from mcda.set_functions import HashableSet
from mcda.types import Relation
from mcda.values import CommensurableValues


class RelationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.r1 = Relation(0, 1)
        self.r2 = Relation(0, 1)
        self.r3 = Relation(1, 0)
        self.r4 = Relation(1, 2)
        self.r5: Relation = P(0, 1)

    def test_constructor(self):
        self.assertEqual((self.r1.a, self.r1.b), (0, 1))

    def test_elements(self):
        self.assertEqual(self.r1.elements, (0, 1))

    def test_same_elements(self):
        self.assertTrue(self.r1.same_elements(self.r2))
        self.assertTrue(self.r1.same_elements(self.r3))
        self.assertFalse(self.r1.same_elements(self.r4))

    def test_equal(self):
        self.assertEqual(self.r1, self.r2)
        self.assertNotEqual(self.r1, self.r3)
        self.assertNotEqual(self.r1, self.r5)

    def test_add(self):
        self.assertRaises(TypeError, lambda r1, r2: r1 + r2, self.r1, (0, 1))
        self.assertTrue(isinstance(self.r1 + self.r4, PreferenceStructure))

    def test_hash(self):
        self.assertEqual(hash(self.r1), hash(self.r3))

    def test_compatible(self):
        self.assertTrue(self.r1.compatible(self.r2))
        self.assertFalse(self.r1.compatible(self.r3))
        self.assertTrue(self.r1.compatible(self.r4))
        self.assertFalse(self.r1.compatible(self.r5))

    def test_types(self):
        self.assertEqual(
            set(Relation.types()),
            {
                P,
                R,
                I,
            },
        )


class PreferenceRelationTestCase(RelationTestCase):
    def setUp(self) -> None:
        self.r1 = P(0, 1)
        self.r2 = P(0, 1)
        self.r3 = P(1, 0)
        self.r4 = P(1, 2)
        self.r5 = I(0, 1)

    def test_constructor(self):
        self.assertRaises(ValueError, P, 0, 0)

    def test_compatible(self):
        self.assertTrue(self.r1.compatible(self.r2))
        self.assertFalse(self.r1.compatible(self.r3))
        self.assertTrue(self.r1.compatible(self.r4))


class IndifferenceRelationTestCase(RelationTestCase):
    def setUp(self) -> None:
        self.r1 = I(0, 1)
        self.r2 = I(0, 1)
        self.r3 = I(1, 0)
        self.r4 = I(2, 1)
        self.r5 = P(0, 1)

    def test_equal(self):
        self.assertEqual(self.r1, self.r2)
        self.assertEqual(self.r1, self.r3)
        self.assertNotEqual(self.r1, self.r5)

    def test_compatible(self):
        self.assertTrue(self.r1.compatible(self.r2))
        self.assertTrue(self.r1.compatible(self.r3))
        self.assertTrue(self.r1.compatible(self.r4))
        self.assertFalse(self.r1.compatible(self.r5))


class IncomparableRelationTestCase(IndifferenceRelationTestCase):
    def setUp(self) -> None:
        self.r1 = R(0, 1)
        self.r2 = R(0, 1)
        self.r3 = R(1, 0)
        self.r4 = R(2, 1)
        self.r5 = P(0, 1)

    def test_constructor(self):
        self.assertRaises(ValueError, R, 0, 0)


class PreferenceStructureTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.relations_list = [
            P(1, 0),
            I(1, 2),
            P(2, 3),
            R(3, 4),
        ]
        self.relations = PreferenceStructure(self.relations_list)
        self.outranking_matrix = create_outranking_matrix(
            [
                [1, 0, 0, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ]
        )
        self.transitive_closure = create_outranking_matrix(
            [
                [1, 0, 0, 0, 0],
                [1, 1, 1, 1, 0],
                [1, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ]
        )
        self.transitive_reduction = PreferenceStructure(
            [
                P((1, 2), (0,)),
                P((1, 2), (3,)),
            ]
        )
        self.elements = [0, 1, 2, 3, 4]
        self.total_preorder = PreferenceStructure(
            [
                P(0, 1),
                I(1, 2),
                P(2, 3),
            ]
        )
        self.total_order = PreferenceStructure(
            [
                P(0, 1),
                P(1, 2),
                P(2, 3),
            ]
        )

    def test_constructor(self):
        self.assertEqual(self.relations._relations, self.relations_list)
        self.assertEqual(
            PreferenceStructure(self.relations_list * 2)._relations,
            self.relations_list,
        )
        self.assertEqual(PreferenceStructure().relations, [])
        self.assertEqual(
            PreferenceStructure(self.relations).relations,
            self.relations.relations,
        )
        self.assertEqual(
            PreferenceStructure(P(0, 1)).relations,
            [P(0, 1)],
        )
        self.assertRaises(
            ValueError,
            PreferenceStructure,
            [P(0, 1), P(1, 0)],
        )
        PreferenceStructure(
            [P(0, 1), P(1, 0)],
            validate=False,
        )

    def test_elements(self):
        self.assertEqual(self.relations.elements, self.elements)

    def test_length(self):
        self.assertEqual(len(self.relations), len(self.relations_list))

    def test_elements_structures(self):
        expected = {
            0: PreferenceStructure([P(1, 0)]),
            1: PreferenceStructure([P(1, 0), I(2, 1)]),
            2: PreferenceStructure([I(1, 2), P(2, 3)]),
            3: PreferenceStructure([P(2, 3), R(4, 3)]),
            4: PreferenceStructure([R(3, 4)]),
        }
        self.assertEqual(dict(self.relations.elements_structures), expected)
        self.assertEqual(
            self.relations.elements_structures[5], PreferenceStructure()
        )
        self.assertEqual(
            len(self.relations.elements_structures),
            len(self.relations.elements),
        )

    def test_elements_pairs_relations(self):
        expected = {
            (1, 0): P(1, 0),
            (1, 2): I(1, 2),
            (2, 3): P(2, 3),
            (3, 4): R(3, 4),
        }
        self.assertEqual(
            dict(self.relations.elements_pairs_relations), expected
        )
        self.assertIn((0, 1), self.relations.elements_pairs_relations)
        self.assertIsNone(
            self.relations.elements_pairs_relations[HashableSet([0, 3])]
        )
        self.assertEqual(
            len(self.relations.elements_pairs_relations),
            len(self.relations.relations),
        )

    def test_typed_structures(self):
        expected = {
            P: PreferenceStructure([P(1, 0), P(2, 3)]),
            I: PreferenceStructure([I(2, 1)]),
            R: PreferenceStructure([R(3, 4)]),
        }
        self.assertEqual(self.relations.typed_structures, expected)
        self.assertEqual(
            len(self.relations.typed_structures), len(Relation.types())
        )

    def test_substructure(self):
        self.assertEqual(self.relations.substructure(), self.relations)
        self.assertEqual(
            self.relations.substructure(elements=[0, 1, 2], types=[P, R]),
            PreferenceStructure([P(1, 0)]),
        )
        self.assertEqual(
            self.relations.substructure(elements=[0, 1, 2]),
            PreferenceStructure([P(1, 0), I(1, 2)]),
        )
        self.assertEqual(
            self.relations.substructure(types=[P, R]),
            PreferenceStructure([P(1, 0), P(2, 3), R(4, 3)]),
        )

    def test_add(self):
        r1 = self.relations + P(4, 5)
        self.assertEqual(r1._relations, self.relations_list + [P(4, 5)])

        r2 = PreferenceStructure([P(4, 5)])
        self.assertEqual(
            (self.relations + r2)._relations,
            self.relations_list + [P(4, 5)],
        )

        with self.assertRaises(ValueError):
            self.relations + P(0, 1)
        with self.assertRaises(ValueError):
            self.relations + PreferenceStructure([P(0, 1)])

    def test_sub(self):
        r1 = self.relations - I(1, 2)
        self.assertEqual(
            set(r1.relations),
            set(self.relations_list) - {I(1, 2)},
        )
        r2 = self.relations - PreferenceStructure([I(1, 2)])
        self.assertEqual(
            set(r2.relations),
            set(self.relations_list) - {I(1, 2)},
        )

    def test_is_total_preorder(self):
        self.assertFalse(self.relations.is_total_preorder)
        self.assertTrue(self.total_preorder.is_total_preorder)
        self.assertTrue(self.total_order.is_total_preorder)

    def test_is_total_order(self):
        self.assertFalse(self.relations.is_total_order)
        self.assertFalse(self.total_preorder.is_total_order)
        self.assertTrue(self.total_order.is_total_order)

    def test_equal(self):
        self.assertEqual(
            self.relations, PreferenceStructure(self.relations_list)
        )
        self.assertNotEqual(self.relations, self.relations_list)

    def test_contains(self):
        self.assertTrue(P(1, 0) in self.relations)
        self.assertFalse(P(0, 2) in self.relations)

    def test_transitive_closure(self):
        self.assertEqual(
            self.relations.transitive_closure,
            PreferenceStructure.from_outranking_matrix(
                self.outranking_matrix.transitive_closure
            ),
        )

    def test_transitive_reduction(self):
        res = self.relations.transitive_reduction.substructure(types=[P, I])
        self.assertEqual(self.transitive_reduction, res)

    def test_from_outranking_matrix(self):
        create_outranking_matrix(
            [
                [1, 0, 0, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ]
        )
        expected = PreferenceStructure(
            [
                P(1, 0),
                R(0, 2),
                R(0, 3),
                R(0, 4),
                I(1, 2),
                R(1, 3),
                R(1, 4),
                P(2, 3),
                R(2, 4),
                R(3, 4),
            ]
        )
        self.assertEqual(
            PreferenceStructure.from_outranking_matrix(self.outranking_matrix),
            expected,
        )

    def test_outranking_matrix(self):
        expected = create_outranking_matrix(
            [
                [1, 0, 0, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ]
        )
        self.assertEqual(self.relations.outranking_matrix, expected)

    def test_from_ranking(self):
        ranking = CommensurableValues([0, 1, 2, 1])
        expected = PreferenceStructure(
            [
                P(1, 0),
                P(2, 0),
                P(3, 0),
                P(2, 1),
                I(1, 3),
                P(2, 3),
            ]
        )
        self.assertEqual(PreferenceStructure.from_ranking(ranking), expected)

    def test_ranking(self):
        with self.assertRaises(ValueError):
            self.relations.ranking
        relations = PreferenceStructure(
            [
                P(1, 0),
                P(2, 1),
                P(2, 3),
                I(1, 3),
            ]
        )
        expected = CommensurableValues(
            [2, 1, 0, 1],
            scale=QuantitativeScale(
                preference_direction=PreferenceDirection.MIN
            ),
        )
        self.assertEqual(relations.ranking, expected)

    def test_copy(self):
        r = self.relations.copy()
        self.assertEqual(r, self.relations)
        r += I(4, 5)
        self.assertNotEqual(r, self.relations)

    def test_str(self):
        expected = "[1 P 0, 1 I 2, 2 P 3, 3 R 4]"
        self.assertEqual(str(self.relations), expected)

    def test_to_graph(self):
        relation_graph = Digraph("relations", strict=True)
        relation_graph.attr("node", shape="box")
        relation_graph.node("0")
        relation_graph.node("1")
        relation_graph.node("2")
        relation_graph.node("3")
        relation_graph.node("4")
        relation_graph.edge("1", "0")
        relation_graph.edge("1", "2", arrowhead="none")
        relation_graph.edge("2", "3")
        relation_graph.edge("3", "4", arrowhead="none", style="dotted")
        self.assertEqual(self.relations.plot().body, relation_graph.body)
