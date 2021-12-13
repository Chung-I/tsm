import argparse
from itertools import islice
from tqdm import tqdm
import logging
import json
import re
from json.decoder import JSONDecodeError
from http.server import BaseHTTPRequestHandler, HTTPServer

import nltk
import benepar
import zhon.hanzi

from tsm.clients import MosesClient
from tsm.sentence import Sentence

zh_char = f"[{zhon.hanzi.punctuation}]|[{zhon.hanzi.characters}]"

class Tokenizer:
    def __init__(self, ckpt_folder):
        from minibert_tokenizer import BertNerTokenizer
        self.tokenizer = BertNerTokenizer(ckpt_folder)

    def tokenize(self, sents):
        tokenized = self.tokenizer.cut(sents)
        tokenized_surfaces = [[x.surface for x in tokens] for tokens in tokenized]
        return tokenized_surfaces


class TaigiServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data)
        try:
            src_sent = json.loads(post_data)['sentence']
            src_char_sent = " ".join(Sentence.parse_mixed_text(src_sent))
            translation_result = client.translate(src_char_sent)
            alignment = [(align['source-word'], align['target-word']) for align in translation_result['word-align']]
            tgt_char_sent = translation_result['text']
            tgt_sent = re.sub(f" ?({zh_char}) ?", r"\1", tgt_char_sent)
            tgt_tokens = cutter.tokenize([tgt_sent])[0]
            benepar_tgt_sent = benepar.InputSentence(words=tgt_tokens)
            tgt_tree = nl_parser.parse(benepar_tgt_sent)
            self._set_response()
            self.wfile.write(json.dumps({"source": src_char_sent, "target": tgt_char_sent, "tree": str(tgt_tree), "alignment": alignment}).encode('utf-8'))
        except JSONDecodeError:
            print(f"cannot read post_data {post_data}")
            self.send_response(400)
            self.send_header('Content-type', 'text/json')
            self.end_headers()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt-path')
    parser.add_argument('--host-name')
    parser.add_argument('--nltk-data-path', default='~/nltk_data')
    parser.add_argument('--port', default="8081")
    args = parser.parse_args()

    global cutter, client, nl_parser
    nltk.data.path.append(args.nltk_data_path)
    nl_parser = benepar.Parser("benepar_zh2")
    client = MosesClient(config={})
    print("done loading parser")
    cutter = Tokenizer(args.ckpt_path)
    print("done initializing word segmentation module")
    webServer = HTTPServer((args.host_name, int(args.port)), TaigiServer)
    webServer.serve_forever()
    print(f"serving at {args.host_name}:{args.port}")
