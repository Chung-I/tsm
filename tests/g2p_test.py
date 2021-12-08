from itertools import accumulate
import unittest
from typing import List, Dict, Any
import logging

import nltk
from nltk.tree import ParentedTree, Tree
import json

from tsm.sentence import Sentence
from tsm.g2p import infer_sandhi_boundary, lexical_government, get_src_sandhi_start_and_ends, infer_pron, alignment_to_tgt2src
from tsm.g2p import cut_source_tokens_from_target_tokens_and_obtain_sandhi_boundaries
from tsm.test_case import TSMTestCase
import editdistance

logger = logging.getLogger(__name__)

class TestG2P(unittest.TestCase):
    def term_error_rate(self, preds, golds):
        total_distance = 0
        total_words = 0
        for pred, gold in zip(preds, golds):
            total_distance += editdistance.eval(pred, gold)
            total_words += len(gold)
        logger.info(f"{total_distance} {total_words}")
        return total_distance / total_words

    def send_fixtures_to_g2p(self, test_case: Dict[str, Any]):
        tgt_tree_str = test_case["tgt_tree"]
        raw_src_text = test_case["src_text"]
        src_tokens = Sentence.parse_mixed_text(raw_src_text, remove_punct=True)
        alignment = test_case["alignment"]
        tgt_to_src = alignment_to_tgt2src(alignment)
        written_pron = test_case["written_pronunciation"].split()
        tgt_tree = ParentedTree.fromstring(tgt_tree_str)
        src_word_lengths, src_sandhi_boundaries = get_src_sandhi_start_and_ends(tgt_tree, src_tokens, tgt_to_src)
        pron = infer_pron(src_tokens, written_pron, src_word_lengths, src_sandhi_boundaries)
        return pron

    def test_lexical_government(self):
        tree = ParentedTree.fromstring("(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))")
        phrase_is_lexically_governed= lexical_government(tree)
        boundaries = infer_sandhi_boundary(tree, phrase_is_lexically_governed)  
        self.assertEqual(boundaries, [False, True, False, False, True])

    def test_get_character_level_sandhi_start_and_ends_from_tree(self):
        sandhi_test_json = TSMTestCase.FIXTURES_ROOT / "sandhi.json"
        with open(sandhi_test_json, "r") as f:
            test_cases = json.load(f)

        start_and_ends_list = []
        gold_start_and_ends_list = [test_case["sandhi_domain_start_ends"] for test_case in test_cases]
        actual_prons = [test_case["actual_pronunciation"].split() for test_case in test_cases]
        inferred_prons = []
        for test_case in test_cases:
            pron = self.send_fixtures_to_g2p(test_case)
            inferred_prons.append(pron)
        try:
            assert inferred_prons == actual_prons
        except AssertionError as e:
            print(e)
        assert self.term_error_rate(inferred_prons, actual_prons) < 0.1

    def test_cut_source_tokens_from_target_tokens_and_obtain_sandhi_boundaries(self):
        src_tokens = Sentence.parse_mixed_text("到厝了後愛會記得用Line敲予我")
        src_char_len = len(src_tokens)
        tgt_words = ['到', '家', '之後', '要', '記得', '用', 'Line', '打', '給', '我']
        alignment = [[0, 0],[1, 1],[2, 2],[3, 3],[4, 4],[5, 5],[6, 5],[7, 6],[8, 7],[9, 8],[10, 9],[11, 10],[12, 11]]
        tgt_to_src = alignment_to_tgt2src(alignment)
        tgt_sandhi_boundaries = [False, True, True, False, False, False, False, False, False, True]
        src_word_lengths, src_sandhi_boundaries = \
            cut_source_tokens_from_target_tokens_and_obtain_sandhi_boundaries(src_char_len, tgt_words, tgt_to_src, tgt_sandhi_boundaries)
        assert src_word_lengths == [1, 1, 2, 1, 3, 1, 1, 1, 1, 1]
        assert src_sandhi_boundaries == [False, True, True, False, False, False, False, False, False, True]

    def test_tone_sandhi_from_suisiann_text(self):
        suisiann_test_json = TSMTestCase.FIXTURES_ROOT / "suisiann.json"
        with open(suisiann_test_json, "r") as f:
            test_cases = json.load(f)

        inferred_prons = []
        actual_prons = [test_case["actual_pronunciation"].split() for test_case in test_cases]
        for test_case in test_cases:
            sent_obj = Sentence.parse_singhong_sent((test_case["taibun"], test_case["tailo"]))
            graph_text, phn_text = Sentence.get_grapheme_phoneme_pairs(sent_obj)
            test_case["src_text"] = graph_text
            test_case["written_pronunciation"] = phn_text
            inferred_pron = self.send_fixtures_to_g2p(test_case)
            inferred_prons.append(inferred_pron)
        try:
            assert inferred_prons == actual_prons
        except AssertionError as e:
            print(e)
        assert self.term_error_rate(inferred_prons, actual_prons) < 0.1