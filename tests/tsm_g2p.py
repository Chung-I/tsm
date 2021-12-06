import unittest
from typing import List, Dict
from tsm.tsm_g2p import infer_sandhi_boundary, lexical_government, get_character_level_sandhi_start_and_ends_from_tree, infer_pron
import nltk
from nltk.tree import ParentedTree, Tree


class testG2P(unittest.TestCase):
    def test_lexical_government(self):
        tree = ParentedTree.fromstring("(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))")
        phrase_is_lexically_governed= lexical_government(tree)
        boundaries = infer_sandhi_boundary(tree, phrase_is_lexically_governed)
        
        self.assertEqual(boundaries, [False, True, False, False, True])
    def test_get_character_level_sandhi_start_and_ends_from_tree(self):
        test_cases = [
            (
                """
                    (TOP
                    (IP
                        (NP (PN 他))
                        (VP
                        (VC 是)
                        (NP
                            (QP (CD 一) (CLP (M 個)))
                            (CP (CP (IP (VP (ADVP (AD 很)) (VP (VA 聰明)))) (DEC 的)))
                            (NP (NN 孩子))))))
                """,
                list("伊是一个誠巧的囝仔"),
                {
                    0: 0,
                    1: 1,
                    2: 2,
                    3: 3,
                    4: 4,
                    5: 5,
                    6: 6,
                    7: 6,
                    8: 7,
                    9: 8
                },
                "i1 si7 tsit8 e5 tsiann5 khiau2 e5 gin2 na2",
                [(0, 1), (1, 6), (6, 7), (7, 9)],
                "i7 si3 tsit10 e7 tsiann7 khiau2 e7 gin1 na2",
            ),
            (
                """
                    (TOP
                        (IP
                            (NP (NN 錄影帶))
                            (VP (VP (VV 租) (QP (CD 一) (CLP (M 齣)))) (VP (MSP 來) (VP (VV 看))))))
                """,
                list("錄影片租一齣來看"),
                {
                    0: 0,
                    1: 1,
                    2: 2,
                    3: 3,
                    4: 4,
                    5: 5,
                    6: 6,
                    7: 7
                },
                "lok8 iann2 phinn3 tsoo1 tsit8 tshut4 lai5 kuann3",
                [(0, 3), (3, 6), (6, 8)],
                "lok10 iann1 phinn3 tsoo7 tsit10 tshut4 lai7 kuann3"
            ),
            (
                "(TOP (IP (ADVP (AD 幸好)) (NP (PN 我)) (VP (ADVP (AD 沒)) (VP (VV 去)))))",
                list("佳哉我沒去"),
                {
                    0: 0,
                    1: 1,
                    2: 2,
                    3: 3,
                    4: 4,
                },
                "ka1 tsai3 gua2 bor5 khi3",
                [(0, 2), (2, 3), (3, 5)],
                "ka7 tsai3 gua1 bor7 khi3",
            ),
            (
                "(TOP (IP (NP (PN 我)) (VP (ADVP (AD 幸好)) (ADVP (AD 沒)) (VP (VV 去)))))",
                list("我佳哉沒去"),
                {
                    0: 0,
                    1: 1,
                    2: 2,
                    3: 3,
                    4: 4,
                },
                "gua2 ka1 tsai3 bor5 khi3",
                [(0, 1), (1, 5)],
                "gua1 ka7 tsai2 bor7 khi3",
            )
        ]
        start_and_ends_list = []
        gold_start_and_ends_list = [test_cases[-2] for test_cases in test_cases]
        gold_prons = [test_cases[-1] for test_cases in test_cases]
        prons = []
        for tgt_tree_str, src_tokens, tgt_to_src, phn_text, _, _ in test_cases:
            tgt_tree = ParentedTree.fromstring(tgt_tree_str)
            tgt_tree.pretty_print()
            start_and_ends  = get_character_level_sandhi_start_and_ends_from_tree(tgt_tree, src_tokens, tgt_to_src)
            pron_as_phns = infer_pron(src_tokens, phn_text.split(), start_and_ends)
            pron = " ".join(pron_as_phns)
            start_and_ends_list.append(start_and_ends)
            prons.append(pron)
        assert prons == gold_prons and start_and_ends_list == gold_start_and_ends_list 