import unittest
from unittest import suite
from tsm.sentence import Sentence

class TestSentence(unittest.TestCase):
    def test_parse_singhong_sent(self):
        sent_obj = Sentence.parse_singhong_sent('紅-嬰-仔｜ang5-enn1-a2 哭｜khau3 甲｜kah4 一｜tsit8 身-軀｜sin1-khu1 汗｜kuann7 。｜.')
        chars = Sentence.process_singhong_sent(sent_obj)
        self.assertEqual(chars, '紅 嬰 仔 哭 甲 一 身 軀 汗')

    def test_parse_to_graph_phn_pairs(self):
        sent_obj = Sentence.parse_singhong_sent('紅-嬰-仔｜ang5-enn1-a2 哭｜khau3 甲｜kah4 一｜tsit8 身-軀｜sin1-khu1 汗｜kuann7 。｜.')
        graph_text, phn_text = Sentence.get_grapheme_phoneme_pairs(sent_obj)
        self.assertEqual(graph_text, '紅 嬰 仔 哭 甲 一 身 軀 汗')
        self.assertEqual(phn_text, 'ang5 enn1 a2 khau3 kah4 tsit8 sin1 khu1 kuann7')

        suisiann_taibun = "佗一條路是著的？"
        suisiann_tailo = "Tó tsi̍t tiâu lōo sī tio̍h--ê?"
        sent_obj = Sentence.parse_singhong_sent((suisiann_taibun, suisiann_tailo))
        graph_text, phn_text = Sentence.get_grapheme_phoneme_pairs(sent_obj)
        self.assertEqual(graph_text, "佗 一 條 路 是 著 的")
        self.assertEqual(phn_text, "to2 tsit8 tiau5 loo7 si7 tioh8 e5")