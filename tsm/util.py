from typing import List, Dict, Tuple, Iterable, Union
from itertools import product, accumulate, groupby
from functools import lru_cache
from collections import defaultdict
import re
import logging
import os

import unicodedata
import csv
from nltk.tree import Tree

from tsm.sentence import Sentence
from tsm.symbols import 臺灣閩南語羅馬字拼音聲母表
from tsm.symbols import 臺灣閩南語羅馬字拼音韻母表
from 臺灣言語工具.基本物件.公用變數 import 分字符號, 分詞符號
from tsm.symbols import iNULL, TONES, is_phn, all_syls
from tsm.POJ_TL import poj_tl
from tsm.sentence import Sentence

flatten = lambda l: [item for sublist in l for item in sublist]

def file_exists_and_not_empty(file: str):
    return os.path.exists(file) and os.path.getsize(file) > 0

def is_preterminal(t: Tree):
    return all(map(lambda c: isinstance(c, str), t))

def path_compression(dictionary: Dict[Tuple[int], Tuple[int]]):
    dictionary_compressed = {}
    for key in dictionary:
        value = dictionary[key]
        while dictionary.get(value):
            value = dictionary[value]
        dictionary_compressed[key] = value
    return dictionary_compressed

def get_label(maybe_tree: Union[Tree, str]) -> str:
    if isinstance(maybe_tree, Tree):
        return maybe_tree.label()
    return maybe_tree

def lexify(obj):
    if isinstance(obj, Tree):
        return obj.flatten()
    return obj

def sandhi_mark(is_boundary: bool):
    return " #" if is_boundary else ""

def cut_source_tokens_from_target_tokens_and_obtain_sandhi_boundaries(
    src_char_len: int,
    tgt_words: List[str],
    tgt_to_src: Dict[int, List[int]],
    tgt_sandhi_boundaries: List[bool],
) -> Tuple[List[int], List[bool]]:
    src_char_sandhi_boundaries: List[bool] = [False] * src_char_len
    tgt_char_start_and_ends: List[Tuple[int, int]] = word_lengths_to_char_start_and_ends(map(lambda word: len(Sentence.parse_mixed_text(word)), tgt_words))
    tgt_word_indices_for_src_chars: List[int] = [-1] * src_char_len
    for word_idx, (start, end) in enumerate(tgt_char_start_and_ends):
        max_src_char_idx = -1
        for tgt_char_idx in range(start, end):
            for src_char_idx in tgt_to_src[tgt_char_idx]:
                max_src_char_idx = max(max_src_char_idx, src_char_idx)
                tgt_word_indices_for_src_chars[src_char_idx] = word_idx
        src_char_sandhi_boundaries[max_src_char_idx] = tgt_sandhi_boundaries[word_idx]

    src_word_lengths = [len(list(values)) for _, values in groupby(tgt_word_indices_for_src_chars)]
    src_sandhi_boundaries = [src_char_sandhi_boundaries[idx-1] for idx in cumsum(src_word_lengths)]

    return src_word_lengths, src_sandhi_boundaries

def cumsum(lst):
    return list(accumulate(lst))

def alignment_to_tgt2src(alignment: List[Tuple[int, int]]) -> Dict[int, List[int]]:
    """
    paired alignment to target to source token mapping.
    """
    tgt2src: Dict[int, List[int]] = defaultdict(list)
    for src_idx, tgt_idxs in alignment:
        tgt2src[tgt_idxs].append(src_idx)
    return tgt2src

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

def word_lengths_to_char_start_and_ends(word_lengths: Iterable[int]) -> List[Tuple[int, int]]:
    start = 0
    end = 0
    start_and_ends = []
    for word_len in word_lengths:
        end += word_len
        start_and_ends.append((start, end))
        start = end
    return start_and_ends

def read_file_to_lines(filename: str, unicode_escape=False) -> List[str]:
    if unicode_escape:
        with open(filename, 'rb') as fp:
            lines = fp.read().decode('unicode_escape').splitlines()
    else:
        with open(filename) as fp:
            lines = fp.read().splitlines()
    return lines

def write_lines_to_file(filename: str, lines: List[str]) -> None:
    with open(filename, 'w') as fp:
        for line in lines:
            fp.write(line + '\n')

