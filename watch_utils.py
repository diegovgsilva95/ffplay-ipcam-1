"""
Author: Diego Silva <github.com/diegovgsilva95>
Description: 
    (pt-br) Módulo de utilitários para monitoramento em tempo real de câmeras IP chinesas SOFIA usando FFPLAY/FFMPEG.
    (en) Util module for real-time monitoring of SOFIA chinese IP cameras using FFPLAY/FFMPEG.
""" 
import sys

def printerr(*args):
    """ 
    Apenas um alias para o print para não ter que ficar 
    repetindo file=sys.stderr a cada impressão de texto no STDERR 
    """
    print(*args, file=sys.stderr)
