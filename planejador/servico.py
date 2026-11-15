"""Orquestra o fluxo: validar -> preparar -> chamar -> interpretar."""
from typing import Callable

from .client import chamar_llm
from .config import Config
from .entrada import validar_anotacao
from .parser import Planejamento, interpretar_resposta
from .prompt import construir_mensagens


def gerar_planejamento(anotacao: str, config: Config, chamador: Callable = chamar_llm) -> Planejamento:
    """`chamador` pode ser substituido nos testes para evitar chamada real ao LLM."""
    texto = validar_anotacao(anotacao)
    resposta = chamador(config, construir_mensagens(texto))
    return interpretar_resposta(resposta)
