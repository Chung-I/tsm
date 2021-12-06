from 臺灣言語工具.語音合成.閩南語音韻.變調判斷 import 變調判斷
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音
from tsm.symbols import TSM_IPA_RHYME_TO_PHONE, IPA_TO_TLPA
from 臺灣言語工具.基本物件.公用變數 import 分字符號, 分詞符號, 標點符號

def 台灣話口語講法(句物件, apply_tone_sandhi=True, to_phn=True, to_TLPA=False, phn_delimiter=' '):
    if to_phn and to_TLPA:
        raise NotImplementedError('to_phn and to_TLPA cannot be True at the same time')

    結果句物件 = 句物件.轉音(臺灣閩南語羅馬字拼音, 函式='音值')
    判斷陣列 = 變調判斷.判斷(結果句物件)
    這馬所在 = 0
    for 詞物件, 原底詞 in zip(結果句物件.網出詞物件(), 句物件.網出詞物件()):
        新陣列 = []
        for 字物件, 原底字 in zip(詞物件.內底字, 原底詞.內底字):
            變調方式 = 判斷陣列[這馬所在]
            if 變調方式 == 變調判斷.愛提掉的:
                pass
            else:
                if 字物件.音 == (None,):
                    音 = f"##PUNCT{原底字.音}##PUNCT" if 原底字.音 in 標點符號 else f"##OOL{原底字.音}##OOL"
                    新陣列.append(原底字.__class__(原底字.型, 音, 原底字.輕聲標記)) # OOL = Out-of-Lexicon
                else:
                    initial, rhyme, tone = 變調方式.變調(字物件.音) if apply_tone_sandhi else 字物件.音
                    if to_TLPA:
                        initial = IPA_TO_TLPA.get(initial, initial)
                        rhyme = IPA_TO_TLPA.get(rhyme, rhyme)
                    if to_phn:
                        rhyme = TSM_IPA_RHYME_TO_PHONE[rhyme]
                    字物件.音 = phn_delimiter.join([initial, rhyme, tone])
                    # except KeyError:
                    #     print(r"rhyme: {rhyme} not found in rhyme to phone mapping for char: {initial}{rhyme}{tone}")
                    #     return None
                    新陣列.append(字物件)
            這馬所在 += 1
        詞物件.內底字 = 新陣列
    return 結果句物件
