#!/bin/python3
"""
Author: Diego Silva <github.com/diegovgsilva95>
Description: 
    (pt-br) Monitoramento em tempo real de câmeras IP chinesas SOFIA usando FFPLAY/FFMPEG.
    (en) Real-time monitoring of SOFIA chinese IP cameras using FFPLAY/FFMPEG.
Keywords: dvr, nvr, sofia, ip camera, ffmpeg, ffplay, hevc, h265
""" 
#region Importações
import sys
import os
import shlex
import subprocess
import io
from dvrip import DVRIPCam, SomethingIsWrongWithCamera
from time import sleep, time
from watch_utils import printerr
from watch_video import consume_video, clean_video, init_video
from watch_audio import consume_audio, clean_audio, init_audio
#endregion
#region Constantes
MONITOR_MAX_DURATION = 120 # segundos
STREAM_NAME = "Extra"
globalData = type("", (), {})() # Forma esquisita de fazer o mesmo que um new class{}() do Javascript
#endregion
#region Define variáveis globais e função de monitoramento
monitoring_since = time()

def handleMonitor(frame, meta, user_data):
    global monitoring_since
    if monitoring_since is None:
        printerr("Não era para essa função estar sendo chamada.")

    printerr("Recebendo frames...")

    fn = None
    if frame is None:
        printerr(f"Frame vazio, verifique metadados: {meta}")
    elif ("type" in meta) and (meta["type"] == "g711a"): # Frame possui áudio s8 a-law 8kHz
        fn = consume_audio
    else: # Frame provavelmente possui vídeo HEVC 
        fn = consume_video
        
    if callable(fn):
        try:
            fn(frame, meta)
        except Exception as e:
            printerr("Houve um erro em um dos consumidores. Por precaução, parando monitoramento...")
            printerr("O erro detalhado será armazenado e virá a seguir...")
            monitoring_since = None
            globalData.consumerError = e
            cam.stop_monitor()

    if (monitoring_since is not None) and (time() - monitoring_since >= MONITOR_MAX_DURATION):
        printerr(f"Parando monitoramento após {MONITOR_MAX_DURATION} segundos.")
        cam.stop_monitor()
#endregion
if __name__ != "__main__":
    printerr(f"[{os.path.basename(__file__)}] Esse módulo espera ser invocado diretamente via Python. Saindo.")
else:
    #region Interpretar os parâmetros (IP da câmera, usuário e senha)
    cam_args = sys.argv[1:]
    try:
        cam_ip = cam_args[0]
        cam_user = cam_args[1]
        cam_pw = "" # ... e nem aqui.
        if len(cam_args) == 3:
            cam_pw = cam_args[2]

    except Exception as e:
        printerr("Alguns parâmetros são obrigatórios.")
        printerr(f"Chamada:\n\t./{os.path.basename(__file__)} <IP da câmera> <Usuário> [senha]")
        exit(1)
    #endregion
    try:
        #region Conecta com a câmera...
        cam = DVRIPCam(cam_ip, user=cam_user, password=cam_pw)
        # cam.debug()
        if not cam.login():
            printerr(f"Falha ao conectar com a câmera {cam_ip}")
            exit(1)
        #endregion
        #region Obtém informações da câmera
        globalData.cam_info = cam.get_system_info()
        globalData.cam_model = globalData.cam_info.get('DeviceModel')
        globalData.cam_serial = globalData.cam_info.get('SerialNo')
        globalData.cam_hw = globalData.cam_info.get('HardWare')

        printerr(f"Conectado à {globalData.cam_model} {globalData.cam_hw} ({globalData.cam_serial}) em {cam.proto}://{cam.ip}:{cam.port}")
        #endregion
        #region Inicializa o compartilhamento de escopo para consumidores de áudio e de vídeo...
        init_video(globalData)
        init_audio(globalData)
        #endregion
        #region Iniciando monitoramento...
        printerr(f"Requisitando modo de monitoramento...")
        cam.start_monitor(handleMonitor, stream=STREAM_NAME)
        monitoring_since = time()
        #endregion
        #region Finalizando a câmera e consumidores...
        printerr(f"Fechando a câmera...")
        cam.close()
        printerr(f"Encerrando FFMPEG...")
        clean_video()
        clean_audio()
        #endregion
        #region Levantando eventuais erros anteriores para debugging...
        if "consumerError" in dir(globalData):
            printerr("Houve um erro no último consumo. Disparando para eventual debug.")
            raise globalData.consumerError
        #endregion
        printerr("Fim do programa")
    #region Tratamento de erros
    # Erros específicos (como SomethingIsWrongWithCamera) foram removidos, por hora.
    except Exception as e:
        curr_traceback = e.__traceback__
        curr_traceback_index = 0
        err_stack = []

        while curr_traceback is not None:
            frame = curr_traceback.tb_frame
            fn_name = frame.f_code.co_name
            if fn_name == "<module>":
                fn_name = "escopo principal"
            else:
                fn_name = f"função '{fn_name}'"

            err_stack.append(f"\t{frame.f_code.co_filename}:{curr_traceback.tb_lineno}, {fn_name}")
            
            curr_traceback_index = curr_traceback_index + 1
            if curr_traceback_index > 20:
                break
            curr_traceback = curr_traceback.tb_next

        printerr("Erro genérico:", repr(e))
        printerr("\n".join(err_stack))
    #endregion