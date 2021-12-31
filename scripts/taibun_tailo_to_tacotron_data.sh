EXP_HOME_DIR="/volume/asr-share-experiments/chungyili"
MINIBERT_TOKENIZER_DIR="/volume/translation-data-nfs/zh-en-data/checkpoints/tokenizer/distill"
NLTK_DATA_PATH="$EXP_HOME_DIR/nltk_data"
MOSES_BIN="/opt/moses/bin/moses"
SRC_TO_TGT_MODEL_DIR="$EXP_HOME_DIR/moses_model/tai_man/less_char_model-phrase-mslr-bidirectional-fe/model/moses.ini"
TACOTRON_DATA="$EXP_HOME_DIR/tacotron_data"
tone_sandhi_opts=
to_tacotron_opts=
LEXICON_DIR="$EXP_HOME_DIR/lexicons"
cmudict=$LEXICON_DIR/cmudict-ascii
stage=0

. scripts/parse_options.sh || exit 1;

SRC_FILE=$1
OUTPUT_STEM=$2
OUTPUT_DIR="$TACOTRON_DATA/$OUTPUT_STEM"

 
if [[ $stage -le 0 ]];
then
  mkdir -p $OUTPUT_DIR
  
  python scripts/prepare_tone_sandhi_data.py --minibert-tokenizer-dir $MINIBERT_TOKENIZER_DIR \
      --nltk-data-path $NLTK_DATA_PATH \
      --moses-bin $MOSES_BIN \
      --src-to-tgt-model-dir $SRC_TO_TGT_MODEL_DIR \
      --stage 0 \
      $SRC_FILE $OUTPUT_DIR/wav.txt $OUTPUT_DIR/taibun.txt $OUTPUT_DIR/tailo.txt $OUTPUT_DIR/mandarin.txt $OUTPUT_DIR/alignment.txt $OUTPUT_DIR/mandarin_tree.txt || exit 1;
fi

if [[ $stage -le 1 ]];
then
  python scripts/run_g2p.py $OUTPUT_DIR/taibun.txt $OUTPUT_DIR/tailo.txt $OUTPUT_DIR/alignment.txt $OUTPUT_DIR/mandarin_tree.txt $OUTPUT_DIR/wav.txt $OUTPUT_DIR/data.csv $tone_sandhi_opts || exit 1;
fi

if [[ $stagae -le 2 ]];
then
  python scripts/to_tacotron_data.py $OUTPUT_DIR/data.csv $OUTPUT_DIR --dicts $cmudict  $to_tacotron_opts || exit 1;
  #python scripts/to_tacotron_data.py $OUTPUT_DIR/data.csv $OUTPUT_DIR --dicts $LEXICON_DIR/suisiann_dict.txt  $to_tacotron_opts || exit 1;
fi
