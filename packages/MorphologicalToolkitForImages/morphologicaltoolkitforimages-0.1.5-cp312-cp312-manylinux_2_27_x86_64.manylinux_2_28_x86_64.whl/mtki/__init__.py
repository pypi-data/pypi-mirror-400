try:
    import torch 
except ImportError:
    raise ImportError("O pacote 'mtki' requer a biblioteca PyTorch.")


from ._mtki import *
