"""Interpretacao e validacao da resposta do modelo."""
import json
import re
from dataclasses import dataclass, field
from typing import List

from .erros import RespostaInvalida

STATUS_VALIDOS = ("ok", "insuficiente", "fora_do_escopo")


@dataclass
class Planejamento:
    status: str
    motivo: str = ""
    tema: str = ""
    objetivo: str = ""
    conteudo: List[str] = field(default_factory=list)
    atividades: List[str] = field(default_factory=list)
    avaliacao: List[str] = field(default_factory=list)


def _extrair_json(texto: str) -> str:
    """Modelos as vezes cercam o JSON com ```; remove isso e pega do primeiro { ao ultimo }."""
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", (texto or "").strip())
    ini, fim = texto.find("{"), texto.rfind("}")
    if ini == -1 or fim <= ini:
        raise RespostaInvalida("O modelo nao devolveu um JSON. Tente novamente.")
    return texto[ini : fim + 1]


def _como_lista(valor) -> List[str]:
    if valor in (None, ""):
        return []
    if isinstance(valor, str):
        return [valor.strip()]
    if isinstance(valor, list):
        return [str(v).strip() for v in valor if str(v).strip()]
    raise RespostaInvalida("Campo da resposta com tipo inesperado.")


def interpretar_resposta(texto: str) -> Planejamento:
    try:
        dados = json.loads(_extrair_json(texto))
    except json.JSONDecodeError:
        raise RespostaInvalida("O modelo devolveu um JSON malformado. Tente novamente.") from None
    if not isinstance(dados, dict):
        raise RespostaInvalida("O JSON devolvido nao e um objeto.")

    status = str(dados.get("status", "")).strip()
    if status not in STATUS_VALIDOS:
        raise RespostaInvalida("A resposta nao informa um 'status' valido.")

    plano = Planejamento(
        status=status,
        motivo=str(dados.get("motivo") or "").strip(),
        tema=str(dados.get("tema") or "").strip(),
        objetivo=str(dados.get("objetivo") or "").strip(),
        conteudo=_como_lista(dados.get("conteudo")),
        atividades=_como_lista(dados.get("atividades")),
        avaliacao=_como_lista(dados.get("avaliacao")),
    )

    if status == "ok":
        faltam = [n for n in ("tema", "objetivo", "conteudo", "atividades", "avaliacao") if not getattr(plano, n)]
        if faltam:
            raise RespostaInvalida("Resposta incompleta; campos ausentes: " + ", ".join(faltam) + ".")
    elif not plano.motivo:
        plano.motivo = "O modelo nao informou o motivo."
    return plano
