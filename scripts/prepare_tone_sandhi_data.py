import csv
import subprocess
from pathlib import Path

import re
import nltk
import benepar
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音

from tsm.sentence import Sentence
from tsm.util import file_exists_and_not_empty
from minibert_tokenizer import BertNerTokenizer

def read_csv(path):
    pairs = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            wavfile = row['音檔']
            taibun = row['漢字']
            tailo = row.get('羅馬字', None)
            pairs[wavfile] = (taibun, tailo)

    return pairs

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process moe file.')

    parser.add_argument('input_file', help='Input file.')
    parser.add_argument('wav_output_file', help='Wav Output file.')
    parser.add_argument('src_output_file', help='Source(Taibun) Output file.')
    parser.add_argument('phn_output_file', help='Phn(Tailo) Output file.')
    parser.add_argument('tgt_output_file', help='Target(Mandarin) Output file.')
    parser.add_argument('tgt_ali_file', help='Target(Mandarin) Alignment Output file.')
    parser.add_argument('tgt_tree_output_file', help='Target(Mandarin) Syntax Tree Output file.')
    parser.add_argument('tgt_ner_tag_output_file', help='Target(Mandarin) named entity tags Output file.')
    parser.add_argument('--minibert-tokenizer-dir', required=True)
    parser.add_argument('--nltk-data-path', required=True)
    parser.add_argument('--moses-bin', required=True)
    parser.add_argument('--src-to-phn-model-dir')
    parser.add_argument('--src-to-tgt-model-dir')
    parser.add_argument('--stage', type=int, default=0)
    parser.add_argument('--moses-threads', type=int, default=16)

    args = parser.parse_args()

    pairs = read_csv(args.input_file)

    if args.stage < 1:
        if next(iter(pairs.values()))[1] is None:
            print("tailo field is None; inferring pronunciation using moses smt model")
            fo_wav = open(args.wav_output_file, 'w')
            fo_src = open(args.src_output_file, 'w')
            for wavfile, (taibun, _) in pairs.items():
                chars = Sentence.parse_mixed_text(taibun)
                fo_src.write(" ".join(chars) + "\n")
                fo_wav.write(wavfile + "\n")
            fo_wav.close()
            fo_src.close()

            fi_src = open(args.src_output_file)
            if args.src_to_phn_model_dir:
                fo_phn = open(args.phn_output_file, 'w')
                print("inferring pronunciation using moses smt model")
                subprocess.run([args.moses_bin, '-threads', str(args.moses_threads), '-dl', '0', '-f', args.src_to_phn_model_dir], stdin=fi_src, stdout=fo_phn)
                fo_phn.close()
            elif not file_exists_and_not_empty(args.phn_output_file):
                raise ValueError("Either --phn-output-file is not empty or --src-to-phn-model-dir must be specified.")
            fi_src.close()
        else:
            fo_wav = open(args.wav_output_file, 'w')
            fo_src = open(args.src_output_file, 'w')
            fo_phn = open(args.phn_output_file, 'w')
            for wavfile, (taibun, tailo) in pairs.items():
                try:
                    sent_obj = Sentence.parse_singhong_sent((taibun, tailo))
                    graphs, phns = Sentence.get_grapheme_phoneme_pairs(sent_obj, remove_punct=False)
                    fo_src.write(graphs + '\n')
                    fo_phn.write(phns + '\n')
                    fo_wav.write(wavfile + '\n')
                except:
                    print(taibun, tailo)
            fo_wav.close()
            fo_src.close()
            fo_phn.close()

    if args.stage < 2:
        fo_tgt = open(args.tgt_output_file, 'w')
        fo_ali = open(args.tgt_ali_file, 'w')
        with open(args.src_output_file) as fo_src:
            print("running moses")
            with subprocess.Popen([args.moses_bin, '-threads', str(args.moses_threads), '-print-alignment-info', '-f', args.src_to_tgt_model_dir],
                                stdin=fo_src, stdout=subprocess.PIPE) as process:
                for line in process.stdout:
                    line = line.decode('utf-8')
                    tgt_out, ali = line[:-1].split("|||")
                    fo_tgt.write(tgt_out + "\n")
                    fo_ali.write(ali + "\n")
        fo_tgt.close()
        fo_ali.close()

    if args.stage < 3:
        nltk.data.path.append(args.nltk_data_path)
        print("loading parser and tokenizer")
        nl_parser = benepar.Parser("benepar_zh2")
        print("done loading parser")
        tokenizer = BertNerTokenizer(args.minibert_tokenizer_dir)
        print("done loading tokenizer")

        with open(args.tgt_output_file, 'r') as f:
            lines = f.read().splitlines()
            tokenized = tokenizer.cut(list(map(lambda line: re.sub(r' ([\u4e00-\u9ffff]) ', r'\1', line), lines)))
            cutted_sents = [benepar.InputSentence(words=[x.surface for x in tokens]) for tokens in tokenized]
            ner_tagged_sents = [[x.ner_tag for x in tokens] for tokens in tokenized]
            parsed_sents = nl_parser.parse_sents(cutted_sents)

        with open(args.tgt_ner_tag_output_file, 'w') as fp:
            for ner_tags in ner_tagged_sents:
                ner_tags = ["_" if tag is None else tag for tag in ner_tags]
                fp.write(" ".join(ner_tags) + "\n")

        fo_tgt_tree = open(args.tgt_tree_output_file, 'w')
        for wavfile, parsed_sent in zip(pairs, parsed_sents):
            fo_tgt_tree.write(re.sub(r'\s+', ' ', str(parsed_sent)) + "\n")
        fo_tgt_tree.close()
