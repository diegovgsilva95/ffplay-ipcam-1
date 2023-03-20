#!/bin/zsh
# Não recomendo definir parâmetros de login e senha nesse arquivo...
dir=$(dirname $0)
python $dir/watch.py $1 $2 $3 | ffplay -hide_banner -loglevel error -window_title "Câmera" -probesize 20000 -
