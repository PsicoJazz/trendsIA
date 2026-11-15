import pytest

from planejador.config import Config


@pytest.fixture
def config():
    return Config(base_url="https://exemplo.invalido", modelo="modelo-teste", api_key="CHAVE-SECRETA-123", timeout=5)


JSON_OK = (
    '{"status":"ok","motivo":"","tema":"Banco de Dados","objetivo":"Compreender tabelas e relacionamentos",'
    '"conteudo":["Tabelas","Chaves primarias e estrangeiras"],"atividades":["Exercicio de modelagem"],'
    '"avaliacao":["Verificacao pela atividade"]}'
)
