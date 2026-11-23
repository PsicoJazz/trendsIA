"""Carregamento e validacao da configuracao (variaveis de ambiente / .env)."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Union

from dotenv import load_dotenv

from .erros import ConfigError

TIMEOUT_PADRAO = 120


@dataclass(frozen=True)
class Config:
    base_url: str
    modelo: str
    api_key: str = field(default="", repr=False)  # opcional; repr=False: nunca aparece em print/log
    timeout: int = TIMEOUT_PADRAO
    verify: Union[bool, str] = True  # True, False ou caminho de um certificado CA
    debug: bool = False  # registra trecho da mensagem de erro do servico (so para diagnostico)


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

    verify: Union[bool, str] = True
    flag = ler("LLM_VERIFY_SSL").lower()
    if flag in ("false", "0", "no", "nao", "não"):
        verify = False
    elif flag not in ("", "true", "1", "yes", "sim"):
        raise ConfigError("LLM_VERIFY_SSL deve ser true ou false.")
    elif ler("LLM_CA_BUNDLE"):
        if not Path(ler("LLM_CA_BUNDLE")).is_file():
            raise ConfigError("LLM_CA_BUNDLE aponta para um arquivo que nao existe.")
        verify = ler("LLM_CA_BUNDLE")

    return Config(
        base_url=base_url,
        modelo=ler("LLM_MODEL"),
        api_key=ler("LLM_API_KEY"),
        timeout=timeout,
        verify=verify,
        debug=ler("LLM_DEBUG").lower() in ("true", "1", "yes", "sim"),
    )
