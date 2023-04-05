#!/bin/zsh
# Continuo não recomendando definir parâmetros de login e senha nesse arquivo...
dir=$(dirname $0)
python $dir/watch.py "$1" "$2" "$3" "$4"

# O seguinte trecho não é mais necessário (devido ao uso do subprocessing) 
# e está aqui para fins históricos:
# | ffplay -hide_banner -loglevel error -window_title "Câmera" -probesize 20000 -