def read_suisiann_csv(filename: str):
    pairs = {}
    with open(filename, 'r') as f:
        for row in csv.DictReader(f):
            wavfile = row['音檔']
            taibun = row['漢字']
            tailo = row['羅馬字']
            pairs[wavfile] = (taibun, tailo)

    return pairs

def read_suisiann_file_to_gp_pairs(filename: str):
    pairs = read_suisiann_csv(filename)
    for wavfile, (taibun, tailo) in pairs.items():
        sent_obj = Sentence.parse_singhong_sent((taibun, tailo))
        graphs, phns = Sentence.get_grapheme_phoneme_pairs(sent_obj)
        yield wavfile, graphs, phns

def generate_tsm_lexicon(lexicon_path: str,
                         grapheme_with_tone: bool = False,
                         phoneme_with_tone: bool = False):
    """
    Generate `lexicon.txt` through cartesian product of initials and finals.

    # Parameters

    lexicon_path: `str`
        The path to write lexicon to.
    grapheme_with_tone: `bool`, optional
        Set to True if grapheme needs tone.
    phoneme_with_tone: `bool`, optional
        Set to True if phoneme needs tone.

    # Returns:

        None
    """
    def generate_g2p_pair(initial, final, graph_tone, phn_tone):
        grapheme = f"{initial}{final}{graph_tone}"
        if initial:
            phoneme = f"{initial} {final}{phn_tone}"
        else:
            phoneme = f"{iNULL} {final}{phn_tone}"
        return grapheme, phoneme

    fp = open(lexicon_path, 'w')
    tones = TONES if grapheme_with_tone else [""]
    phonemes = product(臺灣閩南語羅馬字拼音聲母表,
                       臺灣閩南語羅馬字拼音韻母表,
                       tones)
    phonemes = filter(lambda triple: is_phn(triple[1], triple[2]),
                      phonemes)
    g2p_pairs = [generate_g2p_pair(initial, final, tone, tone if phoneme_with_tone else "")
                 for initial, final, tone in phonemes]

    for grapheme, phoneme in g2p_pairs:
        fp.write(f"{grapheme} {phoneme}\n")
    fp.close()

def generate_initials(initial_path):
    initials = list(map(lambda ini: ini if ini else iNULL, 臺灣閩南語羅馬字拼音聲母表))
    with open(initial_path, 'w') as fp:
        for initial in initials:
            fp.write(f"{initial}\n")

def generate_finals(final_path, phoneme_with_tone):
    finals = []
    tones = TONES if phoneme_with_tone else [""]
    finals = [(final, tone) for final, tone in product(臺灣閩南語羅馬字拼音韻母表, tones)
              if is_phn(final, tone)]
    with open(final_path, 'w') as fp:
        for final, tone in finals:
            fp.write(f"{final}{tone}\n")

def apply_tone_sandhi(hanji, lomaji, char_delimiter=分字符號, word_delimiter=分詞符號, sent_delimiter=分詞符號):

    from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
    from tsm.tone_sandhi import 台灣話口語講法

    結果句物件 = 台灣話口語講法(
        拆文分析器.建立句物件(hanji, lomaji),
        char_delimiter, word_delimiter, sent_delimiter, skip_punct,
    )
    return 結果句物件.看音(物件分字符號=char_delimiter, 物件分詞符號=word_delimiter, 物件分句符號=sent_delimiter)

def parse_args_and_preprocess(get_paths, get_tuple_from_path, data_dir_help):
    from pathlib import Path
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', help=data_dir_help)
    parser.add_argument('output_path', help='the path for the processed texts.')

    args = parser.parse_args()

    parallel_sents = [get_tuple_from_path(json_file)
                      for json_file in get_paths(Path(args.data_dir))]
    tone_sandhi_sents = [apply_tone_sandhi(hanji, lomaji) for hanji, lomaji
                         in parallel_sents]

def g2p(lexicon: Dict[str, List[str]], sentence: List[str]) -> List[List[str]]:
    phonemes = []
    words = sentence.split()
    for word in sentence.split():
        if word in lexicon:
            phonemes += lexicon[word][0]
        else:
            logging.warning(f"{word} has no entry in lexicon")
    return phonemes

def dfs_factory(backtrack):

    @lru_cache(maxsize=None)
    def dfs(idx):
        if idx > 0:
            paths = []
            for pred_idx in backtrack[idx]:
                paths += [[idx] + path for path in dfs(pred_idx)]
            return paths
        else:
            return [[0]]

    return dfs

