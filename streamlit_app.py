import streamlit as st
import runpy
from pathlib import Path

st.set_page_config(
    page_title="Autonomous Inventory Agent",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


PAGES = {
    "📊 Dashboard": "dashboard.Home",
    "📚 Visão Histórica": "dashboard/OriginalData.py",
    "🛒 Vendas": "dashboard.Sales",
    "📦 Estoque": "dashboard.Inventory",
    "🧾 Produtos": "dashboard.Products",
    "⚙️ Simulação": "dashboard.Simulation",
    "🤖 Agentes": "dashboard.Agents",
    "🧠 Decisões": "dashboard.Decisions",
    "📡 Eventos": "dashboard.Events",
    "🚚 Compras": "dashboard.Purchases",
    "📊 Analytics": "dashboard.Analytics",
    # "🔮 Previsão": "dashboard.Forecast",
    "📋 Tarefas": "dashboard.Tasks",
    "🏭 Fornecedores": "dashboard.Suppliers",
    "📄 Relatórios": "dashboard.Reports",
    "🧠 AI Analyst": "dashboard.AI_Analyst",
}


st.sidebar.title(
    "📦 Autonomous Inventory Agent"
)

st.sidebar.caption(
    "Sistema autônomo de gestão de estoque"
)


page = st.sidebar.radio(
    "Navegação",
    list(PAGES.keys())
)


st.sidebar.divider()

st.sidebar.caption(
    "Sistema"
)

st.sidebar.success(
    "🟢 Operational"
)
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
    # "🔮 Previsão": "dashboard/Forecast.py",
    "📋 Tarefas": "dashboard/Tasks.py",
    "🏭 Fornecedores": "dashboard/Suppliers.py",
    "📄 Relatórios": "dashboard/Reports.py",
    "🧠 AI Analyst": "dashboard/AI_Analyst.py",
}

page_path = Path(PAGE_FILES[page])

runpy.run_path(
    str(page_path),
    run_name="__main__"
)