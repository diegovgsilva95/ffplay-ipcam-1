import sys

def printerr(*args):
    """ 
    Apenas um alias para o print para não ter que ficar 
    repetindo file=sys.stderr a cada impressão de texto no STDERR 
    """
    print(*args, file=sys.stderr)
