from enum import Enum
from itertools import product

臺灣閩南語羅馬字拼音聲母表 = {
    'p', 'ph', 'm', 'b',
    't', 'th', 'n', 'l',
    'k', 'kh', 'ng', 'g',
    'ts', 'tsh', 's', 'j',
    'h', '',
}
# 臺灣閩南語羅馬字拼音方案使用手冊 + 臺灣語語音入門 + 教育部辭典的字
# 歌仔戲：枝頭 ki1 thiou5， 土 thou。目前教羅共ou轉oo（因為台華辭典按呢處理）
臺灣閩南語羅馬字拼音通行韻母表 = {
    'a', 'ah', 'ap', 'at', 'ak', 'ann', 'annh',
    'am', 'an', 'ang',
    'e', 'eh', 'enn', 'ennh',
    'i', 'ih', 'ip', 'it', 'ik', 'inn', 'innh',
    'im', 'in', 'ing',
    'o', 'oh',
    'oo', 'ooh', 'op', 'ok', 'om', 'ong', 'onn', 'onnh',
    'u', 'uh', 'ut', 'un',
    'ai', 'aih', 'ainn', 'ainnh',
    'au', 'auh', 'aunn', 'aunnh',
    'ia', 'iah', 'iap', 'iat', 'iak', 'iam', 'ian', 'iang', 'iann', 'iannh',
    'io', 'ioh',
    'iok', 'iong', 'ionn',
    'iu', 'iuh', 'iut', 'iunn', 'iunnh',
    'ua', 'uah', 'uat', 'uak', 'uan', 'uann', 'uannh',
    'ue', 'ueh', 'uenn', 'uennh',
    'ui', 'uih', 'uinn', 'uinnh',
    'iau', 'iauh', 'iaunn', 'iaunnh',
    'uai', 'uaih', 'uainn', 'uainnh',
    'm', 'mh', 'ng', 'ngh',
    'ioo', 'iooh',  # 諾 0hioo 0hiooh, 詞目總檔.csv:khan35 jioo51
}
臺灣閩南語羅馬字拼音次方言韻母表 = {
    'er', 'erh', 'erm', 'ere', 'ereh',  # 泉　鍋
    'ee', 'eeh', 'uee',  # 漳　家
    'eng',
    'ir', 'irh', 'irp', 'irt', 'irk', 'irm', 'irn', 'irng', 'irinn',
    'ie',  # 鹿港偏泉腔
    'or', 'orh', 'ior', 'iorh',  # 蚵
    'uang',  # 金門偏泉腔　　風　huang1
    'oi', 'oih',  # 詞彙方言差.csv:硩⿰落去
}
臺灣閩南語羅馬字拼音韻母表 = 臺灣閩南語羅馬字拼音通行韻母表 | 臺灣閩南語羅馬字拼音次方言韻母表

iNULL = "iNULL"
TONES = list(map(str, range(1, 10)))
entering_tones = ['4', '8']
entering_tone_suffixes = "hptk"

is_phn = lambda final, tone: tone == "" or ((final[-1] in entering_tone_suffixes) == (tone in entering_tones))

is_final = lambda final: ((final[0][-1] in entering_tone_suffixes) == (final[-1] in entering_tones))

join_pair = lambda pair: "".join(pair)

all_toneless_syls = set(map(join_pair, product(臺灣閩南語羅馬字拼音聲母表, 臺灣閩南語羅馬字拼音韻母表)))
all_syls = set(map(join_pair, product(臺灣閩南語羅馬字拼音聲母表, map(join_pair, filter(is_final, product(臺灣閩南語羅馬字拼音韻母表, TONES))))))

class Stratum(Enum):
    無 = 0
    文 = 1
    白 = 2
    俗 = 3
    替 = 4

