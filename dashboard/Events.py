import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("📡 Eventos")

st.caption(
    "Fluxo de eventos gerados pelo sistema."
)


events = pd.read_sql(
    """
    SELECT
        event_id,
        event_type,
        product_id,
        quantity,
        event_data,
        event_timestamp
    FROM events
    WHERE is_simulated = TRUE
    ORDER BY event_timestamp DESC
    LIMIT 500
    """,
    engine
)


if events.empty:

    st.info(
        "Nenhum evento registrado."
    )

else:

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Eventos",
        f"{len(events):,}"
    )

    col2.metric(
        "Tipos de evento",
        f"{events['event_type'].nunique():,}"
    )

    col3.metric(
        "Produtos envolvidos",
        f"{events['product_id'].nunique():,}"
    )

    st.divider()

    event_filter = st.selectbox(
        "Tipo de evento",
        ["Todos"] +
        sorted(
            events["event_type"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    filtered = events.copy()

    if event_filter != "Todos":

        filtered = filtered[
            filtered["event_type"]
            == event_filter
        ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("📈 Eventos por tipo")

    event_counts = (
        filtered["event_type"]
        .value_counts()
        .reset_index()
    )

    event_counts.columns = [
        "event_type",
        "count"
    ]

    st.bar_chart(
        event_counts.set_index(
            "event_type"
        )
    )