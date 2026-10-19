# Oficina de qualidade de prompts

Pipeline para converter relatos de bugs em User Stories, publicar uma versão do prompt no LangSmith e medir a qualidade em um dataset fixo de 15 exemplos. A implementação mantém o avaliador e o dataset fornecidos pelo exercício.

## Técnicas Aplicadas (Fase 2)

O prompt `prompts/bug_to_user_story_v2.yml` combina três técnicas:

| Técnica | Aplicação | Motivo |
|---|---|---|
| Few-shot | Três pares entrada/saída: filtro de exportação, duplicação de endereço e relato insuficiente | Mostrar critérios verificáveis e como tratar falta de informação sem fabricar requisitos |
| Role prompting | Product Manager responsável por histórias implementáveis e testáveis | Tornar explícita a perspectiva de produto, sem pressupor soluções técnicas |
| Skeleton of thought | Seções fixas de título, contexto, User Story, critérios de aceitação e pontos a esclarecer | Dar uma estrutura consistente à resposta final, sem solicitar raciocínio interno |

O exemplo de CSV preserva o filtro da profissional selecionada e verifica que outros horários não aparecem. O de endereço cobre clique único e repetido. O relato insuficiente pede atual, esperado e reprodução. O prompt também delimita o relato como dado e rejeita instruções que tentem mudar a tarefa.

### Comparação v1 e v2

A v1 presente no starter usa uma instrução genérica, insere `bug_report` nas mensagens de sistema e usuário, não fornece exemplos e não define critérios de aceitação. A v2 deixa a variável somente na mensagem do usuário, explicita o papel, fixa o formato, demonstra entradas/saídas e separa fatos de lacunas.

Essa comparação descreve os arquivos locais. O pull do Hub e a comparação empírica ainda precisam ser executados com credenciais. O identificador semente `leonanluppi/bug_to_user_story_v1` é obrigatório no exercício; os scripts preservam esse contrato.

## Como Executar

Pré-requisitos: Python 3.12, conta LangSmith com chave e handle público, e chave do Gemini (ou OpenAI, suportado pelo avaliador original).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure no `.env`:

- `LANGSMITH_API_KEY`, `USERNAME_LANGSMITH_HUB` e `LANGSMITH_PROJECT=oficina-prompt-quality`.
- `LLM_PROVIDER=google`, `GOOGLE_API_KEY`, `LLM_MODEL` e `EVAL_MODEL` com modelos Gemini disponíveis e compatíveis com `temperature=0`.
- Para OpenAI, use `LLM_PROVIDER=openai` e `OPENAI_API_KEY` em vez da chave Google.

Consulte os [modelos Gemini](https://ai.google.dev/gemini-api/docs/models) ou [modelos OpenAI](https://platform.openai.com/docs/models). Não envie o `.env` ao repositório.

Execute na raiz, nesta ordem:

```bash
python src/pull_prompts.py
python src/push_prompts.py
python src/evaluate.py
```

O pull importa o prompt semente como `ChatPromptTemplate` e salva a v1 sem descartar mensagens. Se o formato remoto não corresponder ao suportado, falha explicitamente. O push valida o YAML, exige `few-shot` e outra técnica, confere a variável `bug_report` e publica `HANDLE/bug_to_user_story_v2` como prompt público.

O avaliador busca a versão publicada, executa os 15 exemplos e registra o experimento com tracing. Confira **helpfulness, correctness, f1_score, clarity e precision**, além da média. Todas precisam atingir **0,8**; uma média alta não compensa uma métrica abaixo do limite.

Analise os exemplos com falhas, ajuste somente o prompt, faça novo push e repita a avaliação. O exercício espera 3 a 5 iterações; registre somente as efetivamente realizadas. `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e o dataset permanecem inalterados.

## Resultados Finais

**Implementação e validação local prontas; avaliação remota pendente de credenciais.** Ainda não há experimento, nota, prompt público próprio nem screenshot de aprovação. Nenhum resultado de LLM foi simulado para preencher esses itens.

Os **10 testes locais passaram** em 19/10/2026. Eles cobrem campos/estrutura do YAML, few-shot, técnica adicional, uso de `bug_report`, formatação com chaves literais e preservação do prompt importado. Execute:

```bash
PYTHONPATH=src pytest -q
```

| Evidência exigida | Estado |
|---|---|
| Pull real do prompt semente | Aguarda chave LangSmith |
| Prompt v2 público no próprio handle | Aguarda chave e handle |
| Experimentos e cinco métricas ≥0,8 | Aguarda chaves e execução |
| Dataset público com 15 exemplos | Aguarda experimentos e compartilhamento |
| Tracing de pelo menos três exemplos | Aguarda experimentos |
| Screenshots das notas finais | Aguarda resultados reais |

Após validar as métricas, compartilhe **uma vez** o dataset no LangSmith e registre seu link público aqui. O endereço do experimento mostrado pelo script pode exigir acesso ao workspace. O compartilhamento expõe o dataset e seus experimentos; use apenas os exemplos do exercício. Guarde também capturas do dashboard e três traces representativos. Os testes locais não substituem essas evidências.
