from typing import Dict, List, Any, Union, Tuple
import json
import unicodedata
import regex as re
import zhon.hanzi
import cn2an
import opencc

from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.基本物件.公用變數 import 標點符號
from 臺灣言語工具.基本物件.句 import 句
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音

converter = opencc.OpenCC('s2tw.json')


class Sentence:
    word_segmenter_cache: dict = {}
    @staticmethod
    def from_line(line: str, remove_punct: bool = True,
                  form: str = 'char', pos_tagged: bool = False,
                  normalize: bool = True):
        assert form in ['char', 'word', 'sent']
        if pos_tagged:
            if remove_punct:
                # remove words that are punctuation mark (PM)
                line = re.sub("\s\S+_PM\s", " ", line)
            line = re.sub("_\S+\s", " ", line)

        if normalize:
            line = Sentence.normalize(line)

        if form in ['char', 'word']:
            words = line.split()
        elif form == 'sent':
            words = list(line)
        else:
            raise NotImplementedError

        if remove_punct:
            words = list(filter(lambda w: w, [re.sub("[^\P{P}-]+", "", word.strip()).strip() for word in words]))

        return words

    @staticmethod
    def an2cn(line, mode='direct'):
        return re.sub(r'(\d+)', lambda x: cn2an.an2cn(x.group(), mode=mode), line)

    @staticmethod
    def normalize(line: str):
        line = unicodedata.normalize("NFKC", line)
        line = cn2an.transform(line, "an2cn")
        line = converter.convert(line)
        return line

    @staticmethod
    def cut(sent):
        if "ckip" not in Sentence.word_segmenter_cache:
            from tsm.ckip_wrapper import CKIPWordSegWrapper
            Sentence.word_segmenter_cache["ckip"] = CKIPWordSegWrapper('/home/nlpmaster/ssd-1t/weights/data')
        sent = re.sub("\s+", "", sent)
        return Sentence.word_segmenter_cache["ckip"].cut(sent)

    @staticmethod
    def parse_mixed_text(mixed_text, remove_punct=False, char_level=True):
        zh_suffix = "" if char_level else "+"
        if remove_punct:
            return [match.group() for match in re.finditer(f"[{zhon.hanzi.characters}]{zh_suffix}|([^{zhon.hanzi.characters}\W]\')+", mixed_text)]
        else:
            return [match.group() for match in re.finditer(f"[{zhon.hanzi.characters}]{zh_suffix}|([^{zhon.hanzi.characters}\W]|\')+|\p{{P}}+", mixed_text)]

    @staticmethod
    def parse_singhong_sent(sent: Union[str, Tuple[str, str]], to_numbered_tone_mark=True):
        if isinstance(sent, str):
            taibun, tailo = map(lambda words: " ".join(words), zip(*[word.split('｜') for word in sent.split()]))
        else:
            taibun, tailo = sent
        sent_obj = 拆文分析器.建立句物件(taibun, tailo)
        return sent_obj

    @staticmethod
    def parse_mixed_taibun_tailo(mixed_sent: str, cutted=True):
        if not cutted:
            mixed_sent = re.sub(f"([{zhon.hanzi.characters}])", r" \1 ", mixed_sent)
        sent_obj = 拆文分析器.建立句物件(mixed_sent)
        return sent_obj

    @staticmethod
    def parse_tailo(tailo: str):
        sent_obj = 拆文分析器.建立句物件(tailo, tailo)
        return sent_obj

    @staticmethod
    def process_singhong_sent(sent_obj, output_type='char', remove_punct=True, to_numbered_tone_mark=True):
        if to_numbered_tone_mark:
            sent_obj = sent_obj.轉音(臺灣閩南語羅馬字拼音, 函式="轉換到臺灣閩南語羅馬字拼音")
        tailo_char_delimiter = ' ' if output_type == 'char' else '-'
        taibun_char_delimiter = ' ' if output_type == 'char' else ''
        def stringify(word, show_type="看型"):
            chars = ""
            for idx, char in enumerate(word.篩出字物件()):
                text = getattr(char, show_type)()
                prefix = ""
                if idx > 0:
                    if re.match("\w+\d", text):
                        prefix = tailo_char_delimiter
                    else:
                        prefix = taibun_char_delimiter
                chars += prefix + text
            return chars

        words = [word for word in sent_obj.網出詞物件()]
        if remove_punct:
            words = list(filter(lambda x: x.看型() not in 標點符號, words))

        _words = [stringify(word, "看型") for word in words]
        _phns = [stringify(word, "看音") for word in words]
        return _words, _phns

    @staticmethod
    def get_grapheme_phoneme_pairs(sent_obj: 句, remove_punct=True, remove_neutral_tone_mark=True):
        graphs = sent_obj.看型(物件分字符號=' ', 物件分詞符號=' ', 物件分句符號=' ').strip().split()
        phns = sent_obj.看音(物件分字符號=' ', 物件分詞符號=' ', 物件分句符號=' ').strip().split()
        try:
            if remove_punct:
                graphs, phns = zip(*filter(lambda pairs: all(map(lambda unit: unit not in 標點符號, pairs)), zip(graphs, phns)))
            if remove_neutral_tone_mark:
                graphs, phns = zip(*map(lambda pairs: map(lambda unit: re.sub(r"--(\S+)", r"\1", unit), pairs), zip(graphs, phns)))
        except ValueError as e:
            print(f"get_grapheme_phoneme_pairs: ValueError from {graphs} {phns}", e)

        return " ".join(graphs), " ".join(phns)


