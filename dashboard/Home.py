import streamlit as st
import pandas as pd

from src.database.repositories import clear_simulation_data
from src.database.connection import engine
from src.database.demo_loader import load_demo


# ============================================================
# CONFIGURAÇÃO DO AMBIENTE
# ============================================================

try:
    APP_MODE = st.secrets["APP_MODE"]
except Exception:
    APP_MODE = "desktop"

IS_CLOUD = APP_MODE == "cloud"


# ============================================================
# INICIALIZAÇÃO DO AMBIENTE
# ============================================================

@st.cache_resource
def initialize_cloud_demo():
    """
    Inicializa o estado padrão da Demo no Streamlit Cloud.

    Executa uma única vez por processo do Streamlit:
    - remove dados simulados existentes
    - restaura o Demo Dataset
    """
    load_demo()
    return True


if IS_CLOUD:
    initialize_cloud_demo()
else:

    if "simulation_initialized" not in st.session_state:
        clear_simulation_data()
        st.session_state.simulation_initialized = True


# ============================================================
# TÍTULO
# ============================================================

st.title("📦 Autonomous Inventory Agent")

st.caption("Control Room")


if IS_CLOUD:
    st.info(
        "☁️ **Demo Dataset ativo** — "
        "dados simulados pré-gerados estão carregados na base."
    )


# ============================================================
# RESUMO DO ESTOQUE
# ============================================================

col1, col2, col3, col4 = st.columns(4)

data = pd.read_sql(
    """
    SELECT
        COUNT(*) AS products,
        COALESCE(SUM(quantity), 0) AS stock,
        COALESCE(
            SUM(
                CASE
                    WHEN quantity <= reorder_point
                    THEN 1
                    ELSE 0
                END
            ),
            0
        ) AS low_stock,
        COALESCE(
            SUM(
                CASE
                    WHEN quantity <= 0
                    THEN 1
                    ELSE 0
                END
            ),
            0
        ) AS out_of_stock
    FROM inventory
    """,
    engine
)

row = data.iloc[0]

col1.metric("Produtos", f"{int(row['products']):,}")
col2.metric("Estoque", f"{int(row['stock']):,}")
col3.metric("Estoque baixo", f"{int(row['low_stock']):,}")
col4.metric("Sem estoque", f"{int(row['out_of_stock']):,}")


# ============================================================
# LIVE ACTIVITY
# ============================================================

st.divider()

st.subheader("⚡ Live Activity")

events = pd.read_sql(
    """
    SELECT
        event_type,
        product_id,
        quantity,
        event_timestamp
    FROM events
    ORDER BY event_timestamp DESC
    LIMIT 15
    """,
    engine
)

if events.empty:
    st.info("Nenhum evento registrado.")
else:
    st.dataframe(
        events,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# AGENT STATUS
# ============================================================

st.divider()

st.subheader("🤖 Agent Status")

col1, col2, col3, col4 = st.columns(4)

col1.success("Monitor\n\n🟢 ACTIVE")
col2.success("Sales\n\n🟢 ACTIVE")
col3.success("Demand\n\n🟢 ACTIVE")
col4.warning("Replenishment\n\n🟡 WAITING")