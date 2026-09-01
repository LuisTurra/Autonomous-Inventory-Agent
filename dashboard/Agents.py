import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("🤖 Agentes Autônomos")

st.caption(
    "Monitoramento das decisões e atividades dos agentes."
)


agents = pd.DataFrame([
    {
        "Agente": "Monitor Agent",
        "Função": "Monitorar estoque",
        "Status": "ACTIVE"
    },
    {
        "Agente": "Sales Analyst",
        "Função": "Analisar vendas",
        "Status": "ACTIVE"
    },
    {
        "Agente": "Demand Agent",
        "Função": "Analisar demanda",
        "Status": "ACTIVE"
    },
    {
        "Agente": "Replenishment Agent",
        "Função": "Reposição automática",
        "Status": "ACTIVE"
    },
])


st.subheader("Status dos agentes")

st.dataframe(
    agents,
    use_container_width=True,
    hide_index=True
)


st.divider()

st.subheader("🧠 Decisões recentes")

decisions = pd.read_sql(
    """
    SELECT
        decision_id,
        agent_name,
        product_id,
        decision_type,
        reasoning,
        created_at
    FROM decisions
    WHERE is_simulated = TRUE
    ORDER BY created_at DESC
    LIMIT 50
    """,
    engine
)

if decisions.empty:

    st.info(
        "Nenhuma decisão registrada."
    )

else:

    st.dataframe(
        decisions,
        use_container_width=True,
        hide_index=True
    )


st.divider()

st.subheader("📋 Tarefas")

tasks = pd.read_sql(
    """
    SELECT
        task_id,
        task_type,
        product_id,
        quantity,
        priority,
        status,
        created_at
    FROM tasks
    WHERE is_simulated = TRUE
    ORDER BY created_at DESC
    LIMIT 50
    """,
    engine
)

if tasks.empty:

    st.info(
        "Nenhuma tarefa registrada."
    )

else:

    st.dataframe(
        tasks,
        use_container_width=True,
        hide_index=True
    )