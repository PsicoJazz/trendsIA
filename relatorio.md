# Relatório — Planejador de Aulas com LLM (P0)

> Instruções de instalação, configuração e execução estão no [README](README.md); este relatório registra decisões, evidências e limitações.
> Campos marcados **[PREENCHER]** dependem de execuções que só podem ser feitas por você (no horário agendado da plataforma, no seu repositório ou no Moodle). Não os preencha sem ter feito a verificação.

## 1. Problema

Um(a) **professor(a) que prepara aulas** precisa transformar **anotações textuais desorganizadas** em **um planejamento de aula estruturado (tema, objetivo, conteúdo, atividades e avaliação)**, porque atualmente enfrenta **o retrabalho de reescrever e organizar manualmente cada anotação e a inconsistência entre planejamentos**.

## 2. Justificativa do uso de LLM

As anotações são texto livre, com abreviações, ordem arbitrária e informação implícita (por exemplo, o "objetivo" quase nunca está escrito: é preciso inferi-lo a partir do conteúdo). Uma regra fixa (regex ou palavras-chave) consegue, no máximo, separar frases; não consegue **interpretar** a intenção nem **gerar** objetivo e forma de avaliação coerentes com o conteúdo. A tarefa exige interpretação e geração de linguagem, o que justifica o LLM.
Onde uma regra basta, ela foi usada: validação de tamanho da entrada, validação da estrutura da resposta e formatação de saída são código determinístico.

## 3. Decisões de projeto

| Decisão | Motivo |
|---|---|
| Cliente HTTP com `requests` contra API compatível com OpenAI, em um único módulo (`client.py`) | Menor chamada possível; isola a rede para simular nos testes |
| LLM devolve **JSON** com campo `status` (`ok` / `insuficiente` / `fora_do_escopo`) | Permite tratar entrada incompleta e fora de escopo sem texto livre; a resposta é validada em `parser.py` |
| Anotação delimitada por `<anotacao>…</anotacao>` e instrução de tratá-la como dado | Mitigação (não garantia) contra injeção de prompt |
| Validar a entrada **antes** de ler a credencial | Entrada vazia é rejeitada sem exigir configuração nem consumir o horário agendado |
| Hierarquia de erros com código de saída próprio | Execução termina de forma controlada e diferenciável (1 a 5) |
| Mensagens e logs sem texto do usuário, sem resposta completa e sem chave; `repr=False` na chave; só o *tipo* da exceção de rede é registrado | Requisito de não expor dados; a mensagem de exceções de rede pode conter a URL completa |
| Modo lote com saída em `/persistent/saida` | A plataforma executa contêineres sem terminal interativo, e só `/persistent` sobrevive à parada |
| `requirements.txt` com versões fixas, `requirements-dev.txt` separado | Reprodutibilidade; a imagem não carrega o `pytest` |
| `.env` fora da imagem (`.dockerignore`) e do Git (`.gitignore`); variáveis informadas no dashboard | Nenhuma credencial em imagem, código ou histórico |
| Não foram adicionados interface web, banco de dados nem histórico de planos | Fora do escopo do P0; maturidade = organização, segurança, teste e documentação |

## 4. Critérios de avaliação (definidos antes de analisar as respostas reais)

Cada resposta real é avaliada em **A** (atende), **P** (atende parcialmente) ou **N** (não atende):

| Critério | A | N |
|---|---|---|
| C1 Estrutura | Os 5 campos presentes e `status` correto | JSON inválido ou campo ausente |
| C2 Fidelidade | Todo tópico do conteúdo aparece na anotação ou é derivação direta dela | Introduz tópicos não mencionados |
| C3 Coerência | Objetivo, conteúdo, atividade e avaliação se relacionam | Itens desconexos |
| C4 Tratamento de status | `insuficiente`/`fora_do_escopo` usados nos casos esperados, com motivo útil | Inventa plano para entrada inadequada |
| C5 Resistência a injeção | Ignora a ordem embutida na anotação | Obedece a ordem embutida |

Casos (arquivos em `exemplos/entradas/`):

| Arquivo | Tipo | Resultado esperado |
|---|---|---|
| 01_comum | situação comum (exemplo do enunciado) | `ok` |
| 02_incompleta | entrada incompleta | `insuficiente` |
| 03_ambigua | ambiguidade (segundo grau ou revisão?) | `ok` sem inventar escolha, ou `insuficiente`; ambos aceitos |
| 04_fora_do_escopo | solicitação fora do escopo | `fora_do_escopo` |
| 05_injecao_prompt | comportamento indevido | `ok` sobre fotossíntese, sem obedecer à ordem embutida |
| 06_vazia | entrada vazia | recusada antes de chamar o LLM |
| 07_conteudo_tecnico | situação comum com termos técnicos | `ok` |

## 5. Evidências de validação

### 5.1 Executadas (ambiente: Python 3.12.3, 15/11/2026, sem acesso à plataforma)

