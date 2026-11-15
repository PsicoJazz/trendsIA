import pytest

from planejador.entrada import TAMANHO_MAXIMO, validar_anotacao
from planejador.erros import EntradaInvalida


@pytest.mark.parametrize("texto", ["", "   ", "\n\t", None])
def test_entrada_vazia_e_rejeitada_com_orientacao(texto):
    with pytest.raises(EntradaInvalida, match="vazia"):
        validar_anotacao(texto)


def test_entrada_muito_curta():
    with pytest.raises(EntradaInvalida, match="curta"):
        validar_anotacao("aula")


def test_entrada_muito_longa():
    with pytest.raises(EntradaInvalida, match="maximo"):
        validar_anotacao("x" * (TAMANHO_MAXIMO + 1))


def test_entrada_valida_remove_espacos():
    assert validar_anotacao("  Aula sobre banco de dados  ") == "Aula sobre banco de dados"
