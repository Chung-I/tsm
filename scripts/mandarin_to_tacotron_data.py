from typing import List
import argparse
import json
import re

from pypinyin import pinyin, lazy_pinyin, Style

from tsm.util import cumsum
from tsm.symbols import MANDARIN_TONE_TO_FIVE_LEVEL_TONE

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

def word_lengths_to_boundary(word_lengths: List[int]) -> List[bool]:
    """
    Convert word length to boundary.
    """
    boundaries = [False] * sum(word_lengths)

    for cum_len in cumsum(word_lengths):
        boundaries[cum_len-1] = True
    return boundaries

def separate_pinyin_from_tone(syllable):
    match = re.match(r"([a-z]+)(\d)?", syllable.lower())
    try:
        base_syllable = match.group(1)
        tone = match.group(2)
        if tone is None:
            tone = "5"
    except AttributeError:
        raise ValueError("syllable {} is not in the format of 'base_syllable[tone]'".format(syllable))
    tone = MANDARIN_TONE_TO_FIVE_LEVEL_TONE[tone]
    return base_syllable, tone

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str,
                        help="input pipe delimited text file. format: <file_prefix>|<grapheme>|<pinyin>")
    parser.add_argument("output_file", type=str)
    parser.add_argument("--speaker", type=str, default="jarvis")
    parser.add_argument("--pinyin-ipa-mapping-file", type=str, default='tsm/pinyin2ipa.json')
    parser.add_argument("--infer", action='store_true')
    parser.add_argument("--remove-punct", action='store_true')
    parser.add_argument("--path-prefix", type=str)
    args = parser.parse_args()

    if not args.infer and not args.path_prefix:
        raise ValueError("path_prefix must be provided if not in infer mode")

    with open(args.pinyin_ipa_mapping_file) as fp:
        pinyin2ipa = json.load(fp)

    speaker_id = SPEAKERS[args.speaker]
    style_id = STYLES["neutral"]
    with open(args.input_file) as fp:
        with open(args.output_file, 'w') as fp_out:
            for line in fp:
                line = line.strip()
                fields = line.split('|')
                if len(fields) == 2:
                    file_prefix, sent = fields
                    pinyins = " ".join(lazy_pinyin(sent, style=Style.TONE3, neutral_tone_with_five=True))
                else:
                    file_prefix, sent, pinyins = fields
                words = sent.split()
                word_boundary = word_lengths_to_boundary(list(map(len, words)))
                units = []
                lang_codes: List[int] = []
                word_lang_codes: List[str] = []
                for idx, pinyin in enumerate(pinyins.split()):
                    if not re.match(r"[a-z]+(\d)?", pinyin):
                        if args.remove_punct:
                            continue
                        else:
                            units.append("sp")
                            lang_codes.append(LANGS["#P"])
                            word_lang_codes.append("#P")
                    pinyin, tone = separate_pinyin_from_tone(pinyin)
                    ipa = pinyin2ipa[pinyin]
                    units += list(ipa)
                    lang_codes += [LANGS["ZH"]] * len(ipa)
                    units.append(tone)
                    lang_codes.append(LANGS["ZH"])
                    if word_boundary[idx]:
                        units.append('#E')
                        lang_codes.append(LANGS["#P"])
                        word_lang_codes.append("ZH")
                transcript = " ".join(units)
                if args.infer:
                    lang_text = " ".join(word_lang_codes)
                    fp_out.write(f"{file_prefix}|{transcript}|{lang_text}\n")
                else:
                    lang_text = " ".join(map(str, lang_codes))
                    feat_file = f"{args.path_prefix}/{file_prefix}.wav.s16.f32"
                    fp_out.write(f"{feat_file}|{speaker_id}|{style_id}|{transcript}|{lang_text}\n")

