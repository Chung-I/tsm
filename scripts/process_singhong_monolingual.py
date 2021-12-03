
import argparse
import tqdm
import re

from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.基本物件.公用變數 import 標點符號
from 臺灣言語工具.解析整理.解析錯誤 import 解析錯誤

def from_graph_phn_pair(main_sent, pron_sent=None, output_type='char', remove_punct=False):
    結果句物件 = 拆文分析器.建立句物件(main_sent, pron_sent)
    char_delimiter = ' ' if output_type == 'char' else ''
    words = 結果句物件.看型(物件分字符號=char_delimiter, 物件分詞符號=' ', 物件分句符號=' ').strip().split()
    if remove_punct:
        words = filter(lambda x: x not in 標點符號, words)
    return " ".join(words)


def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

def write_file(filename, lines):
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input file')
    parser.add_argument('output_file', help='output file')
    parser.add_argument('--output-type', choices=['char', 'word'], default='char', help='output granularity')
    parser.add_argument('--language', choices=['taibun-tailo', 'taibun', 'tailo', 'mandarin'], default='taigi', help='language')
    parser.add_argument('--add-linenum', action='store_true', help='add line number')
    parser.add_argument('--remove-punct', action='store_true', help='remove punctuation')
    args = parser.parse_args()

    sents = read_file(args.input_file)
    output_sents = []
    num_skipped_sents = 0
    for idx, sent in enumerate(tqdm.tqdm(sents)):
        try:
            if args.language == 'taibun-tailo':
                taibun, tailo = map(lambda words: " ".join(words), zip(*[word.split('｜') for word in sent.split()]))
                output_sent = from_graph_phn_pair(taibun, tailo, args.output_type, args.remove_punct)
            else:
                output_sent = from_graph_phn_pair(sent, None, args.output_type, args.remove_punct)
            if args.add_linenum:
                output_sent = str(idx) + "\t" + output_sent
            output_sents.append(output_sent)
        except (解析錯誤, ValueError) as e:
            print("Sentence skipped:" + sent)
            num_skipped_sents += 1

    print(f"Done processing, {num_skipped_sents} sents skipped")
    write_file(args.output_file, output_sents)
