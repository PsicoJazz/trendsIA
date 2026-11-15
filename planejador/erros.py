"""Erros controlados da aplicacao. Cada um carrega o codigo de saida do processo."""


class PlanejadorError(Exception):
    codigo_saida = 1


class EntradaInvalida(PlanejadorError):
    codigo_saida = 1


class ConfigError(PlanejadorError):
    codigo_saida = 2


class CredencialInvalida(PlanejadorError):
    codigo_saida = 3


class ErroComunicacao(PlanejadorError):
    codigo_saida = 4


class RespostaInvalida(PlanejadorError):
    codigo_saida = 5
