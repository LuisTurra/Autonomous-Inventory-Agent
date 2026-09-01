import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("🚚 Compras")

st.caption(
    "Pedidos de reposição e entregas dos fornecedores."
)


purchases = pd.read_sql(
    """
    SELECT
        purchase_id,
        product_id,
        supplier_id,
        quantity,
        unit_cost,
        status,
        expected_delivery,
        delivered_at
    FROM purchases
    WHERE is_simulated = TRUE
    ORDER BY purchase_id DESC
    LIMIT 200
    """,
    engine
)


if purchases.empty:

    st.info(
        "Nenhuma compra registrada."
    )

else:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Pedidos",
        f"{len(purchases):,}"
    )

    col2.metric(
        "Pendentes",
        f"{len(purchases[purchases['status'] == 'ORDERED']):,}"
    )

    col3.metric(
        "Entregues",
        f"{len(purchases[purchases['status'] == 'DELIVERED']):,}"
    )

    col4.metric(
        "Unidades",
        f"{int(purchases['quantity'].sum()):,}"
    )

    st.divider()

    status_filter = st.selectbox(
        "Status",
        ["Todos"] +
        sorted(
            purchases["status"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    filtered = purchases.copy()

    if status_filter != "Todos":

        filtered = filtered[
            filtered["status"]
            == status_filter
        ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("💰 Custo das compras")

    purchases["total_cost"] = (
        purchases["quantity"]
        * purchases["unit_cost"]
    )

    st.metric(
        "Custo total",
        f"R$ {purchases['total_cost'].sum():,.2f}"
    )