臺灣閩南語羅馬字拼音對照音值韻母表 = {
    'a': 'a', 'aʔ': 'a ʔ', 'ap': 'a p', 'at': 'a t', 'ak': 'a k',
    'am': 'a m', 'an': 'a n', 'aŋ': 'a ŋ',
    'aⁿ': 'aⁿ', 'aⁿʔ': 'aⁿ ʔ',
    'e': 'e', 'eh': 'e ʔ', 'enn': 'eⁿ', 'ennh': 'eⁿ ʔ',
    'i': 'i', 'ih': 'i ʔ', 'ip': 'i p', 'it': 'i t', 'ik': 'i k',
    'inn': 'iⁿ', 'innh': 'iⁿ ʔ',
    'im': 'i m', 'in': 'i n', 'ing': 'i ŋ',
    'o': 'ə', 'oh': 'ə ʔ',
    'oo': 'o', 'ooh': 'o ʔ', 'op': 'o p', 'ok': 'o k',
    'om': 'o m', 'ong': 'o ŋ',
    'onn': 'oⁿ', 'onnh': 'oⁿ ʔ',
    'oi': 'ə i', 'oih': 'ə i ʔ',  # ##
    'u': 'u', 'uh': 'u ʔ', 'ut': 'u t', 'un': 'u n',
    'ai': 'a i', 'aih': 'a i ʔ', 'ainn': 'aⁿ iⁿ', 'ainnh': 'aⁿ iⁿ ʔ',
    'au': 'a u', 'auh': 'a u ʔ', 'aunn': 'aⁿ uⁿ', 'aunnh': 'aⁿ uⁿ ʔ',
    'ia': 'i a', 'iah': 'i a ʔ', 'iap': 'i a p', 'iat': 'e t', 'iak': 'i a k',
    'iam': 'i a m', 'ian': 'e n', 'iang': 'i a ŋ',
    'iann': 'iⁿ aⁿ', 'iannh': 'iⁿ aⁿ ʔ',
    'io': 'i ə', 'ioh': 'i ə ʔ', 'iok': 'i o k',
    'iong': 'i o ŋ', 'ionn': 'iⁿ oⁿ',
    'iu': 'i u', 'iuh': 'i u ʔ', 'iut': 'i u t',
    'iunn': 'iⁿ uⁿ', 'iunnh': 'iⁿ uⁿ ʔ',
    'ua': 'u a', 'uah': 'u a ʔ', 'uat': 'u a t', 'uak': 'u a k',
    'uan': 'u a n', 'uann': 'uⁿ aⁿ', 'uannh': 'uⁿ aⁿ ʔ',
    'ue': 'u e', 'ueh': 'u e ʔ',
    'uenn': 'uⁿ eⁿ', 'uennh': 'uⁿ eⁿ ʔ',
    'ui': 'u i', 'uih': 'u i ʔ',
    'uinn': 'uⁿ iⁿ', 'uinnh': 'uⁿ iⁿ ʔ',
    'iau': 'i a u', 'iauh': 'i a u ʔ',
    'iaunn': 'iⁿ aⁿ uⁿ', 'iaunnh': 'iⁿ aⁿ uⁿ ʔ',
    'uai': 'u a i', 'uaih': 'u a i ʔ',
    'uainn': 'uⁿ aⁿ iⁿ', 'uainnh': 'uⁿ aⁿ iⁿ ʔ',
    'm': 'm̩', 'mh': 'm̩ ʔ',
    'ng': 'ŋ̩', 'ngh': 'ŋ̩ ʔ',
    'ioo': 'i o', 'iooh': 'i o ʔ',
    'er': 'ə', 'erh': 'ə ʔ',
    'erm': 'ə m', 'ere': 'ə e', 'ereh': 'ə e ʔ',
    'ee': 'ɛ', 'eeh': 'ɛ ʔ', 'eng': 'e ŋ', 'uee': 'u ee',
    'ir': 'ɨ', 'irh': 'ɨ ʔ', 'irp': 'ɨ p', 'irt': 'ɨ t', 'irk': 'ɨ k',
    'irm': 'ɨ m', 'irn': 'ɨ n', 'irng': 'ɨ ŋ',
    'irinn': 'ɨⁿ iⁿ',
    'ie': 'i e',
    'or': 'ə', 'orh': 'ə ʔ', 'ior': 'i ə', 'iorh': 'i ə ʔ',
    'uang': 'u a ŋ',
}

