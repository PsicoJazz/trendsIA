"""Fluxo completo com o LLM simulado: valida codigos de saida e mensagens."""
import pytest

from planejador import main as m
from planejador.erros import CredencialInvalida, ErroComunicacao
from tests.conftest import JSON_OK

ENV = {"LLM_BASE_URL": "https://h", "LLM_MODEL": "m", "LLM_API_KEY": "CHAVE-SECRETA-123"}


@pytest.fixture
def ambiente(monkeypatch):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(m, "carregar_config", m.carregar_config)  # usa o ambiente real do teste
    monkeypatch.setattr("planejador.config.load_dotenv", lambda *a, **k: None)  # ignora .env local


def _chamador_ok(cfg, msgs):
    return JSON_OK


def test_entrada_valida(ambiente, capsys):
    assert m.main(["Aula sobre banco de dados e tabelas"], chamador=_chamador_ok) == 0
    assert "Tema da aula: Banco de Dados" in capsys.readouterr().out


def test_entrada_vazia_impede_envio(ambiente, capsys):
    def nao_deve_chamar(cfg, msgs):
        raise AssertionError("o LLM nao deveria ser chamado")
    assert m.main(["   "], chamador=nao_deve_chamar) == 1
    assert "vazia" in capsys.readouterr().err


def test_configuracao_ausente(monkeypatch, capsys):
    monkeypatch.setattr("planejador.config.load_dotenv", lambda *a, **k: None)
    for k in ENV:
        monkeypatch.delenv(k, raising=False)
    assert m.main(["Aula sobre banco de dados e tabelas"], chamador=_chamador_ok) == 2
    err = capsys.readouterr().err
    assert "LLM_BASE_URL" in err and "LLM_MODEL" in err and "CHAVE-SECRETA-123" not in err


def test_sem_chave_executa_normalmente(monkeypatch, capsys):
    monkeypatch.setattr("planejador.config.load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("LLM_BASE_URL", "https://h")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    assert m.main(["Aula sobre banco de dados e tabelas"], chamador=_chamador_ok) == 0


def test_credencial_invalida_termina_controlado(ambiente, capsys):
    def rejeita(cfg, msgs):
        raise CredencialInvalida("Credencial rejeitada")
    assert m.main(["Aula sobre banco de dados e tabelas"], chamador=rejeita) == 3


def test_falha_de_comunicacao(ambiente, capsys):
    def cai(cfg, msgs):
        raise ErroComunicacao("Nao foi possivel conectar")
    assert m.main(["Aula sobre banco de dados e tabelas"], chamador=cai) == 4
    assert "conectar" in capsys.readouterr().err


def test_resposta_do_modelo_invalida(ambiente):
    assert m.main(["Aula sobre banco de dados e tabelas"], chamador=lambda c, s: "isto nao e json") == 5


def test_modo_lote_grava_saidas_e_continua_apos_falha(ambiente, tmp_path, capsys):
    ent, sai = tmp_path / "e", tmp_path / "s"
    ent.mkdir()
    (ent / "a.txt").write_text("Aula sobre banco de dados e tabelas", encoding="utf-8")
    (ent / "b.txt").write_text("", encoding="utf-8")  # vazia: falha so este arquivo
    codigo = m.main(["--pasta-entrada", str(ent), "--pasta-saida", str(sai)], chamador=_chamador_ok)
    assert codigo == 1
    assert (sai / "a.md").exists() and not (sai / "b.md").exists()
    assert "1 de 2" in capsys.readouterr().out


def test_modo_lote_pasta_inexistente(ambiente, tmp_path):
    assert m.main(["--pasta-entrada", str(tmp_path / "nao_existe")], chamador=_chamador_ok) == 1
