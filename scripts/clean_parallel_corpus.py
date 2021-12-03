
import argparse
import tqdm
import re

def read_file(filename):
    datas = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            idx, content = line.split("\t")
            datas[idx] = content
    return datas

def write_file(filename, lines):
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files', nargs='+', help='input file')
    parser.add_argument('--output-files', nargs='+', help='output file')
    args = parser.parse_args()

    datas_list = [read_file(input_file) for input_file in args.input_files]
    output_sents_list = [[] for _ in args.output_files]
    num_skipped_sents = 0
    for line_num in datas_list[0].keys():
        if all([line_num in datas for datas in datas_list]):
            for i in range(len(datas_list)):
                output_sents_list[i].append(datas_list[i][line_num].strip())


    print(f"Done processing, {num_skipped_sents} sents skipped")
    for output_file, output_sents in zip(args.output_files, output_sents_list):
        write_file(output_file, output_sents)
