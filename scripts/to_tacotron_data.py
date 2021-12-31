import argparse
import csv
from os import replace
import re
import tqdm
from pathlib import Path
import json
import itertools

from 臺灣言語工具.基本物件.公用變數 import 標點符號

from tsm.util import flatten
from tsm.symbols import TSM_IPA_TO_ARPABET, TSM_TONE_TO_FIVE_LEVEL_TONE

LANGS = {
    "#P": 0, # punctuation
    "TAI": 1,
    "EN": 2,
    "ZH": 3,
}

STYLES = {
    "#P": 0,
    "neutral": 1,
}

SPEAKERS = {
    "tai": 0,
    "jarvis": 1,
}

pad = "_"

special_token = {
    "endofword": "#E",
    "endofsent": "#S",
    "attribute_pad": "#P",
    "shortpause": "sp",
}

ARPABET = {
    'OW', 'IH', 'T', 'N', 'TH', 'OY', 'R', 'ER', 'P', 'UH', 'L', 'Q', 'AE', 'DH', 'EH', 'AA',
    'S', 'CH', 'J', 'SH', 'AH', 'IY', 'EY', 'W', 'AO', 'Z', 'G', 'AW', 'X', 'F', 'V', 'JH', 'M',
    'ZH', 'NG', 'K', 'AY', 'HH', 'UW', 'Y', 'D', 'B'
}

_tone = ["@" + str(s) for s in set(TSM_TONE_TO_FIVE_LEVEL_TONE.values())]
_arpabet = ["@" + s for s in set(itertools.chain(*[phns.split() for phns in TSM_IPA_TO_ARPABET.values()])).union(ARPABET)]
_special_token = ["@" + s for s in special_token.values()]
# Export all symbols:
SYMBOLS = (
    [pad]
    # + list(_punctuation)
    + _arpabet
    # + _pinyin
    # + _silences
    +  _tone
    + _special_token
)

def read_csv(path):
    pairs = {}
    with open(path, 'r') as f:
        for row in csv.DictReader(f):
            wavfile = row['音檔']
            hanji = row['漢字']
            lomaji = row['羅馬字']
            pairs[wavfile] = (hanji, lomaji)

    return pairs

def write_csv(path, datas, infer=False):
    with open(path, 'w') as f:
        writer = csv.writer(f, delimiter='|')
        for data in datas:
            if infer:
                wavfile, transcript, lang_code = data
                wavfile = Path(wavfile).stem
                writer.writerow([str(wavfile), transcript, lang_code])
            else:
                wavfile, speaker, style,  transcript, lang_code = data
                wavfile = Path("/volume/tts/tai/feature_16k/bfcc/") / Path(wavfile).with_suffix(".f32").name
                writer.writerow([str(wavfile), speaker, style, transcript, lang_code])

def read_dict(path, encoding="utf-8", ipa=False):
    lexicon = {}
    
    with open(path, encoding=encoding) as f:
        for line in f:
            if line.startswith(';;;'): # skip cmudict header
                continue
            words = re.split("\s+", line)
            word = words[0].lower()
            pron = " ".join(words[1:]).strip()
            if ipa:
                pron = re.sub(r"[ˌˈ]+", "", pron)
                pron = " ".join(pron)
            lexicon[word] = pron
    return lexicon

def write_dict(lexicon, path):
    with open(path, 'w') as f:
        for word, pron in lexicon.items():
            f.write(f"{word} {pron}\n")

def merge_dict(dicts):
    merged = {}
    for d in dicts:
        for word, pron in d.items():
            merged[word] = pron
    return merged

def list_level_join(list_of_lists, delimiter, keep_last_delimiter=True):
    new_lst = []
    for lst in list_of_lists:
        new_lst += lst
        new_lst.append(delimiter)

    if not keep_last_delimiter:
        new_lst = new_lst[:-1]
    return new_lst