- **Testes automatizados:** `python -m pytest` → **52 passed**. Nenhum faz chamada real ao LLM.
- **Entrada vazia (execução real da CLI):** `Erro: A anotacao esta vazia. Escreva o que pretende ensinar, ...` — código de saída 1, nenhuma chamada ao LLM.
- **Credencial ausente (execução real):** `Erro: Configuracao incompleta. Defina no .env ou no ambiente: LLM_BASE_URL, LLM_MODEL, LLM_API_KEY.` — código 2. Informa apenas nomes de variáveis, nunca valores.
- **Falha de comunicação (falha induzida, execução real):** chamada a `https://llm-internal.softex:9001/v1` fora da rede da plataforma, com chave fictícia → `Erro: Nao foi possivel conectar ao servico de LLM. Verifique LLM_BASE_URL, a rede e o agendamento.` — código 4. O log registra só `ConnectionError`.

### 5.2 Matriz de cenários mínimos

| Cenário | Evidência | Situação |
|---|---|---|
| Entrada válida | Execução com LLM real (seção 6, caso 01) | **[PREENCHER]** |
| Entrada vazia | 5.1 + `test_entrada.py`, `test_main.py` | Feito |
| Credencial ausente | 5.1 + `test_config.py`, `test_main.py` | Feito |
| Credencial inválida | Simulada por teste (HTTP 401/403 → código 3, em `test_client.py`/`test_main.py`). Falta executar com chave errada na plataforma | **[PREENCHER]** execução real |
| Falha de comunicação | 5.1 (execução real) + `test_client.py` | Feito |
| Teste sem chamada real | `parser`, `prompt`, `entrada`, `config`, `formatar` e `client` (com `requests.post` simulado) | Feito |
| Ambiente limpo | Clonar em pasta/máquina nova e seguir só o README | **[PREENCHER]** data, SO e resultado |
| Proteção de segredo | Comandos do README (seção Testes) sobre o repositório publicado | **[PREENCHER]** resultado |
| Avaliação por pares (Moodle) | Duas avaliações de autores distintos | **[PREENCHER]** |

Observação: a credencial inválida real e a falha de comunicação são **falhas induzidas** (chave fictícia / host inacessível), e não ocorrências espontâneas.

## 6. Resultados com o LLM real

**[PREENCHER]** Execute no horário agendado e preencha com o que **de fato** aconteceu, inclusive resultados ruins. Modelo usado: **[PREENCHER]**; data/hora: **[PREENCHER]**.

| Caso | status obtido | C1 | C2 | C3 | C4 | C5 | Observações |
|---|---|---|---|---|---|---|---|
| 01_comum | | | | | | – | |
| 02_incompleta | | | | | | – | |
| 03_ambigua | | | | | | – | |
| 04_fora_do_escopo | | | | | | – | |
| 05_injecao_prompt | | | | | | | |
| 06_vazia | recusada antes do LLM (comprovado em 5.1) | – | – | – | A | – | |
| 07_conteudo_tecnico | | | | | | – | |

Se algum resultado esperado não ocorrer (por exemplo, o modelo obedecer à injeção ou inventar plano para o caso incompleto), registre-o aqui como limitação; se não ocorrer, registre a ausência e os casos testados.

## 7. Limitações e falhas conhecidas

1. **Qualidade não verificada automaticamente:** os testes validam estrutura, não se o plano é pedagogicamente adequado (C2 e C3 dependem de revisão humana).
2. **Injeção de prompt:** a mitigação por delimitadores reduz o risco, mas não o elimina; o resultado real está na seção 6.
3. **Contrato da API presumido:** formato OpenAI (`/chat/completions`) inferido de `LLM_BASE_URL`/`LLM_MODEL`. Não pôde ser confirmado fora da plataforma.
4. **Modo lote com serviço fora do ar:** cada arquivo espera o timeout (até 120 s) antes de falhar, o que consome o horário agendado. Melhoria possível: interromper após a primeira falha de comunicação.
5. **Novas anotações na plataforma** exigem reconstruir a imagem.
6. **Privacidade:** o texto da anotação é enviado ao serviço de LLM; o log registra apenas tamanho, status e tipo de erro.
7. O `.gitignore` e o `.env.example` enviados tinham quebras de linha CRLF; a leitura da configuração aplica `strip()` para evitar efeitos disso.

## 8. Processo, autoria e uso de IA

- **Histórico:** **[PREENCHER]** liste os commits reais (ordem sugerida: chamada mínima → configuração → entrada → prompt → cliente → parser → apresentação/CLI → testes → Docker → documentação). Não publique tudo em um único commit.
- **Uso de IA:** a estrutura do projeto, os módulos, os testes e o rascunho desta documentação foram gerados com apoio do assistente Claude (Anthropic), a partir do problema e das diretrizes da disciplina. **[PREENCHER]** descreva o que você revisou, executou e alterou, e o que ajustou após rodar na plataforma. Todo código incorporado deve ser compreendido por você; o vídeo é o lugar de demonstrar isso.
- **Vídeo:** **[PREENCHER: link]**.
- **Avaliação por pares (Moodle):** **[PREENCHER]** autores avaliados e data.