TSM_IPA_RHYME_TO_PHONE = {'a': 'a', 'aʔ': 'a ʔ', 'ap': 'a p', 'at': 'a t', 'ak': 'a k',
    'am': 'a m', 'an': 'a n', 'aŋ': 'a ŋ', 'aⁿ': 'aⁿ', 'aⁿʔ': 'aⁿ ʔ',
    'e': 'e', 'eʔ': 'e ʔ', 'eⁿ': 'eⁿ', 'eⁿʔ': 'eⁿ ʔ',
    'i': 'i', 'iʔ': 'i ʔ', 'ip': 'i p', 'it': 'i t', 'ik': 'i k',
    'iⁿ': 'iⁿ', 'iⁿʔ': 'iⁿ ʔ', 'im': 'i m', 'in': 'i n', 'iŋ': 'i ŋ',
    'ə': 'ə', 'əʔ': 'ə ʔ', 'o': 'o', 'oʔ': 'o ʔ', 'op': 'o p', 'ok': 'o k', 'om': 'o m', 'oŋ': 'o ŋ', 
    'oⁿ': 'oⁿ', 'oⁿʔ': 'oⁿ ʔ', 'əi': 'ə i', 'əiʔ': 'ə i ʔ',
    'u': 'u', 'uʔ': 'u ʔ', 'ut': 'u t', 'un': 'u n',
    'ai': 'a i', 'aiʔ': 'a i ʔ', 'aⁿiⁿ': 'aⁿ iⁿ', 'aⁿiⁿʔ': 'aⁿ iⁿ ʔ', 
    'au': 'a u', 'auʔ': 'a u ʔ', 'aⁿuⁿ': 'aⁿ uⁿ', 'aⁿuⁿʔ': 'aⁿ uⁿ ʔ',
    'ia': 'i a', 'iaʔ': 'i a ʔ', 'iap': 'i a p',
    'iet': 'e t', 'iak': 'i a k', 'iam': 'i a m', 'ien': 'e n',
    'iaŋ': 'i a ŋ', 'iⁿaⁿ': 'iⁿ aⁿ', 'iⁿaⁿʔ': 'iⁿ aⁿ ʔ',
    'iə': 'i ə', 'iəʔ': 'i ə ʔ', 'iok': 'i o k', 'ioŋ': 'i o ŋ', 'iⁿoⁿ': 'iⁿ oⁿ',
    'iu': 'i u', 'iuʔ': 'i u ʔ', 'iut': 'i u t', 'iⁿuⁿ': 'iⁿ uⁿ', 'iⁿuⁿʔ': 'iⁿ uⁿ ʔ',
    'ua': 'u a', 'uaʔ': 'u a ʔ', 'uat': 'u a t', 'uak': 'u a k', 'uan': 'u a n', 'uⁿaⁿ': 'uⁿ aⁿ', 'uⁿaⁿʔ': 'uⁿ aⁿ ʔ',
    'ue': 'u e', 'ueʔ': 'u e ʔ', 'uⁿeⁿ': 'uⁿ eⁿ', 'uⁿeⁿʔ': 'uⁿ eⁿ ʔ', 'ui': 'u i', 'uiʔ': 'u i ʔ', 'uⁿiⁿ': 'uⁿ iⁿ', 'uⁿiⁿʔ': 'uⁿ iⁿ ʔ',
    'iau': 'i a u', 'iauʔ': 'i a u ʔ', 'iⁿaⁿuⁿ': 'iⁿ aⁿ uⁿ', 'iⁿaⁿuⁿʔ': 'iⁿ aⁿ uⁿ ʔ',
    'uai': 'u a i', 'uaiʔ': 'u a i ʔ', 'uⁿaⁿiⁿ': 'uⁿ aⁿ iⁿ', 'uⁿaⁿiⁿʔ': 'uⁿ aⁿ iⁿ ʔ',
    'm̩': 'm̩', 'm̩ʔ': 'm̩ ʔ', 'ŋ̩': 'ŋ̩', 'ŋ̩ʔ': 'ŋ̩ ʔ', 'io': 'i o', 'ioʔ': 'i o ʔ', 'əm': 'ə m', 'əe': 'ə e', 'əeʔ': 'ə e ʔ',
    'ɛ': 'ɛ', 'ɛʔ': 'ɛ ʔ', 'eŋ': 'e ŋ', 'uee': 'u ee',
    'ɨ': 'ɨ', 'ɨʔ': 'ɨ ʔ', 'ɨp': 'ɨ p', 'ɨt': 'ɨ t', 'ɨk': 'ɨ k', 'ɨm': 'ɨ m', 'ɨn': 'ɨ n', 'ɨŋ': 'ɨ ŋ',
    'ɨⁿiⁿ': 'ɨⁿ iⁿ', 'ie': 'i e', 'uaŋ': 'u a ŋ'
}

