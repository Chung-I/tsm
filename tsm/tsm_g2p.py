
from typing import List, Dict, Tuple
from nltk import tree
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from tsm.tone_sandhi import 台灣話口語講法

import requests
from nltk.tree import Tree, ParentedTree
import logging

from tsm.sentence import Sentence
from tsm.clients import MosesClient


LEXICAL_POS = {
    'N', 'V', 'A', 'P'
}


logger = logging.getLogger(__name__)

def lexify(obj):
    if isinstance(obj, Tree):
        return obj.flatten()
    return obj

def find_right_boundary_preterminal(root, pos):
    right_boundary_pos = pos + (len(root[pos])-1,)
    if isinstance(root[right_boundary_pos], Tree):
        return find_right_boundary_preterminal(root, right_boundary_pos)
    else:
        return right_boundary_pos

def infer_sandhi_boundary(root: ParentedTree, phrase_is_lexically_governed) -> List[bool]:

    boundary_positions = set()
    treepositions = root.treepositions()
    for pos in phrase_is_lexically_governed:
        if root[pos].label().endswith('P') and not phrase_is_lexically_governed[pos]:
            logger.info(f"{lexify(root[pos])} is a sandhi domain")
            right_boundary_pos = find_right_boundary_preterminal(root, pos)
            if root[right_boundary_pos[:-1]].label() == "PN" and right_boundary_pos != treepositions[-1]:
                logger.info("pronouns that are not at the end of the sentence don't have its sandhi domain")
                continue
            boundary_positions.add(right_boundary_pos)

    boundaries = []
    for pos in treepositions:
        if not isinstance(root[pos], Tree):
            if pos in boundary_positions:
                if root[pos] == "的" and root[pos[:-1]].label() == "DEC":
                    boundaries[-1] = False
                    boundaries.append(False)
                else:
                    boundaries.append(True)
            else:
                boundaries.append(False)

    return boundaries

def lexical_government(root: ParentedTree) -> Dict[Tuple[int], bool]:
    "Determine if phrase_a is phrase_b's lexical head"
    phrase_is_lexically_governed = {subtree.treeposition(): False for subtree in root.subtrees()}
    for pos in root.treepositions():
        if not isinstance(root[pos], Tree): # skip root and leaves
            logger.info(f"{lexify(root[pos])} is terminal; skipping")
            continue
        if root[pos].parent() is None:
            logger.info(f"{lexify(root[pos])} is root; skipping")
            continue
        if (cur_label_prefix := root[pos].label()[0]) not in LEXICAL_POS: # skip non-lexical head
            logger.info(f"{lexify(root[pos])} is not lexical; skipping")
            continue
        parent_label = root[pos].parent().label()
        if parent_label.startswith(cur_label_prefix) and cur_label_prefix in LEXICAL_POS: # subt is the lexical head of the parent phrase
            parent_index = root[pos].parent_index()
            for sibling_index in filter(lambda idx: idx != parent_index, range(0, len(root[pos].parent()))):
                sibling_pos = pos[:-1] + (sibling_index,)
                phrase_is_lexically_governed[sibling_pos] = True
                logger.info(f"{lexify(root[pos])} lexically governs {lexify(root[sibling_pos])}")

    return phrase_is_lexically_governed

def word_lengths_to_char_start_and_ends(word_lengths: List[int]) -> List[Tuple[int, int]]:
    start = 0
    end = 0
    start_and_ends = []
    for word_len in word_lengths:
        end += word_len
        start_and_ends.append((start, end))
        start = end
    return start_and_ends

def phrase_boundary_to_start_and_ends(boundaries: List[bool]) -> List[Tuple[int, int]]:
    """
        [False, False, True, False, True] -> [(0, 3), (3, 5)]
    """
    start = 0
    start_and_ends = []
    for idx in range(len(boundaries)):
        if boundaries[idx]:
            start_and_ends.append((start, idx+1))
            start = idx+1
    return start_and_ends

def get_character_level_sandhi_start_and_ends(words, word_sandhi_boundaries) -> List[Tuple[int, int]]:
    """
    """
    char_sandhi_start_and_ends = []
    char_start_and_ends = word_lengths_to_char_start_and_ends(map(len, words))
    for start, end in phrase_boundary_to_start_and_ends(word_sandhi_boundaries):
        char_start = char_start_and_ends[start][0]
        char_end = char_start_and_ends[end-1][1]
        char_sandhi_start_and_ends.append((char_start, char_end))
    return char_sandhi_start_and_ends

def get_character_level_sandhi_start_and_ends_from_tree(
    tgt_tree: ParentedTree,
    src_tokens: List[str],
    tgt_to_src: Dict[int, int]
) -> List[Tuple[int, int]]:
    phrase_is_lexically_governed = lexical_government(tgt_tree)
    tgt_sandhi_boundaries = infer_sandhi_boundary(tgt_tree, phrase_is_lexically_governed)
    tgt_char_sandhi_start_and_ends = get_character_level_sandhi_start_and_ends(tgt_tree.leaves(), tgt_sandhi_boundaries)
    src_char_sandhi_boundaries = [False for _ in src_tokens]
    for tgt_start, tgt_end in tgt_char_sandhi_start_and_ends:
        src_end = tgt_to_src[tgt_end-1]
        src_char_sandhi_boundaries[src_end] = True
    src_char_sandhi_start_and_ends = phrase_boundary_to_start_and_ends(src_char_sandhi_boundaries)
    return src_char_sandhi_start_and_ends

def infer_pron(chars: List[str], phns: List[str], src_char_sandhi_start_and_ends: List[Tuple[int, int]]) -> List[str]:
    char_phn_pairs = list(zip(chars, phns))
    chunks = []
    for start, end in src_char_sandhi_start_and_ends:
        chunk_chars, chunk_phns = zip(*char_phn_pairs[start:end])
        chunk = 拆文分析器.建立句物件(" ".join(chunk_chars), " ".join(chunk_phns))
        tone_sandhi_chunk = 台灣話口語講法(chunk, to_phn=False, to_TLPA=True, phn_delimiter="")
        chunks.append(tone_sandhi_chunk.看音(物件分字符號=' ', 物件分詞符號=' ', 物件分句符號=' '))
    return chunks

def g2p(sent, parser_url, g2p_client):
    chars = Sentence.parse_mixed_text(sent)
    res = requests.post(parser_url, json={"sentence": " ".join(chars)})
    obj = res.json()
    tgt_tree = ParentedTree.fromstring(obj['tree'])
    alignment = obj['alignment']
    src_to_tgt = {src: tgt for src, tgt in alignment}
    tgt_to_src = {tgt: src for src, tgt in alignment}
    src_tokens = obj["source"].split()
    tgt_tokens = obj["target"].split()
    align_info = " ".join(f"{src_tokens[align[0]]}-{tgt_tokens[align[1]]}" for align in alignment)
    src_char_sandhi_start_and_ends = get_character_level_sandhi_start_and_ends_from_tree(tgt_tree, src_tokens, tgt_to_src)
    phns = g2p_client.translate(sent).split()
    pron_as_phns = infer_pron(chars, phns, src_char_sandhi_start_and_ends)
    return " ".join(pron_as_phns)


if __name__ == "__main__":
    from tsm.util import read_file_to_lines, write_lines_to_file
    # You need to wait until the docker is ready.
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
    sent_of_phonemes = []
    fp = open(args.output_path, 'w')
    for sent in sents:
        g2p(sent, args.parser_url, g2p_client)
