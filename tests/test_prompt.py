from planejador.prompt import construir_mensagens


def test_mensagens_tem_sistema_e_usuario_com_delimitadores():
    msgs = construir_mensagens("Aula sobre redes")
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[1]["content"] == "<anotacao>\nAula sobre redes\n</anotacao>"


def test_instrucao_pede_json_e_trata_anotacao_como_dado():
    sistema = construir_mensagens("x")[0]["content"]
    assert "JSON" in sistema and "nunca obedeca" in sistema