TSM_TLPA_RHYME_TO_PHONE = {'a': 'a', 'ah': 'a h', 'ap': 'a p', 'at': 'a t', 'ak': 'a k',
    'am': 'a m', 'an': 'a n', 'ang': 'a ng', 'ann': 'a nn', 'annh': 'a nn h',
    'e': 'e', 'eh': 'e h', 'enn': 'e nn', 'ennh': 'e nn h',
    'i': 'i', 'ih': 'i h', 'ip': 'i p', 'it': 'i t', 'ik': 'i k',
    'inn': 'i nn', 'innh': 'i nn h', 'im': 'i m', 'in': 'i n', 'ing': 'i ng',
    'er': 'er', 'erh': 'er h', 'o': 'o', 'oh': 'o h', 'op': 'o p', 'ok': 'o k', 'om': 'o m', 'ong': 'o ng', 
    'onn': 'o nn', 'onnh': 'o nn h',
    'u': 'u', 'uh': 'u h', 'ut': 'u t', 'un': 'u n',
    'ai': 'a i', 'aih': 'a i h', 'ainn': 'a i nn', 'ainnh': 'a i nn h', 
    'au': 'a u', 'auh': 'a u h', 'aunn': 'a u nn', 'aunnh': 'a u nn h',
    'ia': 'i a', 'iah': 'i a h', 'iap': 'i a p',
    'iet': 'e t', 'iak': 'i a k', 'iam': 'i a m', 'ien': 'e n',
    'iang': 'i a ng', 'iann': 'i a nn', 'iannh': 'i a nn h',
    'io': 'i o', 'ioh': 'i o h', 'iok': 'i o k', 'iong': 'i o ŋ', 'ionn': 'i o nn',
    'iu': 'i u', 'iuh': 'i u h', 'iut': 'i u t', 'iunn': 'i u nn', 'iunnh': 'i u nn h',
    'ua': 'u a', 'uah': 'u a h', 'uat': 'u a t', 'uak': 'u a k', 'uan': 'u a n', 'uann': 'u a nn', 'uannh': 'u a nn h',
    'ue': 'u e', 'ueh': 'u e h', 'uenn': 'u e nn', 'uennh': 'u e nn h', 'ui': 'u i', 'uih': 'u i h', 'uinn': 'u i nn', 'uinnh': 'u i nn h',
    'iau': 'i a u', 'iauh': 'i a u h', 'iⁿaⁿuⁿ': 'i a u nn', 'iaunnh': 'i a u nn h',
    'uai': 'u a i', 'uaih': 'u a i h', 'uainn': 'u a i nn', 'uainnh': 'u a i nn h',
    'm': 'm', 'mh': 'm h', 'ng': 'ng', 'ngh': 'ng h', 'erm': 'er m', 'ere': 'er e', 'ereh': 'er e h',
    'ee': 'ee', 'eeh': 'ee h', 'eng': 'e ng', 'uee': 'u ee',
    'ir': 'ir', 'irh': 'ir h', 'irp': 'ir p', 'irt': 'ir t', 'irk': 'ir k', 'irm': 'ir m', 'irn': 'ir n', 'irng': 'ir ng',
    'irnn': 'ir nn', 'ie': 'i e', 'uang': 'u a ng'
}

TSM_IPA_TO_ARPABET = {
    'b': 'B', 'oⁿ': 'AO NN', 's': 'S', 'ŋ̩': 'NG', 'dz': 'DZ', 'k': 'KK', 'n': 'N', 'a': 'AA', 'l': 'L', 'iⁿ': 'IY NN',
    'ɨⁿ': 'IH NN', 'ɛ': 'EH', 'u': 'UW', 'i': 'IY', 'o': 'AO', 't': 'TT', 'tsʰ': 'TSH', 'ə': 'AX', 'ŋ': 'NG', 'g': 'G',
    'ʔ': 'Q', 'eⁿ': 'EH NN', 'ɨ': 'IH', 'uⁿ': 'UW NN', 'aⁿ': 'AA NN', 'p': 'PP', 'm̩': 'M', 'm': 'M', 'kʰ': 'KKH',
    'ts': 'TS', 'tʰ': 'TTH', 'h': 'HH', 'pʰ': 'PPH', 'e': 'EH', 'ee': 'EH', 
}

