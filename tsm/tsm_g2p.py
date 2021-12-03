from nltk.grammar import Nonterminal
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.翻譯.摩西工具.摩西用戶端 import 摩西用戶端
from 臺灣言語工具.翻譯.摩西工具.語句編碼器 import 語句編碼器
from 臺灣言語工具.語音合成 import 台灣話口語講法
import docker
import time
from tsm.dummy_segmenter import DummySegmenter
import itertools

import requests
import sys
import nltk
from nltk.tree import Tree, ParentedTree
import logging

LEXICAL_PHRASE = {
    'N', 'V', 'A', 'P'
}

logger = logging.getLogger(__name__)

def init():
    '''
    cmd = "docker run --name huatai -p 8080:8080 -d --rm i3thuan5/hokbu-le:huatai"
    '''
    client = docker.from_env()
    if not client.containers.list(filters={"name":"huatai"}):
        client.containers.run("i3thuan5/hokbu-le:huatai", 
                                name="huatai",
                                ports={'8080/tcp': 8080},
                                detach=True,
                                auto_remove=True)    

def translate(text, seg=False):
    #華語句物件 = 拆文分析器.建立句物件(text)
    if seg:
        from tsm.ckip_segmenter import CKIPSegmenter
        華語斷詞句物件 = CKIPSegmenter.斷詞(text)
    else:
        華語斷詞句物件 = DummySegmenter.斷詞(text)
    台語句物件, 華語新結構句物件, 分數 = (摩西用戶端(位址='localhost', 編碼器=語句編碼器).翻譯分析(華語斷詞句物件))
    口語講法 = 台灣話口語講法(台語句物件)
    return 華語斷詞句物件, 台語句物件, 口語講法

def lexify(obj):
    if isinstance(obj, Tree):
        return " ".join(obj.leaves())
    return obj

def find_right_boundary_preterminal(root, pos):
    right_boundary_pos = pos + (len(root[pos])-1,)
    if isinstance(root[right_boundary_pos], Tree):
        return find_right_boundary_preterminal(root, right_boundary_pos)
    else:
        return right_boundary_pos

def infer_sandhi_boundary(root: ParentedTree, phrase_is_lexically_governed):

    boundary_positions = set()
    for pos in phrase_is_lexically_governed:
        if root[pos].label().endswith('P') and not phrase_is_lexically_governed[pos]:
            right_boundary_pos = find_right_boundary_preterminal(root, pos)
            boundary_positions.add(right_boundary_pos)

    boundaries = []
    for pos in root.treepositions():
        if not isinstance(root[pos], Tree):
            if pos in boundary_positions:
                boundaries.append(True)
            else:
                boundaries.append(False)

    return boundaries

def lexical_government(root: ParentedTree):
    "Determine if phrase_a is phrase_b's lexical head"
    phrase_is_lexically_governed = {subtree.treeposition(): False for subtree in root.subtrees()}
    for pos in root.treepositions():
        if not isinstance(root[pos], Tree) or root[pos].parent() is None: # skip root and leaves
            continue
        if root[pos].parent().label().startswith(root[pos].label()[0]): # subt is the lexical head of the parent phrase
            parent_index = root[pos].parent_index()
            for sibling_index in filter(lambda idx: idx != parent_index, range(0, len(root[pos].parent()))):
                sibling_pos = pos[:-1] + (sibling_index,)
                phrase_is_lexically_governed[sibling_pos] = True
                logger.info(f"{lexify(root[sibling_pos])} is lexically governed by {lexify(root[sibling_pos])}")

    return phrase_is_lexically_governed


def g2p(sent, parser_url, g2p_url):
    res = requests.post(parser_url, json={"sentence": " ".join(list(sent))})
    obj = res.json()
    tree_str = obj['tree']
    alignment = obj['alignment']
    src_tokens = obj["source"].split()
    tgt_tokens = obj["target"].split()
    align_info = " ".join(f"{src_tokens[align[0]]}-{tgt_tokens[align[1]]}" for align in alignment)
    tree = Tree.fromstring(tree_str)

    
if __name__ == "__main__":
    from util import read_file_to_lines, write_lines_to_file
    init()
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
    sent_of_phonemes = []
    fp = open(args.output_path, 'w')
    for sent in sents:
        g2p(sent, args.parser_url, args.g2p_url)
    
