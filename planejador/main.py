"""Interface de linha de comando: modo unico (texto/arquivo/stdin) e modo lote (pastas)."""
import argparse
import logging
import sys
from pathlib import Path
from typing import Callable, List, Optional

from .client import chamar_llm
from .config import Config, carregar_config
from .entrada import validar_anotacao
from .erros import CredencialInvalida, EntradaInvalida, PlanejadorError
from .formatar import formatar
from .servico import gerar_planejamento

log = logging.getLogger("planejador")


def _args(argv: Optional[List[str]]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="planejador", description="Transforma anotacoes de aula em planejamento estruturado.")
    p.add_argument("texto", nargs="?", help="anotacao entre aspas (se omitido, le --arquivo, as pastas ou a entrada padrao)")
    p.add_argument("--arquivo", help="arquivo .txt com a anotacao")
    p.add_argument("--pasta-entrada", help="modo lote: pasta com arquivos .txt")
    p.add_argument("--pasta-saida", help="modo lote: pasta onde gravar os .md (padrao: ./saida)")
    return p.parse_args(argv)


def _modo_unico(args, chamador: Callable) -> int:
    if args.arquivo:
        try:
            texto = Path(args.arquivo).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            raise EntradaInvalida("Nao foi possivel ler o arquivo informado (existe? esta em UTF-8?).") from None
    elif args.texto is not None:
        texto = args.texto
    else:
        texto = sys.stdin.read()
    texto = validar_anotacao(texto)  # impede o envio se vazio, antes de exigir credencial
    config = carregar_config()
    log.info("processando 1 anotacao (%d caracteres)", len(texto))
    print(formatar(gerar_planejamento(texto, config, chamador)))
    return 0


def _modo_lote(args, config: Config, chamador: Callable) -> int:
    entrada = Path(args.pasta_entrada)
    saida = Path(args.pasta_saida or "saida")
    arquivos = sorted(entrada.glob("*.txt")) if entrada.is_dir() else []
    if not arquivos:
        raise EntradaInvalida("Nenhum arquivo .txt encontrado na pasta de entrada.")
    saida.mkdir(parents=True, exist_ok=True)

    falhas, primeiro_codigo = 0, 0
    for arq in arquivos:
        try:
            texto = arq.read_text(encoding="utf-8")
            plano = gerar_planejamento(texto, config, chamador)
            (saida / f"{arq.stem}.md").write_text(formatar(plano) + "\n", encoding="utf-8")
            log.info("arquivo=%s status=%s", arq.name, plano.status)
        except CredencialInvalida:
            raise  # nao adianta continuar com a credencial rejeitada
        except (PlanejadorError, OSError, UnicodeDecodeError) as exc:
            falhas += 1
            codigo = getattr(exc, "codigo_saida", 1)
            primeiro_codigo = primeiro_codigo or codigo
            log.error("arquivo=%s falhou: %s", arq.name, type(exc).__name__)
            print(f"[{arq.name}] {exc if isinstance(exc, PlanejadorError) else 'erro ao ler/gravar arquivo'}", file=sys.stderr)
    print(f"Concluido: {len(arquivos) - falhas} de {len(arquivos)} arquivos processados em '{saida}'.")
    return primeiro_codigo


def main(argv: Optional[List[str]] = None, chamador: Callable = chamar_llm) -> int:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s %(levelname)s %(message)s")
    args = _args(argv)
    try:
        if args.pasta_entrada:
            return _modo_lote(args, carregar_config(), chamador)
        return _modo_unico(args, chamador)
    except PlanejadorError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return exc.codigo_saida