TSM_TLPA_TO_ARPABET = {
    'i': 'IY', 'g': 'G', 'kh': 'KH', 'k': 'K', 'l': 'L', 'p': 'P', 'a': 'AA', 'nn': 'NN', 's': 'S', 'n': 'N', 'ee': 'EH',
    'o': 'AO', 'j': 'DZ', 'b': 'B', 'ts': 'Z', 'tsh': 'TS', 'th': 'TH', 'u': 'UW', 'er': 'ER', 'ng': 'NG', 'e': 'EH', 't': 'T', 'm': 'M', 'h': 'HH', 'ir': 'IH', 'ph': 'PH',
}

TSM_TONE_TO_FIVE_LEVEL_TONE = {
    '1': '55', '2': '51', '3':'21', '4': '21', '5': '24', '7': '33', '8': '53', '9': '24', '10': '21',
}
# TSM_TLPA_RHYME_TO_PHONE = {'a': 'AA', 'ah': 'AA Q', 'ap': 'AA P', 'at': 'AA T', 'ak': 'AA K',
#     'am': 'AA M', 'an': 'AA N', 'ang': 'AA NG', 'ann': 'A NN', 'annh': 'A NN Q',
#     'e': 'EH', 'eh': 'EH Q', 'enn': 'E NN', 'ennh': 'E NN Q',
#     'i': 'IY', 'ih': 'IH Q', 'ip': 'IH P', 'it': 'IH T', 'ik': 'IH K',
#     'inn': 'IY NN', 'innh': 'IY NN Q', 'im': 'IY M', 'in': 'IY N', 'ing': 'IY NG',
#     'er': 'ER', 'erh': 'ER Q', 'o': 'AX', 'oh': 'AX Q', 'op': 'AO P', 'ok': 'AO K', 'om': 'AO M', 'ong': 'AO NG', 
#     'onn': 'AO NN', 'onnh': 'o nn h',
#     'u': 'u', 'uh': 'u h', 'ut': 'u t', 'un': 'u n',
#     'ai': 'a i', 'aih': 'a i h', 'ainn': 'a i nn', 'ainnh': 'a i nn h', 
#     'au': 'a u', 'auh': 'a u h', 'aunn': 'a u nn', 'aunnh': 'a u nn h',
#     'ia': 'i a', 'iah': 'i a h', 'iap': 'i a p',
#     'iet': 'e t', 'iak': 'i a k', 'iam': 'i a m', 'ien': 'e n',
#     'iang': 'i a ng', 'iann': 'i a nn', 'iannh': 'i a nn h',
#     'io': 'i o', 'ioh': 'i o h', 'iok': 'i o k', 'iong': 'i o ŋ', 'ionn': 'i o nn',
#     'iu': 'i u', 'iuh': 'i u h', 'iut': 'i u t', 'iunn': 'i u nn', 'iunnh': 'i u nn h',
#     'ua': 'u a', 'uah': 'u a h', 'uat': 'u a t', 'uak': 'u a k', 'uan': 'u a n', 'uann': 'u a nn', 'uannh': 'u a nn h',
#     'ue': 'u e', 'ueh': 'u e h', 'uenn': 'u e nn', 'uennh': 'u e nn h', 'ui': 'u i', 'uih': 'u i h', 'uinn': 'u i nn', 'uinnh': 'u i nn h',
#     'iau': 'i a u', 'iauh': 'i a u h', 'iⁿaⁿuⁿ': 'i a u nn', 'iaunnh': 'i a u nn h',
#     'uai': 'u a i', 'uaih': 'u a i h', 'uainn': 'u a i nn', 'uainnh': 'u a i nn h',
#     'm': 'mm', 'mh': 'm h', 'ng': 'ng', 'ngh': 'ng h', 'erm': 'er m', 'ere': 'er e', 'ereh': 'er e h',
#     'ee': 'ee', 'eeh': 'ee h', 'eng': 'e ng', 'uee': 'u ee',
#     'ir': 'ir', 'irh': 'ir h', 'irp': 'ir p', 'irt': 'ir t', 'irk': 'ir k', 'irm': 'ir m', 'irn': 'ir n', 'irŋ': 'ir ŋ',
#     'irnn': 'ir nn', 'ie': 'i e', 'uang': 'u a ng'
# }