#class TaibunSentence(Sentence):
#    @staticmethod
#    def from_line(line: str, remove_punct: bool = True,
#                  form: str = 'char'):
#        assert form in ['char', 'word', 'sent']
#        if form in ['char', 'word']:
#            words = line.split()
#        elif form == 'sent':
#            words = list(line)
#        else:
#            raise NotImplementedError

class ParallelSentence(list):
    """

    Parallel sentence.

    # Parameters

    sent_of_langs : `Dict[str, str]`
        A dictionary storing language as key and corresponding sentence string as value.
    metadata: `Dict[str, Any]`
        A dictionary storing other metadata describing the sentence, e.g. source, speaker, etc.
    """
    def __init__(self, sent_of_langs: Dict[str, str], metadata: Dict[str, Any]):
        self.metadata = metadata
        super(ParallelSentence, self).__init__(sent_of_langs)

    @classmethod
    def from_json(cls, json_file: str, langs: List[str],
                  metadata_fields: List[str]):
        with open(json_file) as fp:
            raw_sent = json.load(fp)

        sent_of_langs = {lang: raw_sent[lang] for lang in langs}
        metadata = {field: raw_sent[field] for field in metadata_fields}

        return cls(sent_of_langs, metadata)

    @staticmethod
    def from_json_to_tuple(json_file: str, mandarin_key: str, taigi_key: str):
                           #cut_mandarin: bool = False,
                           #normalize_mandarin: bool = False,
                           #preprocess_taigi: bool = True):

        with open(json_file) as fp:
            raw_sent = json.load(fp)
        mandarin = raw_sent[mandarin_key]
        taigi = raw_sent[taigi_key]
        #if cut_mandarin:
        #    mandarin_words = Sentence.cut(mandarin)
        #    mandarin = " ".join(mandarin_words)
        #if normalize_mandarin:
        #    mandarin_words = Sentence.from_line(mandarin, form='word')
        #    mandarin = " ".join(mandarin_words)
        #if preprocess_taigi:
        #    taigi_words = ParallelSentence.parse_taigi(taigi)
        #    taigi = " ".join(taigi_words)

        return (mandarin, taigi)

    @staticmethod
    def parse_taigi(taigi):
        #remove alternative pronunciations annotated in brackets, e.g. teh4(leh4) -> teh4
        taigi = re.sub("\([A-Za-z\d\s]+\)", "", taigi)
        #remove alternative pronunciations annotated with slashes, e.g. teh4/leh4 -> teh4
        taigi = re.sub("(\/[A-Za-z]+\d)+", "", taigi)
        words = []
        for word in re.finditer("[A-Za-z]+\d", taigi):
            words.append(word.group())
        return words


