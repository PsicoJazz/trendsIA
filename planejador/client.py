"""Unica camada que fala com o LLM (API compativel com OpenAI /chat/completions)."""
import logging
import time
from typing import Dict, List

import requests
import urllib3

from .config import Config
from .erros import CredencialInvalida, ErroComunicacao, RespostaInvalida

log = logging.getLogger(__name__)
_aviso_tls_emitido = False


def chamar_llm(config: Config, mensagens: List[Dict[str, str]]) -> str:
    """Envia a solicitacao e devolve o texto da resposta do modelo."""
    url = f"{config.base_url}/chat/completions"
    cabecalhos = {"Content-Type": "application/json"}
    if config.api_key:
        cabecalhos["Authorization"] = f"Bearer {config.api_key}"
    corpo = {"model": config.modelo, "messages": mensagens, "temperature": 0.2}

    global _aviso_tls_emitido
    if config.verify is False:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if not _aviso_tls_emitido:
            log.warning("verificacao de certificado TLS DESATIVADA (LLM_VERIFY_SSL=false)")
            _aviso_tls_emitido = True

    inicio = time.monotonic()
    try:
        resp = requests.post(url, headers=cabecalhos, json=corpo, timeout=config.timeout, verify=config.verify)
    except requests.exceptions.Timeout:
        log.error("timeout apos %ss", config.timeout)
        raise ErroComunicacao(
            f"O servico nao respondeu em {config.timeout}s. Tente novamente mais tarde "
            "(confira se a plataforma esta no horario agendado)."
        ) from None
    except requests.exceptions.SSLError:
        log.error("falha de comunicacao: SSLError")
        raise ErroComunicacao(
            "Falha na verificacao do certificado TLS do servico. Se o endpoint interno usa certificado proprio, "
            "informe LLM_CA_BUNDLE (caminho do certificado) ou, so em rede interna, LLM_VERIFY_SSL=false."
        ) from None
    except requests.exceptions.RequestException as exc:
        # Registra apenas o tipo do erro: a mensagem da excecao pode conter a URL completa.
        log.error("falha de comunicacao: %s", type(exc).__name__)
        raise ErroComunicacao(
            "Nao foi possivel conectar ao servico de LLM. Verifique LLM_BASE_URL, a rede e o agendamento."
        ) from None

    duracao = time.monotonic() - inicio
    log.info("resposta http=%s duracao=%.1fs", resp.status_code, duracao)

    if resp.status_code in (401, 403):
        if config.api_key:
            raise CredencialInvalida("Credencial rejeitada pelo servico (LLM_API_KEY invalida ou sem permissao).")
        raise CredencialInvalida("O servico exigiu credencial e LLM_API_KEY nao foi definida.")
    if resp.status_code == 429:
        raise ErroComunicacao("Servico sobrecarregado ou limite de uso atingido (HTTP 429). Aguarde e tente de novo.")
    if resp.status_code >= 400:
        raise ErroComunicacao(f"O servico retornou erro HTTP {resp.status_code}.")

    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise RespostaInvalida("A resposta do servico nao tem o formato esperado (choices/message/content).") from None
