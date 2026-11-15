import pytest

from planejador.erros import RespostaInvalida
from planejador.formatar import formatar
from planejador.parser import interpretar_resposta
from tests.conftest import JSON_OK


def test_resposta_ok():
    p = interpretar_resposta(JSON_OK)
    assert p.status == "ok" and p.tema == "Banco de Dados" and len(p.conteudo) == 2


def test_json_dentro_de_cercas_markdown():
    assert interpretar_resposta("```json\n" + JSON_OK + "\n```").status == "ok"


def test_texto_antes_e_depois_do_json():
    assert interpretar_resposta("Claro! " + JSON_OK + " Espero ter ajudado.").status == "ok"


def test_campo_string_vira_lista():
    p = interpretar_resposta(JSON_OK.replace('["Exercicio de modelagem"]', '"Exercicio de modelagem"'))
    assert p.atividades == ["Exercicio de modelagem"]


@pytest.mark.parametrize("texto", ["", "so texto sem json", "{quebrado", "[1,2]", '{"status":"talvez"}', '{"tema":"x"}'])
def test_respostas_invalidas(texto):
    with pytest.raises(RespostaInvalida):
        interpretar_resposta(texto)


def test_status_ok_com_campo_faltando():
    with pytest.raises(RespostaInvalida, match="avaliacao"):
        interpretar_resposta('{"status":"ok","tema":"a","objetivo":"b","conteudo":["c"],"atividades":["d"]}')


def test_insuficiente_sem_motivo_recebe_motivo_padrao():
    assert interpretar_resposta('{"status":"insuficiente"}').motivo


def test_formatacao_ok_segue_modelo_esperado():
    saida = formatar(interpretar_resposta(JSON_OK))
    for rotulo in ("Tema da aula: Banco de Dados", "Objetivo:", "Conteudo:", "Atividades:", "Avaliacao:"):
        assert rotulo in saida


def test_formatacao_insuficiente_e_fora_do_escopo():
    assert "informacao insuficiente" in formatar(interpretar_resposta('{"status":"insuficiente","motivo":"falta tema"}'))
    assert "nao parece" in formatar(interpretar_resposta('{"status":"fora_do_escopo","motivo":"receita"}'))
