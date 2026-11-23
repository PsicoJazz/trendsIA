"""Testes do cliente HTTP com requests.post substituido (nenhuma chamada real)."""
import logging

import pytest
import requests

from planejador import client
from planejador.erros import CredencialInvalida, ErroComunicacao, RespostaInvalida


class RespostaFalsa:
    def __init__(self, status=200, corpo=None, json_invalido=False):
        self.status_code, self._corpo, self._inv = status, corpo, json_invalido

    def json(self):
        if self._inv:
            raise ValueError("json invalido")
        return self._corpo


def _patch(monkeypatch, retorno=None, excecao=None):
    def falso(*a, **k):
        if excecao:
            raise excecao
        return retorno
    monkeypatch.setattr(client.requests, "post", falso)


MSGS = [{"role": "user", "content": "texto do professor"}]


def test_sucesso(monkeypatch, config):
    _patch(monkeypatch, RespostaFalsa(200, {"choices": [{"message": {"content": "ola"}}]}))
    assert client.chamar_llm(config, MSGS) == "ola"


@pytest.mark.parametrize("status", [401, 403])
def test_credencial_invalida(monkeypatch, config, status):
    _patch(monkeypatch, RespostaFalsa(status))
    with pytest.raises(CredencialInvalida):
        client.chamar_llm(config, MSGS)


@pytest.mark.parametrize("status", [429, 500, 503, 404])
def test_erros_http_viram_erro_de_comunicacao(monkeypatch, config, status):
    _patch(monkeypatch, RespostaFalsa(status))
    with pytest.raises(ErroComunicacao):
        client.chamar_llm(config, MSGS)


@pytest.mark.parametrize("exc", [requests.exceptions.ConnectionError("https://x?key=CHAVE-SECRETA-123"), requests.exceptions.Timeout()])
def test_falha_de_rede_e_timeout(monkeypatch, config, exc):
    _patch(monkeypatch, excecao=exc)
    with pytest.raises(ErroComunicacao) as e:
        client.chamar_llm(config, MSGS)
    assert "CHAVE-SECRETA-123" not in str(e.value)


@pytest.mark.parametrize("resp", [RespostaFalsa(200, {}), RespostaFalsa(200, {"choices": []}), RespostaFalsa(200, json_invalido=True)])
def test_corpo_inesperado(monkeypatch, config, resp):
    _patch(monkeypatch, resp)
    with pytest.raises(RespostaInvalida):
        client.chamar_llm(config, MSGS)


def test_sem_chave_nao_envia_cabecalho_authorization(monkeypatch, config):
    capturado = {}

    def falso(url, headers=None, **k):
        capturado.update(headers)
        return RespostaFalsa(200, {"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(client.requests, "post", falso)
    sem_chave = type(config)(base_url=config.base_url, modelo=config.modelo, api_key="", timeout=5)
    assert client.chamar_llm(sem_chave, MSGS) == "ok"
    assert "Authorization" not in capturado


def test_com_chave_envia_bearer(monkeypatch, config):
    capturado = {}

    def falso(url, headers=None, **k):
        capturado.update(headers)
        return RespostaFalsa(200, {"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(client.requests, "post", falso)
    client.chamar_llm(config, MSGS)
    assert capturado["Authorization"] == "Bearer CHAVE-SECRETA-123"


def test_401_sem_chave_orienta_a_definir_a_variavel(monkeypatch, config):
    _patch(monkeypatch, RespostaFalsa(401))
    sem_chave = type(config)(base_url=config.base_url, modelo=config.modelo, api_key="", timeout=5)
    with pytest.raises(CredencialInvalida, match="LLM_API_KEY"):
        client.chamar_llm(sem_chave, MSGS)


def test_erro_de_certificado_tem_mensagem_especifica(monkeypatch, config):
    _patch(monkeypatch, excecao=requests.exceptions.SSLError("detalhe interno"))
    with pytest.raises(ErroComunicacao, match="LLM_VERIFY_SSL"):
        client.chamar_llm(config, MSGS)


def test_parametro_verify_e_repassado_ao_requests(monkeypatch, config):
    capturado = {}

    def falso(url, **k):
        capturado.update(k)
        return RespostaFalsa(200, {"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(client.requests, "post", falso)
    sem_tls = type(config)(base_url=config.base_url, modelo=config.modelo, api_key="", timeout=5, verify=False)
    client.chamar_llm(sem_tls, MSGS)
    assert capturado["verify"] is False
    client.chamar_llm(config, MSGS)
    assert capturado["verify"] is True


def test_logs_nao_vazam_chave_nem_texto(monkeypatch, config, caplog):
    caplog.set_level(logging.DEBUG)
    _patch(monkeypatch, excecao=requests.exceptions.ConnectionError("detalhe com CHAVE-SECRETA-123"))
    with pytest.raises(ErroComunicacao):
        client.chamar_llm(config, MSGS)
    assert "CHAVE-SECRETA-123" not in caplog.text and "texto do professor" not in caplog.text
