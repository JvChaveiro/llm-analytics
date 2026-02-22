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

# ── Caminhos dos arquivos de contexto ────────────────────────
AGENT_DIR = Path(__file__).parent.parent / "agent"
SKILLS_DIR = AGENT_DIR / "skills"

# ── Funcoes de contexto ──────────────────────────────────────

def load_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def load_skills() -> dict:
    skills = {"Nenhuma": ""}
    if SKILLS_DIR.exists():
        for f in sorted(SKILLS_DIR.glob("*.md")):
            skills[f.stem] = f.read_text(encoding="utf-8")
    return skills

def build_system_prompt(skill_content: str) -> str:
    soul   = load_file(AGENT_DIR / "SOUL.md")
    user   = load_file(AGENT_DIR / "USER.md")
    memory = load_file(AGENT_DIR / "MEMORY.md")

    parts = [soul]
    if user:
        parts.append(f"## Contexto do usuario:\n{user}")
    if memory:
        parts.append(f"## Memoria:\n{memory}")
    if skill_content:
        parts.append(f"## Skill ativa:\n{skill_content}")

    return "\n\n---\n\n".join(filter(None, parts))

def list_models() -> list:
    try:
        models = ollama.list()
        return [m.model for m in models.models]
    except Exception:
        return [os.getenv("OLLAMA_MODEL", "llama3.2")]

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuracoes")

    # Selecao de modelo
    models = list_models()
    default_model = os.getenv("OLLAMA_MODEL", models[0] if models else "llama3.2")
    default_idx = models.index(default_model) if default_model in models else 0
    selected_model = st.selectbox("Modelo", models, index=default_idx)

    # Selecao de skill
    skills = load_skills()
    selected_skill_name = st.selectbox("Skill ativa", list(skills.keys()))
    selected_skill = skills[selected_skill_name]

    st.divider()

    # Status dos arquivos de contexto
    st.markdown("**Contexto carregado:**")
    for label, fname in [("SOUL.md", "SOUL.md"), ("USER.md", "USER.md"), ("MEMORY.md", "MEMORY.md")]:
        path = AGENT_DIR / fname
        icon = "✅" if path.exists() and path.stat().st_size > 0 else "⚠️"
        st.markdown(f"{icon} {label}")

    st.divider()

    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.rerun()

# ── Area principal ───────────────────────────────────────────
st.title("🤖 LLM Analytics")

if selected_skill_name != "Nenhuma":
    st.caption(f"Skill ativa: `{selected_skill_name}` · Modelo: `{selected_model}`")
else:
    st.caption(f"Modelo: `{selected_model}` · Sem skill ativa")

# ── Historico de mensagens ───────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input do usuario ─────────────────────────────────────────
if prompt := st.chat_input("Digite sua mensagem..."):

    # Exibe mensagem do usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Monta historico para o modelo
    system_prompt = build_system_prompt(selected_skill)
    messages_payload = [{"role": "system", "content": system_prompt}]
    messages_payload += [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Gera resposta com streaming
    with st.chat_message("assistant"):
        response_box = st.empty()
        full_response = ""

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

        except Exception as e:
            full_response = f"❌ Erro ao conectar no Ollama: {e}"
            response_box.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
