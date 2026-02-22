# scripts/chat_ui.py
# Interface de chat local com Ollama
# Rodar: streamlit run scripts/chat_ui.py

import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os
import ollama

load_dotenv()

# ── Configuracao da pagina ────────────────────────────────────
st.set_page_config(
    page_title="LLM Analytics",
    page_icon="🤖",
    layout="wide",
)

# ── Caminhos ───────────────────────────────────────────────────
AGENT_DIR  = Path(__file__).parent.parent / "agent"
SKILLS_DIR = AGENT_DIR / "skills"

# ── Mapa de deteccao de skills ─────────────────────────────────
# Cada skill tem um peso por keyword encontrada na mensagem.
# A skill com maior pontuacao e ativada automaticamente.
SKILL_KEYWORDS: dict[str, list[str]] = {
    "sql_analyst": [
        "sql", "query", "select", "from", "where", "join", "group by",
        "order by", "cte", "subquery", "index", "stored procedure",
        "view", "trigger", "schema", "tabela", "banco", "mysql",
        "postgres", "postgresql", "dw", "geo", "duckdb",
        "otimiza", "lento", "performance", "explain", "partition",
        "window function", "rank", "row_number", "lag", "lead",
    ],
    "python": [
        "python", "pandas", "polars", "dataframe", "df", "numpy",
        "script", "codigo", "funcao", "def ", "import", "pip",
        "loop", "lista", "dicionario", "classe", "objeto",
        "csv", "excel", "json", "api", "requests", "httpx",
        "automacao", "etl", "pipeline", "sqlalchemy", "venv",
        "erro", "exception", "traceback", "debug",
    ],
    "powerbi": [
        "power bi", "powerbi", "dax", "medida", "measure",
        "pbix", "pbip", "relatorio", "visual", "pagina",
        "modelo", "relacionamento", "cardinalidade", "estrela",
        "calendario", "data table", "slicer", "filtro",
        "calculate", "filter", "sumx", "averagex", "divide",
        "block", "element", "modifier", "tbdc", "__",
        "fabric", "gateway", "dataset", "semantic model",
        "coluna calculada", "calculated column",
    ],
}

SKILL_ICONS = {
    "sql_analyst": "🗄️",
    "python":      "🐍",
    "powerbi":     "📊",
}

# ── Funcoes auxiliares ───────────────────────────────────────────

def load_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def load_all_skills() -> dict[str, str]:
    skills = {}
    if SKILLS_DIR.exists():
        for f in sorted(SKILLS_DIR.glob("*.md")):
            skills[f.stem] = f.read_text(encoding="utf-8")
    return skills

def detect_skills(message: str, all_skills: dict[str, str]) -> list[str]:
    """Retorna lista de skills detectadas na mensagem, ordenadas por pontuacao."""
    text = message.lower()
    scores: dict[str, int] = {}

    for skill, keywords in SKILL_KEYWORDS.items():
        if skill not in all_skills:
            continue
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[skill] = score

    return sorted(scores, key=lambda s: scores[s], reverse=True)

def build_system_prompt(active_skills: list[str], all_skills: dict[str, str]) -> str:
    soul   = load_file(AGENT_DIR / "SOUL.md")
    user   = load_file(AGENT_DIR / "USER.md")
    memory = load_file(AGENT_DIR / "MEMORY.md")

    parts = [soul]
    if user:
        parts.append(f"## Contexto do usuario:\n{user}")
    if memory:
        parts.append(f"## Memoria:\n{memory}")
    for skill in active_skills:
        content = all_skills.get(skill, "")
        if content:
            parts.append(f"## Skill ativa [{skill}]:\n{content}")

    return "\n\n---\n\n".join(filter(None, parts))

def list_models() -> list[str]:
    try:
        return [m.model for m in ollama.list().models]
    except Exception:
        return [os.getenv("OLLAMA_MODEL", "llama3.2")]

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuracoes")

    models = list_models()
    default_model = os.getenv("OLLAMA_MODEL", models[0] if models else "llama3.2")
    default_idx   = models.index(default_model) if default_model in models else 0
    selected_model = st.selectbox("Modelo", models, index=default_idx)

    st.divider()

    # Status dos arquivos de contexto
    st.markdown("**Contexto carregado:**")
    for label, fname in [("SOUL.md", "SOUL.md"), ("USER.md", "USER.md"), ("MEMORY.md", "MEMORY.md")]:
        path = AGENT_DIR / fname
        icon = "✅" if path.exists() and path.stat().st_size > 0 else "⚠️"
        st.markdown(f"{icon} {label}")

    st.divider()

    # Skills disponiveis
    all_skills = load_all_skills()
    st.markdown("**Skills disponíveis:**")
    for skill in all_skills:
        icon = SKILL_ICONS.get(skill, "💡")
        st.markdown(f"{icon} `{skill}`")

    st.divider()

    # Log de deteccao da ultima mensagem
    if "last_detected" in st.session_state and st.session_state.last_detected:
        st.markdown("**Ultima deteccao:**")
        for s in st.session_state.last_detected:
            icon = SKILL_ICONS.get(s, "💡")
            st.success(f"{icon} {s}")
    elif "last_detected" in st.session_state:
        st.markdown("**Ultima deteccao:**")
        st.info("💬 Contexto geral")

    st.divider()

    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.session_state.pop("last_detected", None)
        st.rerun()

# ── Area principal ───────────────────────────────────────────
st.title("🤖 LLM Analytics")
st.caption(f"Modelo: `{selected_model}` · Deteccao de skill automatica")

# ── Historico ──────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("skills"):
            skills_label = " + ".join(
                f"{SKILL_ICONS.get(s, '')} {s}" for s in msg["skills"]
            )
            st.caption(f"Skills usadas: {skills_label}")

# ── Input ─────────────────────────────────────────────────────
if prompt := st.chat_input("Digite sua mensagem..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Detecta skills automaticamente
    detected = detect_skills(prompt, all_skills)
    st.session_state.last_detected = detected

    # Mostra badge de deteccao em tempo real
    if detected:
        badge = " + ".join(f"{SKILL_ICONS.get(s, '')} `{s}`" for s in detected)
        st.info(f"Skill detectada: {badge}")

    # Monta system prompt com as skills detectadas
    system_prompt = build_system_prompt(detected, all_skills)
    messages_payload = [{"role": "system", "content": system_prompt}]
    messages_payload += [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Gera resposta com streaming
    with st.chat_message("assistant"):
        response_box   = st.empty()
        full_response  = ""

        try:
            stream = ollama.chat(
                model=selected_model,
                messages=messages_payload,
                stream=True,
            )
            for chunk in stream:
                token = chunk["message"]["content"]
                full_response += token
                response_box.markdown(full_response + "▌")
            response_box.markdown(full_response)

            if detected:
                skills_label = " + ".join(
                    f"{SKILL_ICONS.get(s, '')} {s}" for s in detected
                )
                st.caption(f"Skills usadas: {skills_label}")

        except Exception as e:
            full_response = f"❌ Erro ao conectar no Ollama: {e}"
            response_box.error(full_response)

    st.session_state.messages.append({
        "role":    "assistant",
        "content": full_response,
        "skills":  detected,
    })
