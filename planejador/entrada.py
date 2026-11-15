"""Captura e validacao da entrada do usuario."""
from .erros import EntradaInvalida

TAMANHO_MINIMO = 10
TAMANHO_MAXIMO = 4000


def validar_anotacao(texto: str) -> str:
    """Retorna a anotacao limpa ou levanta EntradaInvalida com orientacao ao usuario."""
    limpo = (texto or "").strip()
    if not limpo:
        raise EntradaInvalida(
            "A anotacao esta vazia. Escreva o que pretende ensinar, "
            "por exemplo: 'Aula sobre banco de dados, explicar tabelas e chaves.'"
        )
    if len(limpo) < TAMANHO_MINIMO:
        raise EntradaInvalida(
            f"A anotacao e muito curta (minimo {TAMANHO_MINIMO} caracteres). Informe o tema e o que pretende fazer."
        )
    if len(limpo) > TAMANHO_MAXIMO:
        raise EntradaInvalida(
            f"A anotacao tem {len(limpo)} caracteres; o maximo e {TAMANHO_MAXIMO}. Resuma ou divida em aulas."
        )
    return limpo
