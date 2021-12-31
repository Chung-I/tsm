from typing import List, Dict, Tuple, Set
from nltk import tree
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from tsm.tone_sandhi import 台灣話口語講法

import re
import requests
from nltk.tree import Tree, ParentedTree
import logging
from collections import defaultdict
from itertools import groupby

from tsm.util import word_lengths_to_char_start_and_ends, lexify, cumsum, alignment_to_tgt2src
from tsm.util import cut_source_tokens_from_target_tokens_and_obtain_sandhi_boundaries, sandhi_mark
from tsm.util import is_preterminal, path_compression
from tsm.sentence import Sentence
from tsm.clients import MosesClient
from tsm.head_finder import HeadFinder
from tsm.chinese_head_finder import ChineseSemanticHeadFinder

logger = logging.getLogger(__name__)


class ToneSandhiG2P:
    def __init__(self,  head_finder: HeadFinder, base_g2p: MosesClient = None, parser_url: str = None) -> None:
        self.lexical_category = {'N', 'V', 'A', 'P'}
        self.base_g2p = base_g2p
        self.parser_url = parser_url
        self.head_finder = head_finder

    def __call__(self, sent: str) -> str:
        chars = Sentence.parse_mixed_text(sent)
        res = requests.post(self.parser_url, json={"sentence": " ".join(chars)})
        obj = res.json()
        tgt_tree = ParentedTree.fromstring(obj['tree'])
        alignment = obj['alignment']
        tgt_to_src = alignment_to_tgt2src(alignment)
        src_tokens = obj["source"].split()
        src_word_lengths, src_sandhi_boundaries = self.get_src_sandhi_start_and_ends(tgt_tree, src_tokens, tgt_to_src)
        phns = self.base_g2p.translate(sent).split()
        pron_as_phns = self.infer_pron(chars, phns, src_word_lengths, src_sandhi_boundaries)
        return " ".join(pron_as_phns)

    def run(self, src_text, phn_text, tgt_tree, tgt_to_src, apply_tone_sandhi=True):
        src_tokens = Sentence.parse_mixed_text(src_text)
        src_word_lengths, src_sandhi_boundaries = self.get_src_sandhi_start_and_ends(tgt_tree, src_tokens, tgt_to_src)
        phns = phn_text.split()
        graphs, phns = self.infer_pron(src_tokens, phns, src_word_lengths, src_sandhi_boundaries, apply_tone_sandhi)
        return graphs, phns

    def find_boundary_preterminal(self, root, pos, direction="right"):
        if isinstance(root[pos], Tree):
            if direction == "right":
                boundary_pos = pos + (len(root[pos])-1,)
            elif direction == "left":
                boundary_pos = pos + (0,)
            else:
                raise ValueError("direction must be either 'right' or 'left'")
            return self.find_boundary_preterminal(root, boundary_pos)
        else:
            return pos

    def infer_sandhi_boundary(self, root: ParentedTree, phrase_is_lexically_governed: Set[Tuple[int]]) -> List[bool]:

        boundary_positions = set()
        treepositions = root.treepositions()
        for pos in filter(lambda p: isinstance(root[p], Tree), treepositions):
            right_boundary_pos = self.find_boundary_preterminal(root, pos, "right")
            if root[right_boundary_pos[:-1]].label() == "PN" and right_boundary_pos != treepositions[-1]:
                logger.info("pronouns that are not at the end of the sentence don't have its sandhi domain")
                continue
            elif root[right_boundary_pos] == "的":
                logger.info("for now set all occurrences of '的' as non-boundaries")
                continue
            elif (re.match(r"[A-Z]+P$", root[pos].label()) or root[pos].label() == 'NR') and not pos in phrase_is_lexically_governed:
                logger.info(f"{lexify(root[pos])} is a sandhi domain")
                boundary_positions.add(right_boundary_pos)

        boundaries = []
        for pos in treepositions:
            if not isinstance(root[pos], Tree):
                boundaries.append(pos in boundary_positions)

        return boundaries

    def set_governed(self, root: ParentedTree, pos: Tuple[int], phrase_is_lexically_governed: Dict[Tuple[int], bool]) -> None:
        phrase_is_lexically_governed[pos] = True
        for child in root[pos]:
            if isinstance(child, Tree):
                self.set_governed(root, child.treeposition(), phrase_is_lexically_governed)

    def lexical_government(self, root: Tree) -> Set[Tuple[int]]:
        "Determine if phrase_a is phrase_b's lexical head"
        root = ParentedTree.convert(root)
        phrase_positions = {pos for pos in root.treepositions() if isinstance(root[pos], Tree)}
        phrase_is_lexically_governed: Set[Tuple[int]] = set()

        head_of_phrases = {}
        for pos in phrase_positions:
            if not is_preterminal(root[pos]):
                head: Tree = self.head_finder.determine_head(root[pos], root[pos].parent())
                head_of_phrases[pos] = head.treeposition()
        head_of_phrases = path_compression(head_of_phrases)
        logger.info("\n".join([f"head of {lexify(root[pos])}: {lexify(root[head_pos])}" for pos, head_pos in head_of_phrases.items()]))

        # first_branching_nodes = {}
        # for pos, head_pos in head_of_phrases.items():
        #     if head_pos not in first_branching_nodes and len(root[pos]) > 1:
        #         first_branching_nodes[head_pos] = pos
        #     else:
        #         if len(root[pos]) > 1 and len(pos) > len(first_branching_nodes[head_pos]):
        #             first_branching_nodes[head_pos] = pos

        phrases_that_heads_head: Dict[Set[Tuple[int]]] = defaultdict(set)
        for pos, head_pos in head_of_phrases.items():
            #if root[pos].label().startswith(root[head_pos][0]):
            phrases_that_heads_head[head_pos].add(pos)

        # for head_pos, first_branching_pos in first_branching_nodes.items():
        #     is_conjunction_phrase = any([child.label() == "CC" for child in root[first_branching_pos]])
        #     if root[head_pos].label() not in self.head_finder.nonlexical_tags:
        #         for child in root[first_branching_pos]:
        #             child_pos = child.treeposition()
        #             if isinstance(root[child_pos], Tree) and head_of_phrases.get(child_pos, child_pos) != head_pos and (not is_conjunction_phrase or child.label() == "CONJ"):
        #                 logger.info(f"{lexify(child)} is governed by {lexify(root[head_pos])}")
        #                 phrase_is_lexically_governed.add(child.treeposition())

        for head_pos, phrases_pos in phrases_that_heads_head.items():
            for phrase_pos in phrases_pos:
                is_conjunction_phrase = any([child.label() == "CC" for child in root[phrase_pos]])
                if root[head_pos].label() not in self.head_finder.nonlexical_tags:
                    for child in root[phrase_pos]:
                        child_pos = child.treeposition()
                        if root[head_pos].label()[0] == 'V' and root[child_pos].label() == "LCP":
                            continue
                        if root[head_pos].label()[0] == 'V' and root[child_pos].label() == "NP" and child_pos < head_pos:
                            continue
                        if isinstance(root[child_pos], Tree) and head_of_phrases.get(child_pos, child_pos) != head_pos and (not is_conjunction_phrase or child.label() == "CONJ"):
                            logger.info(f"{lexify(child)} is governed by {lexify(root[head_pos])}")
                            phrase_is_lexically_governed.add(child.treeposition())

        return phrase_is_lexically_governed

    def get_src_sandhi_start_and_ends(
        self,
        tgt_tree: ParentedTree,
        src_tokens: List[str],
        tgt_to_src: Dict[int, List[int]],
    ) -> Tuple[List[int], List[bool]]:
        logger.info(tgt_tree.pformat())
        phrase_is_lexically_governed = self.lexical_government(tgt_tree)
        tgt_sandhi_boundaries = self.infer_sandhi_boundary(tgt_tree, phrase_is_lexically_governed)
        src_word_lengths, src_sandhi_boundaries = \
            cut_source_tokens_from_target_tokens_and_obtain_sandhi_boundaries(len(src_tokens), tgt_tree.leaves(), tgt_to_src, tgt_sandhi_boundaries)
        return src_word_lengths, src_sandhi_boundaries

    def infer_pron(self, chars: List[str], phns: List[str], src_word_lengths: List[int], src_sandhi_boundaries: List[bool], apply_tone_sandhi=True) -> List[str]:
        start_and_ends = word_lengths_to_char_start_and_ends(src_word_lengths)
        words = ["-".join(chars[start:end]) + sandhi_mark(boundary) for (start, end), boundary in zip(start_and_ends, src_sandhi_boundaries)]
        word_phns = ["-".join(phns[start:end]) + sandhi_mark(boundary) for (start, end), boundary in zip(start_and_ends, src_sandhi_boundaries)]
        logger.info(f"grapheme phoneme pairs sent to singhong system: {' '.join(words)}, {' '.join(word_phns)}")
        sent = 拆文分析器.建立句物件(" ".join(words), " ".join(word_phns))
        tone_sandhi_sent = 台灣話口語講法(sent, apply_tone_sandhi=apply_tone_sandhi, to_phn=False, to_TLPA=True, phn_delimiter="", add_circumfix_for_non_taigi_words=False)
        graph_text = tone_sandhi_sent.看型("-", " ", " ")
        phn_text = tone_sandhi_sent.看音("-", " ", " ")
        return graph_text.split(), phn_text.split()

if __name__ == "__main__":
    from tsm.util import read_file_to_lines, write_lines_to_file
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('output_path')
    parser.add_argument('--parser-url', default="http://localhost:8080")
    parser.add_argument('--g2p-url', default="http://localhost:8000")
    parser.add_argument('--seg', action='store_true')
    args = parser.parse_args()

    sents = read_file_to_lines(args.input_path)
    g2p_client = MosesClient(args.g2p_url)
    head_finder = ChineseSemanticHeadFinder()
    sent_of_phonemes = []
    fp = open(args.output_path, 'w')
    g2p = ToneSandhiG2P(head_finder, g2p_client, args.parser_url)
    for sent in sents:
        g2p(sent)