def build_sent(sent, backtrack):
    my_dfs = dfs_factory(backtrack)
    list_cuts = my_dfs(len(sent))
    sents = []
    for cuts in list_cuts:
        cuts = list(reversed(cuts))
        words = []
        for s, e in zip(cuts[:-1], cuts[1:]):
            words.append(sent[s:e])
        sents.append(words)
    return sents

def dict_seg(sent, wordDict):
    min_cuts = [0] + [len(sent) * (idx + 1) for idx, _ in enumerate(sent)]
    backtrack = [[]] + [[idx] for idx in range(len(sent))]
    for i in range(1,len(sent)+1):
        for j in range(0, i):
            if sent[j:i] in wordDict:
                if min_cuts[j] + 1 == min_cuts[i]:
                    backtrack[i].append(j)
                elif min_cuts[j] + 1 < min_cuts[i]:
                    min_cuts[i] = min_cuts[j] + 1
                    backtrack[i] = [j]
    return build_sent(sent, backtrack)

def char2bpmf(char):
    from pypinyin import pinyin, Style
    return pinyin(char, style=Style.BOPOMOFO)[0][0]

def run_g2p():
    import argparse
    from src.dictionary import Dictionary
    parser = argparse.ArgumentParser()
    parser.add_argument('--lexicon-path')
    parser.add_argument('input_path')
    parser.add_argument('output_path')
    args = parser.parse_args()
    lexicon = Dictionary.parse_lexicon(args.lexicon_path)
    sentences = read_file_to_lines(args.input_path)
    list_of_phonemes = [" ".join(g2p(lexicon, sent)) for sent in sentences]
    write_lines_to_file(args.output_path, list_of_phonemes)

def raw_graph_to_all_graphs(raw_graph):
    raw_graph = re.sub("\(.*\)", "", raw_graph).strip() # get rid of comments in grapheme
    raw_graph = raw_graph.strip()
    raw_graph = re.sub("\s+", "", raw_graph)
    graphs = [graph.strip() for graph in re.split("、|\d\.", raw_graph)]
    return filter(lambda g: g, graphs)

def recursively_retrieve_string_in_parenthesis(string):
    substrings = []
    try:
        span = re.search(r'\((.*?)\)', string).span()
        substrings.append(string[span[0]+1:span[1]-1])
        substrings_left = recursively_retrieve_string_in_parenthesis(string[:span[0]] + string[span[1]:])
        substrings += substrings_left
    except AttributeError:
        substrings.append(string.strip())

    return substrings

def maybe_add_tone(syl_tone):
    try:
        match = re.match("([a-z]+)(\d)", syl_tone)
        syl = match.group(1)
        tone = match.group(2)
    except AttributeError:
        if re.match("[a-z]+", syl_tone):
            syl = syl_tone
            if syl_tone[-1] in "hptk":
                tone = 4
            else:
                tone = 1
        else:
            raise ValueError
    return f"{syl}{tone}"

def process_pron(pron):
    pron = pron.lower()
    pron = unicodedata.normalize("NFKC", pron)
    pron = re.sub("ı", "i", pron) # replace the dotless i to normal i
    pron = poj_tl(pron).tlt_tls().pojs_tls()
    raw_syls = filter(lambda syl: syl, re.split('[\W\-]+', pron.strip()))
    try:
        syls = list(map(maybe_add_tone, raw_syls))
        if not all([(syl in all_syls) for syl in syls]):
            raise ValueError
        return " ".join(syls)
    except ValueError:
        return None

def raw_pron_to_all_prons(raw_pron):
    raw_pron = raw_pron.strip()
    prons = re.split(r'\/', raw_pron) # some word has multiple pronunciations separated by '/'
    prons = flatten([recursively_retrieve_string_in_parenthesis(pron.strip()) for pron in prons])
    return filter(lambda pron: pron, map(process_pron, prons))

def group(objs, key):
    dictionary = defaultdict(list)
    for obj in objs:
        dictionary[key(obj)].append(obj)
    return dictionary

def get_all_possible_translations(possible_cuts, lexicon):
    return flatten([product(*[[entry.phonemes for entry in lexicon[word]] for word in cut]) for cut in possible_cuts])

def match_replace(sent, match, repl):
    start, end = match.span()
    return sent[:start] + repl + sent[end:]
