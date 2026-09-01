import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("📋 Tarefas")

st.caption(
    "Tarefas geradas pelos agentes autônomos."
)


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
    ORDER BY
        CASE priority
            WHEN 'CRITICAL' THEN 1
            WHEN 'HIGH' THEN 2
            WHEN 'MEDIUM' THEN 3
            ELSE 4
        END,
        created_at DESC
    LIMIT 500
    """,
    engine
)


if tasks.empty:

    st.info(
        "Nenhuma tarefa registrada."
    )

else:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total",
        f"{len(tasks):,}"
    )

    col2.metric(
        "Pendentes",
        f"{len(tasks[tasks['status'] == 'PENDING']):,}"
    )

    col3.metric(
        "Em execução",
        f"{len(tasks[tasks['status'] == 'IN_PROGRESS']):,}"
    )

    col4.metric(
        "Críticas",
        f"{len(tasks[tasks['priority'] == 'CRITICAL']):,}"
    )

    st.divider()

    status = st.selectbox(
        "Status",
        ["Todos"] +
        sorted(
            tasks["status"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    filtered = tasks.copy()

    if status != "Todos":

        filtered = filtered[
            filtered["status"] == status
        ]

    priority = st.selectbox(
        "Prioridade",
        ["Todas"] +
        sorted(
            filtered["priority"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    if priority != "Todas":

        filtered = filtered[
            filtered["priority"] == priority
        ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )