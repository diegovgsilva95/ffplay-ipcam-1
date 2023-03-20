import sys
import os
from dvrip import DVRIPCam, SomethingIsWrongWithCamera
from time import sleep

# TODO: 
# `socat - UDP-RECV:34569` recebe um JSON { "NetWork.NetCommon" ... } 
# com as informações da câmera da rede, sem a necessidade de informar um IP
# pois a câmera fica constantemente fazendo broadcast de suas informações
# na rede.
# Ainda haverá necessidade de informar login e senha, e isso é feito através 
# dos parâmetros

cam_args = sys.argv[1:]
try:
    cam_ip = cam_args[0]
    cam_user = cam_args[1]
    cam_pw = "" # ... e nem aqui.
    if len(cam_args) == 3:
        cam_pw = cam_args[2]

except Exception as e:
    print("Alguns parâmetros são obrigatórios.", file=sys.stderr)
    print("Chamada:\n\t./watch.py <IP da câmera> <Usuário> [senha]", file=sys.stderr)
    print("Erro: ", repr(e), file=sys.stderr)
    exit(1)

cam = None
try:
    cam = DVRIPCam(cam_ip, user=cam_user, password=cam_pw)

    if not cam.login():
        print(f"Falha ao conectar com a câmera {cam_ip}", file=sys.stderr)
        exit(1)

    cam_info = cam.get_system_info()
    cam_model = cam_info.get('DeviceModel')
    cam_serial = cam_info.get('SerialNo')
    cam_hw = cam_info.get('HardWare')

    print(f"Conectado à {cam_model} {cam_hw} ({cam_serial}) em {cam.proto}://{cam.ip}:{cam.port}", file=sys.stderr)
    print(f"Requisitando modo de monitoramento...", file=sys.stderr)

    cam.start_monitor(lambda frame, meta, user: sys.stdout.buffer.write(frame))
    cam.close()

except SomethingIsWrongWithCamera as e:
    if str(e) == 'Cannot connect to camera':
        print('Falha ao conectar com a câmera. Verifique a conexão.', file=sys.stderr)
    else:
        print("Algo ocorreu com a câmera: ", str(e), file=sys.stderr)

except SystemExit:
    if not (cam is None):
        print('O programa está saindo. Fechando conexão com a câmera...', file=sys.stderr)
        cam.stop_monitor()
        cam.close()
        exit(0)

except KeyboardInterrupt:
    if not (cam is None):
        print('O programa está saindo. Fechando conexão com a câmera...', file=sys.stderr)
        cam.stop_monitor()
        cam.close()
        exit(0)

except IOError as e:
    
    if not (cam is None):
        print('O programa teve um erro de IO, provavelmente ffplay fechado. Fechando conexão com a câmera...', file=sys.stderr)
        cam.stop_monitor()
        cam.close()
        exit(0)
    else:
        print("Teve erro de IO", file=sys.stderr)

except Exception as e:
    print("Erro genérico:", repr(e), file=sys.stderr)
