import os
import sys
import ctypes
from pathlib import Path

# Carrega a biblioteca manualmente antes de qualquer import
def _preload_libs ():
    """Pre-carrega a biblioteca Fortran"""
    pacote_dir = Path(__file__).parent
    core_dir = pacote_dir / "_core"

    def encontrar_lib (prefixo: str) -> Path:
        """
        Encontra a melhor biblioteca compartilhada para um dado prefixo.
        Prioridade:
        1) libXXX.so
        2) libXXX.so.<major>
        3) libXXX.so.<major>.<minor>.<patch>
        """
        if not core_dir.exists():
            raise RuntimeError(f"Diretório {core_dir} não existe")

        candidatos = list(core_dir.glob(f"{prefixo}.so*"))

        if not candidatos:
            raise RuntimeError(f"Nenhuma biblioteca encontrada para {prefixo}")

        # ordena colocando as mais genéricas primeiro
        candidatos.sort(key=lambda p: (
            p.suffix != ".so",          # .so primeiro
            p.name.count(".")           # menos pontos = mais genérica
        ))

        return candidatos[0]

    libutilidades = encontrar_lib("libutilidades")
    ctypes.CDLL(libutilidades, mode=ctypes.RTLD_GLOBAL)

# Executa o pré-carregamento
_preload_libs()

# Agora importa o módulo
from .api import *
from ._version import __version__