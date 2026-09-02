import streamlit as st
import runpy
from pathlib import Path


st.set_page_config(
    page_title="Autonomous Inventory Agent",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PÁGINAS
# ============================================================

PAGE_FILES = {
    "📊 Dashboard": "dashboard/Home.py",
    "📚 Visão Histórica": "dashboard/OriginalData.py",
    "🛒 Vendas": "dashboard/Sales.py",
    "📦 Estoque": "dashboard/Inventory.py",
    "🧾 Produtos": "dashboard/Products.py",
    "⚙️ Simulação": "dashboard/Simulation.py",
    "🤖 Agentes": "dashboard/Agents.py",
    "🧠 Decisões": "dashboard/Decisions.py",
    "📡 Eventos": "dashboard/Events.py",
    "🚚 Compras": "dashboard/Purchases.py",
    "📊 Analytics": "dashboard/Analytics.py",
    "📋 Tarefas": "dashboard/Tasks.py",
    "🏭 Fornecedores": "dashboard/Suppliers.py",
    "📄 Relatórios": "dashboard/Reports.py",
    "🧠 AI Analyst": "dashboard/AI_Analyst.py",
}


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "📦 Autonomous Inventory Agent"
)

st.sidebar.caption(
    "Sistema autônomo de gestão de estoque"
)


page = st.sidebar.radio(
    "Navegação",
    list(PAGE_FILES.keys())
)


st.sidebar.divider()

st.sidebar.caption(
    "Sistema"
)

st.sidebar.success(
    "🟢 Operational"
)


# ============================================================
# CONTAINER DA PÁGINA
# ============================================================

page_container = st.empty()


with page_container.container():

    page_path = Path(PAGE_FILES[page])

    runpy.run_path(
        str(page_path),
        run_name="__main__"
    )