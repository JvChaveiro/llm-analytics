# MEMORY.md
> Memória de longo prazo curada. Só registrar decisões, preferências
> duráveis e fatos importantes. Não é um diário — é uma referência.

---

## Kick Off — 2026-02-21

### Projeto criado: llm-analytics
- Workspace local para integração de LLMs com fluxos de dados
- Estrutura de pastas criada via PowerShell
- Sistema de arquivos do agente em `agent/` (SOUL.md, USER.md, MEMORY.md, skills/)

### Decisões de arquitetura
- Backend LLM: **Ollama local** (privacidade, sem custo de API)
- Padrão de memória: arquivos Markdown (inspirado em OpenClaw)
  - SOUL.md = personalidade e regras permanentes
  - USER.md = contexto do usuário
  - MEMORY.md = este arquivo (fatos duráveis)
  - agent/skills/*.md = skills carregadas sob demanda
- Injeção de contexto via `scripts/ollama_client.py`
- Modelo preferido: qwen2.5:14b (contexto 32k+)

### Stack definida
- Python + ollama SDK + pandas/polars + sqlalchemy + duckdb
- Ambiente virtual: `.venv/` (não commitado)
- Segredos em `.env` (não commitado)

### Convenções do projeto
- Variáveis em inglês, comentários em português
- Prompts versionados em `prompts/sql/` e `prompts/python/`
- Notebooks para exploração; scripts para uso recorrente

---

## Como usar este arquivo

- **Adicionar:** quando tomar uma decisão técnica importante, mudar de
  ferramenta, ou aprender algo que quer lembrar sempre
- **Não adicionar:** detalhes de sessão, logs de debug, rascunhos
- **Revisar:** mensalmente — remover o que ficou obsoleto
- **Formato:** `## Data — Tópico` seguido de bullets concisos