EXP_HOME_DIR="/volume/asr-share-experiments/chungyili"
MINIBERT_TOKENIZER_DIR="/volume/translation-data-nfs/zh-en-data/checkpoints/tokenizer/distill"
NLTK_DATA_PATH="$EXP_HOME_DIR/nltk_data"
MOSES_BIN_DIR="/opt/moses/bin/moses"
SRC_TO_TGT_MODEL_DIR="$EXP_HOME_DIR/moses_model/tai_man/less_char_model-phrase-mslr-bidirectional-fe/model/moses.ini"
SRC_TO_PHN_MODEL_DIR="$EXP_HOME_DIR/moses_model/taibun_tailo/no_tgb_model/model/moses.ini"
SUISIANN_FILE="/volume/tts/tai/meta_files/SuiSiann.csv"
TACOTRON_DATA="$EXP_HOME_DIR/tacotron_data"
OUTPUT_DIR="$TACOTRON_DATA/cs-16k-tai-betterts-raw"
LEXICON_DIR="$EXP_HOME_DIR/lexicons"
SRC_FILE=$1
mkdir -p $OUTPUT_DIR

python scripts/prepare_tone_sandhi_data.py --minibert-tokenizer-dir $MINIBERT_TOKENIZER_DIR \
    --nltk-data-path $NLTK_DATA_PATH \
    --moses-bin-dir $MOSES_BIN_DIR \
    --src-to-tgt-model-dir $SRC_TO_TGT_MODEL_DIR \
    --src-to-phn-model-dir $SRC_TO_PHN_MODEL_DIR \
    $SRC_FILE $OUTPUT_DIR/wav.txt $OUTPUT_DIR/taibun.txt $OUTPUT_DIR/tailo.txt $OUTPUT_DIR/mandarin.txt $OUTPUT_DIR/alignment.txt $OUTPUT_DIR/mandain_tree.txt

python scripts/apply_tone_sandhi.py $OUTPUT_DIR/taibun.txt $OUTPUT_DIR/tailo.txt $OUTPUT_DIR/alignment.txt $OUTPUT_DIR/mandarin_tree.txt
python scripts/to_tacotron_data.py $OUTPUT_DIR/ts_suisiann.csv $TACOTRON_DATA/cs-16k-tai-betterts --dicts $LEXICON_DIR/suisiann_dict.txt $LEXICON_DIR/cmudict-ascii --infer