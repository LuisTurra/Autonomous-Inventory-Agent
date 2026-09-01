import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("🧾 Produtos")

products = pd.read_sql(
    """
    SELECT
        p.product_id,
        p.product_category_name,
        p.unit_price,
        i.quantity,
        i.reorder_point,
        i.reorder_quantity
    FROM products p
    LEFT JOIN inventory i
        ON p.product_id = i.product_id
    ORDER BY p.product_id
    """,
    engine
)

if products.empty:

    st.info("Nenhum produto encontrado.")

else:

    category = st.selectbox(
        "Categoria",
        ["Todas"] +
        sorted(
            products["product_category_name"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    filtered = products.copy()

    if category != "Todas":

        filtered = filtered[
            filtered["product_category_name"]
            == category
        ]

    st.metric(
        "Produtos encontrados",
        f"{len(filtered):,}"
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🔎 Detalhes do produto")

    product_id = st.selectbox(
        "Selecione um produto",
        filtered["product_id"].tolist()
    )

    product = filtered[
        filtered["product_id"] == product_id
    ].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Preço médio",
        f"R$ {float(product['unit_price']):,.2f}"
    )

    col2.metric(
        "Estoque",
        f"{int(product['quantity'] or 0):,}"
    )

    col3.metric(
        "Reorder Point",
        f"{int(product['reorder_point'] or 0):,}"
    )

    col4.metric(
        "Reposição",
        f"{int(product['reorder_quantity'] or 0):,}"
    )