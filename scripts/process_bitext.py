import argparse
import tqdm
import re

from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器

def from_sentence(main_sent, pron_sent=None, output_type='char'):
    結果句物件 = 拆文分析器.建立句物件(main_sent, pron_sent)
    char_delimiter = ' ' if output_type == 'char' else ''
    return 結果句物件.看型(物件分字符號=char_delimiter, 物件分詞符號=' ', 物件分句符號=' ')

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            yield re.match(r"\d+\.\d+ \d+\.\d+ (.*)", line).group(1).split('\t')

def write_file(filename, lines):
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input file')
    parser.add_argument('--output-files', nargs='+', help='output files')
    parser.add_argument('--output-type', choices=['char', 'word'], default='char', help='output granularity')
    args = parser.parse_args()

    sents = read_file(args.input_file)
    output_sents_list = [[], []]
    for taigi, mandarin in tqdm.tqdm(sents):
        output_sent_tai = from_sentence(taigi, None, args.output_type)
        output_sent_man = from_sentence(mandarin, None, args.output_type)
        if (not output_sent_tai.strip()) or (not output_sent_man.strip()):
            print("empty sentence; skipped")
            continue
        output_sents_list[0].append(output_sent_tai)
        output_sents_list[1].append(output_sent_man)

    for output_file, output_sents in zip(args.output_files, output_sents_list):
        write_file(output_file, output_sents)
