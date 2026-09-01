import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("🏭 Fornecedores")

st.caption(
    "Monitoramento de fornecedores, "
    "lead time e confiabilidade."
)


suppliers = pd.read_sql(
    """
    SELECT
        supplier_id,
        supplier_name,
        lead_time_days,
        reliability
    FROM suppliers
    ORDER BY reliability DESC
    """,
    engine
)


if suppliers.empty:

    st.info(
        "Nenhum fornecedor cadastrado."
    )

else:

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Fornecedores",
        f"{len(suppliers):,}"
    )

    col2.metric(
        "Lead time médio",
        f"{suppliers['lead_time_days'].mean():.1f} dias"
    )

    col3.metric(
        "Confiabilidade média",
        f"{suppliers['reliability'].mean() * 100:.1f}%"
    )

    st.divider()

    display = suppliers.copy()

    display["reliability"] = (
        display["reliability"] * 100
    ).round(1)

    display = display.rename(
        columns={
            "supplier_id": "ID",
            "supplier_name": "Fornecedor",
            "lead_time_days": "Lead Time (dias)",
            "reliability": "Confiabilidade (%)"
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "📦 Compras por fornecedor"
    )

    purchases = pd.read_sql(
        """
        SELECT
            supplier_id,
            COUNT(*) AS orders,
            COALESCE(
                SUM(quantity),
                0
            ) AS units
        FROM purchases
        GROUP BY supplier_id
        ORDER BY orders DESC
        """,
        engine
    )

    if purchases.empty:

        st.info(
            "Nenhuma compra registrada."
        )

    else:

        st.dataframe(
            purchases,
            use_container_width=True,
            hide_index=True
        )