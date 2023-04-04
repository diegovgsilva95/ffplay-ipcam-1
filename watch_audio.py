"""
Author: Diego Silva <github.com/diegovgsilva95>
Description: 
    (pt-br) Consumidor de áudio para monitoramento em tempo real de câmeras IP chinesas SOFIA usando FFPLAY/FFMPEG.
    (en) Audio consumer for real-time monitoring of SOFIA chinese IP cameras using FFPLAY/FFMPEG.
""" 
#region Importações
import sys
import os
import shlex
import subprocess
import io
from watch_utils import printerr
from time import sleep, time
#endregion
#region Definições de variáveis e constantes
FFMPEG_GLOBAL_ARGS = "-probesize 32 -loglevel error -nodisp -window_title \"{window_title}\""
FFMPEG_CMD = f"ffplay {FFMPEG_GLOBAL_ARGS} -f s8 -ar 8000 -acodec pcm_alaw -"
ffmpeg_proc = None
globalData = None
#endregion

def init_audio(actualGlobalData):
    """ Recebe e armazena a classe comum para compartilhamento de informações entre módulos """
    global globalData
    globalData = actualGlobalData

def initFFMPEGAudio():
    """ Inicializa o subprocesso do FFMPEG """
    global ffmpeg_proc
    printerr("[Áudio] Inicializando FFMPEG...")
    FFMPEG_FULL_CMD = FFMPEG_CMD.format(window_title=f"{globalData.cam_model} {globalData.cam_hw} ({globalData.cam_serial})")
    ffmpeg_proc = subprocess.Popen(shlex.split(FFMPEG_FULL_CMD), stdout=sys.stdout, stdin=subprocess.PIPE, stderr=sys.stderr)

def consume_audio(frame, meta):
    """ Para cada frame de áudio a-law recebido, redireciona-o ao subprocesso FFMPEG para reprodução, conversão ou streaming """
    if ffmpeg_proc is None:
        initFFMPEGAudio()
    
    printerr(f"[Áudio] Escrevendo {len(frame)} bytes ao ffmpeg... Dados: {meta}")
    if ffmpeg_proc.poll() is None:
        ffmpeg_proc.stdin.write(frame)


def clean_audio():
    """ Finaliza graciosamente o subprocesso FFMPEG ao término do programa """
    if ffmpeg_proc is not None:
        ffmpeg_proc.stdin.close()
        ffmpeg_proc.kill()
