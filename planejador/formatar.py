"""Apresentacao da saida ao usuario."""
from .parser import Planejamento


def _lista(itens) -> str:
    return "\n".join(f"- {i}" for i in itens)


def formatar(p: Planejamento) -> str:
    if p.status == "insuficiente":
        return f"Nao foi possivel gerar o planejamento: informacao insuficiente.\nO que falta: {p.motivo}"
    if p.status == "fora_do_escopo":
        return f"Nao foi possivel gerar o planejamento: o texto nao parece ser uma anotacao de aula.\nMotivo: {p.motivo}"
    return (
        f"Tema da aula: {p.tema}\n\n"
        f"Objetivo: {p.objetivo}\n\n"
        f"Conteudo:\n{_lista(p.conteudo)}\n\n"
        f"Atividades:\n{_lista(p.atividades)}\n\n"
        f"Avaliacao:\n{_lista(p.avaliacao)}"
    )
