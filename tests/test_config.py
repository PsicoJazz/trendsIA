import pytest

from planejador.config import carregar_config
from planejador.erros import ConfigError

BASE = {"LLM_BASE_URL": "https://h:9001/v1/", "LLM_MODEL": "m", "LLM_API_KEY": "segredo"}


def test_config_valida_normaliza_url_e_usa_timeout_padrao():
    c = carregar_config(BASE)
    assert c.base_url == "https://h:9001/v1" and c.timeout == 120


def test_credencial_ausente_informa_so_o_nome_da_variavel():
    env = {k: v for k, v in BASE.items() if k != "LLM_API_KEY"}
    with pytest.raises(ConfigError) as e:
        carregar_config(env)
    assert "LLM_API_KEY" in str(e.value)


def test_credencial_so_com_espacos_conta_como_ausente():
    with pytest.raises(ConfigError):
        carregar_config({**BASE, "LLM_API_KEY": "   "})


@pytest.mark.parametrize("valor", ["abc", "0", "-3"])
def test_timeout_invalido(valor):
    with pytest.raises(ConfigError, match="LLM_TIMEOUT"):
        carregar_config({**BASE, "LLM_TIMEOUT": valor})


def test_url_sem_esquema():
    with pytest.raises(ConfigError, match="http"):
        carregar_config({**BASE, "LLM_BASE_URL": "servidor:9001"})


def test_chave_nao_aparece_no_repr():
    assert "segredo" not in repr(carregar_config(BASE))
