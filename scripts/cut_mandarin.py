from minibert_tokenizer import BertNerTokenizer
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process moe file.')

    parser.add_argument('input_file', help='Input file.')
    parser.add_argument('output_file', help='Output file.')
    parser.add_argument('--minibert-tokenizer-dir', required=True)
    args = parser.parse_args()
    tokenizer = BertNerTokenizer(args.minibert_tokenizer_dir)
    print("done loading tokenizer")

    with open(args.input_file, 'r') as f:
        lines = f.read().splitlines()
        tokenized = tokenizer.cut(lines)
        cutted_sents = [[x.surface for x in tokens] for tokens in tokenized]

    with open(args.output_file, 'w') as f:
        for cutted_sent in cutted_sents:
            text = " ".join(cutted_sent)
            f.write(f"{text}\n")
