# scripts/db.py
# Centraliza as conexões com banco de dados via aliases.
# Importe diretamente nos scripts e notebooks:
#   from scripts.db import dw, geo

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# ─── CONEXÕES ────────────────────────────────────────────────

# DW — Data Warehouse principal (schema: dw_tbdc_prd)
dw = create_engine(
    os.getenv("MYSQL_DW_CONNECTION"),
    pool_pre_ping=True,   # reconecta automaticamente se a sessão cair
    pool_recycle=3600,    # recicla conexões a cada 1h (evita timeout)
)

# GEO — Banco de produção da empresa (origem do DW)
geo = create_engine(
    os.getenv("MYSQL_GEO_CONNECTION"),
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ─── TESTE DE CONEXÃO ────────────────────────────────────────

def testar_conexoes():
    """Valida se DW e GEO estão acessíveis. Rode antes de iniciar análises."""
    for nome, engine in [("DW", dw), ("GEO", geo)]:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ {nome}: conectado")
        except Exception as e:
            print(f"❌ {nome}: falhou — {e}")


if __name__ == "__main__":
    testar_conexoes()
