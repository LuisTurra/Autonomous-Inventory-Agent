import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("🧠 Decisões")

st.caption(
    "Histórico auditável das decisões tomadas pelos agentes."
)


decisions = pd.read_sql(
    """
    SELECT
        decision_id,
        agent_name,
        product_id,
        decision_type,
        reasoning,
        decision_data,
        created_at
    FROM decisions
    WHERE is_simulated = TRUE
    ORDER BY created_at DESC
    LIMIT 200
    """,
    engine
)


if decisions.empty:

    st.info(
        "Nenhuma decisão foi registrada ainda."
    )

else:

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Decisões",
        f"{len(decisions):,}"
    )

    col2.metric(
        "Agentes",
        f"{decisions['agent_name'].nunique():,}"
    )

    col3.metric(
        "Tipos",
        f"{decisions['decision_type'].nunique():,}"
    )

    st.divider()

    agent_filter = st.selectbox(
        "Agente",
        ["Todos"] +
        sorted(
            decisions["agent_name"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    filtered = decisions.copy()

    if agent_filter != "Todos":

        filtered = filtered[
            filtered["agent_name"]
            == agent_filter
        ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🔍 Detalhes")

    decision_ids = filtered[
        "decision_id"
    ].tolist()

    if decision_ids:

        selected = st.selectbox(
            "Selecione uma decisão",
            decision_ids
        )

        decision = filtered[
            filtered["decision_id"]
            == selected
        ].iloc[0]

        st.write(
            f"**Agente:** {decision['agent_name']}"
        )

        st.write(
            f"**Produto:** {decision['product_id']}"
        )

        st.write(
            f"**Tipo:** {decision['decision_type']}"
        )

        st.write(
            f"**Justificativa:** "
            f"{decision['reasoning']}"
        )

        st.write(
            f"**Dados da decisão:** "
            f"{decision['decision_data']}"
        )