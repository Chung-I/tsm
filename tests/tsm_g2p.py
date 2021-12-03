import unittest
from tsm.tsm_g2p import infer_sandhi_boundary, lexical_government, find_right_boundary_preterminal
import nltk
from nltk.tree import ImmutableParentedTree, Tree


class testLexicalGovernment(unittest.TestCase):
    def test_lexical_government(self):
        tree = ImmutableParentedTree.fromstring("(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))")
        phrase_is_lexically_governed= lexical_government(tree)
        boundaries = infer_sandhi_boundary(tree, phrase_is_lexically_governed)
        
        self.assertEqual(boundaries, [False, True, False, False, True])