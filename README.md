# Planejador de Aulas com LLM

Transforma anotações soltas de professores em um planejamento de aula estruturado
(tema, objetivo, conteúdo, atividades e avaliação) usando um LLM da plataforma TrendsIA.

**Exemplo**

Entrada:
`Aula sobre banco de dados, explicar tabelas, relacionamentos, chaves primárias e estrangeiras. Fazer uma atividade prática com os alunos.`

Saída (formato; o texto exato varia a cada execução):
```
Tema da aula: Banco de Dados

Objetivo: ...

Conteudo:
- ...

Atividades:
- ...

Avaliacao:
- ...
```

Se a anotação for vazia, incompleta demais ou não for sobre aula, o programa informa o que falta em vez de inventar um plano.

## Requisitos

- Python **3.12** (testado com 3.12.3)
- Acesso ao LLM da plataforma TrendsIA **somente dentro do horário agendado** (veja [Agendamento](#agendamento-e-rede-da-plataforma))
- Docker, apenas para enviar a imagem à plataforma

Os testes automatizados **não** precisam de LLM, de credencial nem de rede.

## Instalação

Linux/macOS:
```bash
git clone <https://github.com/PsicoJazz/trendsIA>
cd planejador-aulas
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Windows (PowerShell):
```powershell
git clone <https://github.com/PsicoJazz/trendsIA>
cd planejador-aulas
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

`requirements.txt` tem só as dependências de execução (`python-dotenv`, `requests`); `requirements-dev.txt` acrescenta o `pytest`.

## Configuração

1. Copie o modelo: `cp .env.example .env` (Windows: `copy .env.example .env`).
2. Preencha o `.env`. **Nunca versione o `.env`** (já está no `.gitignore`).

| Variável | Obrigatória | Descrição |
|---|---|---|
| `LLM_BASE_URL` | sim | URL base de uma API compatível com OpenAI. O programa chama `<LLM_BASE_URL>/chat/completions`. Ex.: `https://llm-internal.softex:9001/v1` (confirme o caminho `/v1` na documentação da plataforma) |
| `LLM_MODEL` | sim | Nome do modelo (ex.: `qwen...`, conforme a plataforma) |
| `LLM_API_KEY` | não | Chave de acesso. Só preencha se o serviço exigir; sem ela, nenhum cabeçalho de autenticação é enviado |
| `LLM_TIMEOUT` | não | Tempo máximo de espera em segundos (padrão `120`) |

Variáveis já definidas no ambiente (como as do dashboard da plataforma) têm prioridade sobre o `.env`.

## Execução

Com o ambiente virtual ativo e o `.env` preenchido:

```bash
# Texto direto
python -m planejador "Aula sobre banco de dados, explicar tabelas, chaves primárias e estrangeiras. Atividade prática."

# Arquivo .txt (UTF-8)
python -m planejador --arquivo exemplos/entradas/01_comum.txt

# Entrada padrão
echo "Aula sobre redes: modelo OSI e TCP/IP" | python -m planejador

# Modo lote: processa todos os .txt de uma pasta e grava um .md por arquivo
python -m planejador --pasta-entrada exemplos/entradas --pasta-saida saida
```

Códigos de saída: `0` sucesso · `1` entrada inválida · `2` configuração ausente/inválida (`LLM_BASE_URL`/`LLM_MODEL`) · `3` credencial rejeitada ou exigida e não definida · `4` falha de comunicação · `5` resposta do modelo inválida.

## Testes

```bash
python -m pytest -v
```

Cobrem validação de entrada, configuração, montagem do prompt, interpretação da resposta, cliente HTTP (com `requests.post` simulado), logs sem vazamento e o fluxo completo com LLM simulado.

Verificação de segredos antes de publicar:
```bash
git ls-files | grep -E '(^|/)\.env$'          # não deve listar nada
git log --all -p | grep -iE 'LLM_API_KEY=[^<[:space:]]+'   # não deve listar nada (relevante se você usar chave)
```

## Execução na plataforma TrendsIA

1. Gere a imagem com um identificador único (seu e-mail sem caracteres especiais), ex. `joaosilvagmailcom`:
   ```bash
   docker build -t joaosilvagmailcom:latest .
   docker save --output joaosilvagmailcom.tar joaosilvagmailcom:latest
   ```
   A imagem não contém credenciais (`.dockerignore` exclui `.env`). Confira o tamanho: `docker images joaosilvagmailcom` (limite da plataforma: 1024 MB).
2. No dashboard: **Upload** do `.tar`.
3. **Portas:** deixe em branco (a aplicação não escuta porta; roda e termina).
4. **Variáveis de ambiente** (uma por linha):
   ```
   LLM_BASE_URL=https://llm-internal.softex:9001/v1
   LLM_MODEL=<modelo>
   ```
   Acrescente `LLM_API_KEY=<chave>` apenas se o serviço exigir (o guia da plataforma não menciona chave). Nunca coloque credenciais na imagem nem em logs.
5. **Iniciar** no horário agendado. Acompanhe em **Logs**.
6. Os planejamentos ficam em `/persistent/saida/*.md` (somente `/persistent` sobrevive à parada do container).

### Agendamento e rede da plataforma

- O endpoint `https://llm-internal.softex:9001` só é acessível de dentro do ambiente da plataforma, não do seu computador nem do navegador. Fora dela, a execução termina com o erro `4` (falha de comunicação), o que é esperado.
- Execute o container dentro do horário agendado para o seu grupo; fora dele a chamada falha ou expira.
- Os logs são apagados quando o container é iniciado de novo: salve as evidências antes.

## Estrutura do repositório

```
planejador/
  main.py       CLI: modos único e lote, códigos de saída
  config.py     leitura e validação do .env / ambiente
  entrada.py    validação da anotação (vazia, curta, longa)
  prompt.py     montagem da solicitação (função pura)
  client.py     única camada que chama o LLM; trata 401/403/429/5xx, timeout, rede
  parser.py     interpreta e valida o JSON devolvido pelo modelo
  formatar.py   apresentação do resultado
  servico.py    orquestra validar -> prompt -> chamada -> interpretação
tests/          testes pytest (sem chamada real ao LLM)
exemplos/entradas/   anotações usadas nos testes com o LLM real
Dockerfile · .dockerignore · .env.example · requirements*.txt
relatorio.md    decisões, evidências e limitações
```

## Limitações conhecidas

- A saída do LLM varia entre execuções; o programa valida a **estrutura**, não a qualidade pedagógica do conteúdo. Revise o plano antes de usá-lo.
- O contrato da API (`/chat/completions`, formato OpenAI) é uma suposição baseada no uso de `LLM_BASE_URL`/`LLM_MODEL`; confirme na documentação da plataforma.
- No modo lote, se o serviço estiver fora do ar, cada arquivo espera o timeout antes de falhar (a execução só é interrompida cedo em caso de credencial rejeitada).
- Na plataforma, novas anotações exigem reconstruir a imagem (as de `exemplos/entradas/` são copiadas para ela).
- Anotações com mais de 4000 caracteres são recusadas; não há histórico nem edição do plano.
- O texto da anotação é enviado ao serviço de LLM; não inclua dados pessoais de alunos.

## Outros artefatos

- Relatório: [`relatorio.md`](relatorio.md)
- Vídeo de demonstração: `<LINK-DO-VIDEO>`
