from typing import List, Tuple

from nltk import Tree
import tqdm
import csv
import re

from tsm.g2p import ToneSandhiG2P
from tsm.chinese_head_finder import ChineseSemanticHeadFinder
from tsm.util import alignment_to_tgt2src
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('src_file')
    parser.add_argument('phn_file')
    parser.add_argument('ali_file')
    parser.add_argument('tgt_tree_file')
    parser.add_argument('wav_file')
    parser.add_argument('out_file')
    args = parser.parse_args()

    fi_src = open(args.src_file)
    fi_phn = open(args.phn_file)
    fi_ali = open(args.ali_file)
    fi_tgt = open(args.tgt_tree_file)
    fi_wav = open(args.wav_file)
    head_finder = ChineseSemanticHeadFinder()
    g2p = ToneSandhiG2P(head_finder)
    fo = open(args.out_file, 'w')
    writer = csv.writer(fo, quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(["音檔", "漢字", "羅馬字"])
    for wavfile, src_text, phn_text, alignment_str, tgt_tree_str in tqdm.tqdm(zip(fi_wav, fi_src, fi_phn, fi_ali, fi_tgt)):
        wavfile = wavfile.strip()
        src_text = src_text.strip()
        phn_text = phn_text.strip()
        alignment_str = alignment_str.strip()
        tgt_tree_str = tgt_tree_str.strip()
        tgt_tree = Tree.fromstring(tgt_tree_str)
        alignment: List[Tuple[int, int]] = [tuple(int(x) for x in a.split('-')) for a in alignment_str.split()]
        tgt_to_src = alignment_to_tgt2src(alignment)
        try:
            graphs, phns = g2p.run(src_text, phn_text, tgt_tree, tgt_to_src)
            writer.writerow([wavfile, ' '.join(graphs), ' '.join(phns)])
        except:
            print(f"skip {src_text} {phn_text}")
    fo.close()

