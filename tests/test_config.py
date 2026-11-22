import pytest

from planejador.config import carregar_config
from planejador.erros import ConfigError

BASE = {"LLM_BASE_URL": "https://h:9001/v1/", "LLM_MODEL": "m", "LLM_API_KEY": "segredo"}


def test_config_valida_normaliza_url_e_usa_timeout_padrao():
    c = carregar_config(BASE)
    assert c.base_url == "https://h:9001/v1" and c.timeout == 120


def test_chave_e_opcional():
    env = {k: v for k, v in BASE.items() if k != "LLM_API_KEY"}
    assert carregar_config(env).api_key == ""


def test_chave_so_com_espacos_vira_vazia():
    assert carregar_config({**BASE, "LLM_API_KEY": "   "}).api_key == ""


@pytest.mark.parametrize("faltando", ["LLM_BASE_URL", "LLM_MODEL"])
def test_variavel_obrigatoria_ausente_informa_so_o_nome(faltando):
    env = {k: v for k, v in BASE.items() if k != faltando}
    with pytest.raises(ConfigError) as e:
        carregar_config(env)
    assert faltando in str(e.value) and "segredo" not in str(e.value)


@pytest.mark.parametrize("valor", ["abc", "0", "-3"])
def test_timeout_invalido(valor):
    with pytest.raises(ConfigError, match="LLM_TIMEOUT"):
        carregar_config({**BASE, "LLM_TIMEOUT": valor})


def test_url_sem_esquema():
    with pytest.raises(ConfigError, match="http"):
        carregar_config({**BASE, "LLM_BASE_URL": "servidor:9001"})


def test_chave_nao_aparece_no_repr():
    assert "segredo" not in repr(carregar_config(BASE))
