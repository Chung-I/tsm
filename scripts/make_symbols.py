import argparse
import json
from itertools import chain

from tsm.symbols import TSM_TONE_TO_FIVE_LEVEL_TONE, MANDARIN_TONE_TO_FIVE_LEVEL_TONE

def make_symbol_to_id(symbols):
    symbol_to_id = {}
    idx = 0
    for symbol in symbols:
        symbol_to_id[symbol] = idx
        idx += 1
    return symbol_to_id

def write_json(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()

    ipas = set()
    with open(args.input_file) as fp:
        for line in fp:
            line = line.strip()
            phns = line.split("|")[3]
            ipas.update(phns.split())

pad = "_"
special_token = {
    "endofword": "#E",
    "endofsent": "#S",
    "attribute_pad": "#P",
    "shortpause": "sp",
}
tones = set(chain(TSM_TONE_TO_FIVE_LEVEL_TONE.values(), MANDARIN_TONE_TO_FIVE_LEVEL_TONE.values()))
ipas = ipas - set(special_token.values()) - tones
_tone = ["@" + str(s) for s in tones]
_ipa = ["@" + s for s in ipas]
_special_token = ["@" + s for s in special_token.values()]
# Export all symbols:
SYMBOLS = (
    [pad]
    # + list(_punctuation)
    + _ipa
    # + _pinyin
    # + _silences
    +  _tone
    + _special_token
)


symbol_to_id = make_symbol_to_id(SYMBOLS)
write_json(args.output_file, symbol_to_id)
