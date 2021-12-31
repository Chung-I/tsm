EXP_HOME_DIR="/volume/asr-share-experiments/chungyili"
MINIBERT_TOKENIZER_DIR="/volume/translation-data-nfs/zh-en-data/checkpoints/tokenizer/distill"
NLTK_DATA_PATH="$EXP_HOME_DIR/nltk_data"
MOSES_BIN="/opt/moses/bin/moses"
SRC_TO_TGT_MODEL_DIR="$EXP_HOME_DIR/moses_model/tai_man/less_char_model-phrase-mslr-bidirectional-fe/model/moses.ini"
SRC_TO_PHN_MODEL_DIR="$EXP_HOME_DIR/moses_model/taibun_tailo/no_tgb_model/model/moses.ini"
TACOTRON_DATA="$EXP_HOME_DIR/tacotron_data"
LEXICON_DIR="$EXP_HOME_DIR/lexicons"
tone_sandhi_opts=
to_tacotron_opts=
raw_text=false
cmudict=$LEXICON_DIR/CMU.in.IPA.txt
stage=0

. scripts/parse_options.sh

SRC_FILE=$1
OUTPUT_STEM=$2
OUTPUT_DIR=$OUTPUT_STEM

if [[ $stage -le 0 ]];
then
  mkdir -p $OUTPUT_DIR
  if [[ $raw_text == "true" ]];
  then
    awk -F',' 'NR>0{$0=NR-1".wav,"$0} 1' $SRC_FILE > $SRC_FILE.tmp
    sed '1 i\音檔,漢字' $SRC_FILE.tmp > $SRC_FILE.csv
    SRC_FILE=$SRC_FILE.csv
    echo $SRC_FILE
  fi

  python scripts/prepare_tone_sandhi_data.py --minibert-tokenizer-dir $MINIBERT_TOKENIZER_DIR \
      --nltk-data-path $NLTK_DATA_PATH \
      --moses-bin $MOSES_BIN \
      --src-to-tgt-model-dir $SRC_TO_TGT_MODEL_DIR \
      --src-to-phn-model-dir $SRC_TO_PHN_MODEL_DIR \
      --stage 0 \
      $SRC_FILE $OUTPUT_DIR/wav.txt $OUTPUT_DIR/taibun.txt $OUTPUT_DIR/tailo.txt $OUTPUT_DIR/mandarin.txt $OUTPUT_DIR/alignment.txt $OUTPUT_DIR/mandarin_tree.txt || exit 1;
fi

if [[ $stage -le 1 ]];
then
  python scripts/run_g2p.py $OUTPUT_DIR/taibun.txt $OUTPUT_DIR/tailo.txt $OUTPUT_DIR/alignment.txt $OUTPUT_DIR/mandarin_tree.txt $OUTPUT_DIR/wav.txt $OUTPUT_DIR/data.csv $tone_sandhi_opts || exit 1;
fi

if [[ $stage -le 2 ]];
then
  python scripts/to_tacotron_data.py $OUTPUT_DIR/data.csv $OUTPUT_DIR --dicts $cmudict  $to_tacotron_opts || exit 1;
  #python scripts/to_tacotron_data.py $OUTPUT_DIR/data.csv $OUTPUT_DIR --dicts $LEXICON_DIR/suisiann_dict.txt $LEXICON_DIR/cmudict-ascii $infer_opts || exit 1;
fi
