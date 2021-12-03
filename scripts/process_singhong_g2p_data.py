from tsm.sentence import Sentence
import re
from 臺灣言語工具.解析整理.解析錯誤 import 解析錯誤

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process moe file.')

    parser.add_argument('input_file', help='Input file.')
    parser.add_argument('output_prefix', help='Output file.')
    parser.add_argument('--src', default='taibun')
    parser.add_argument('--tgt', default='tailo')

    args = parser.parse_args()

    fo_src = open(args.output_prefix + '.' + args.src, 'w')
    fo_tgt = open(args.output_prefix + '.' + args.tgt, 'w')
    n_skipped = 0


    with open(args.input_file, 'r', encoding='utf-8') as fi:
        for line in fi:
            try:
                sent_obj = Sentence.parse_singhong_sent(line.strip())
                graphs, phns = Sentence.get_grapheme_phoneme_pairs(sent_obj)
                phns = re.sub(r"\d(\w+\d)", r"\1", phns)
                fo_src.write(graphs + '\n')
                fo_tgt.write(phns + '\n')
            except (解析錯誤, ValueError) as e:
                #print(f"cannot process line: {line.strip()}; skipped")
                n_skipped += 1

    print(f"processing finished; skipped {n_skipped} lines")
    fo_src.close()
    fo_tgt.close()
