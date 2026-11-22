"""Carregamento e validacao da configuracao (variaveis de ambiente / .env)."""
import os
from dataclasses import dataclass, field
from typing import Mapping, Optional

from dotenv import load_dotenv

from .erros import ConfigError

TIMEOUT_PADRAO = 120


@dataclass(frozen=True)
class Config:
    base_url: str
    modelo: str
    api_key: str = field(default="", repr=False)  # opcional; repr=False: nunca aparece em print/log
    timeout: int = TIMEOUT_PADRAO


def carregar_config(env: Optional[Mapping[str, str]] = None) -> Config:
    """Le a configuracao. Variaveis ja definidas no ambiente (ex.: dashboard) tem prioridade sobre o .env."""
    if env is None:
        load_dotenv()  # nao sobrescreve variaveis ja existentes
        env = os.environ

    def ler(nome: str) -> str:
        return (env.get(nome) or "").strip()

    faltando = [n for n in ("LLM_BASE_URL", "LLM_MODEL") if not ler(n)]
    if faltando:
        # Informa apenas os NOMES das variaveis, nunca valores.
        raise ConfigError(
            "Configuracao incompleta. Defina no .env ou no ambiente: " + ", ".join(faltando) + "."
        )

    base_url = ler("LLM_BASE_URL").rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        raise ConfigError("LLM_BASE_URL deve comecar com http:// ou https://.")

    bruto = ler("LLM_TIMEOUT") or str(TIMEOUT_PADRAO)
    try:
        timeout = int(bruto)
        if timeout <= 0:
            raise ValueError
    except ValueError:
        raise ConfigError("LLM_TIMEOUT deve ser um numero inteiro positivo (segundos).") from None

    return Config(base_url=base_url, modelo=ler("LLM_MODEL"), api_key=ler("LLM_API_KEY"), timeout=timeout)
