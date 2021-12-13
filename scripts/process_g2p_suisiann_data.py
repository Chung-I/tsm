import csv

from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音

from tsm.sentence import Sentence
from tsm.util import read_suisiann_csv

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process moe file.')

    parser.add_argument('input_file', help='Input file.')
    parser.add_argument('output_prefix', help='Output file.')
    parser.add_argument('--src', default='taibun')
    parser.add_argument('--tgt', default='tailo')

    args = parser.parse_args()

    pairs = read_suisiann_csv(args.input_file)

    fo_src = open(args.output_prefix + '.' + args.src, 'w')
    fo_tgt = open(args.output_prefix + '.' + args.tgt, 'w')

    for wavfile, (taibun, tailo) in pairs.items():
        sent_obj = Sentence.parse_singhong_sent((taibun, tailo))
        graphs, phns = Sentence.get_grapheme_phoneme_pairs(sent_obj)
        fo_src.write(graphs + '\n')
        fo_tgt.write(phns + '\n')

    fo_src.close()
    fo_tgt.close()