def postprocess_text(foreign_dict, sent, short_pause="sp", word_delimiter="#E", output_type='arpabet', remove_stress=True,
                     remove_punct=False):
    out_of_lexicon_words = set()
    def process_foreign_word(match):
        form = match.group(1)
        if form.lower() in foreign_dict:
            pron = foreign_dict[form.lower()]
            if remove_stress:
                pron = re.sub(r'\d', '', pron)
            char_phns = pron.split()
            return char_phns
        else:
            print(f"{form} not found in foreign dict")
            out_of_lexicon_words.add(form)
            return []

    word_level_lang_codes = []
    word_level_phns = []
    words = sent.網出詞物件()
    for idx, word in enumerate(words):
        form = word.看音()
        phns = []
        if re.match("##PUNCT(.*?)##PUNCT", form):
            if not args.remove_punct:
                phns.append(short_pause)
                word_level_lang_codes.append("#P")
        elif re.match(r"##OOL(.*?)##OOL", form):
            match = re.match(r"##OOL(.*?)##OOL", form)
            char_phns = process_foreign_word(match)
            phns += char_phns
            word_level_lang_codes.append("EN")
        else:
            for character in word.篩出字物件():
                pron = character.音
                match = re.match(r"##OOL(.*?)##OOL", pron)
                if match:
                    char_phns = process_foreign_word(match)
                    phns += char_phns
                else:
                    for phn in pron.split(" "):
                        if re.match("[^\d]+", phn):
                            try:
                                if output_type == 'ipa' and not re.match("##PUNCT(.*?)##PUNCT", phn):
                                    phns += list(filter(lambda x: x != 'ʔ', phn))
                                else:
                                    raw_phn = TSM_IPA_TO_ARPABET[phn]
                                    if len(raw_phn):
                                        phns += raw_phn.split()
                            except KeyError:
                                print(sent.看型())
                                print(f"|{form}| {phn} not found in TSM_IPA_TO_ARPABET")
                        elif re.match("\d+", phn):
                            phns.append(TSM_TONE_TO_FIVE_LEVEL_TONE[phn])
                        else:
                            print(f"Unknown phoneme: {phn}")
            word_level_lang_codes.append("TAI")
        if phns:
            word_level_phns.append(phns)

    phns = list_level_join(word_level_phns, word_delimiter)
    phn_level_lang_codes = list_level_join([[lang_code] * len(phns) for phns, lang_code in zip(word_level_phns, word_level_lang_codes)], "#P")
    phn_text = " ".join(phns)
    assert len(phn_text.split()) == len(" ".join(phn_level_lang_codes).split())
    return phn_text, phn_level_lang_codes, word_level_lang_codes, out_of_lexicon_words

def text_to_phn(text):
    text = " ".join(text)
    #text = re.sub(r'\s+([\u207f\u02b0]+)', r'\1', text)
    return text

def prep(text):
    text = re.sub(r"……", r"...", text)
    return text

def parse_taigi(hanji, lomaji, char_delimiter=" #C ", word_delimiter=" #E ", sent_delimiter=" #S "):

    from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
    from tsm.tone_sandhi import 台灣話口語講法
    結果句物件 = 台灣話口語講法(
        拆文分析器.建立句物件(hanji, lomaji),
        apply_tone_sandhi=False,
    )
    return 結果句物件 #.看音(物件分字符號=char_delimiter, 物件分詞符號=word_delimiter, 物件分句符號=sent_delimiter)

def write_json(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f)

def make_symbol_to_id():
    symbol_to_id = {}
    idx = 0
    for symbol in SYMBOLS:
        symbol_to_id[symbol] = idx
        idx += 1
    return symbol_to_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_dir')
    parser.add_argument('--dicts', nargs='+')
    parser.add_argument('--ool-file')
    parser.add_argument('--infer', action='store_true')
    parser.add_argument('--ipa', action='store_true')
    parser.add_argument('--remove-punct', action='store_true')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    pairs = read_csv(args.input_file)
    dicts = [read_dict(dictionary, ipa=args.ipa) for dictionary in args.dicts]
    foreign_dict = merge_dict(dicts)
    all_ool_words = set()

    datas = []
    for wav, (hanji, lomaji) in tqdm.tqdm(pairs.items()):
        text = parse_taigi(hanji, lomaji)
        text, phn_level_lang_codes, word_level_lang_codes, ool_words = \
            postprocess_text(foreign_dict, text, output_type='ipa' if args.ipa else 'arpabet',
                             remove_punct=args.remove_punct)
        #assert all(map(lambda phn: '@' + phn in SYMBOLS, text.split()))
        all_ool_words.update(ool_words)
        if args.infer:
            data = [wav, text, " ".join(word_level_lang_codes)]
        else:
            data = [wav, SPEAKERS["tai"], STYLES["neutral"], text, " ".join([str(LANGS[lang_code]) for lang_code in phn_level_lang_codes])]
        datas.append(data)

    if args.infer:
        write_csv(output_dir / "infer.txt", datas, infer=True)
    else:
        attributes = {"speakers": SPEAKERS, "styles": STYLES, "languages": LANGS}
        write_json(output_dir / "attributes.json", attributes)
        symbol_to_id = make_symbol_to_id()
        #write_json(output_dir / "symbols.json", symbol_to_id)
        write_csv(output_dir / "train.txt", datas)

    if args.ool_file:
        with open(args.ool_file, 'w') as f:
            for word in all_ool_words:
                f.write(f"{word}\n")
