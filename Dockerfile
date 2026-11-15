FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY planejador/ planejador/
# Anotacoes de exemplo (sem dados pessoais) processadas no modo lote.
COPY exemplos/entradas/ entradas/

# Nenhuma credencial na imagem: as variaveis LLM_* sao informadas no dashboard da plataforma.
# Le /app/entradas/*.txt e grava /persistent/saida/*.md (o que nao esta em /persistent se perde).
CMD ["python", "-m", "planejador", "--pasta-entrada", "/app/entradas", "--pasta-saida", "/persistent/saida"]
