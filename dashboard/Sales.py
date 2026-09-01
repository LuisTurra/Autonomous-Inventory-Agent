import streamlit as st

from src.analytics.sales_ranking import (
    get_sales_ranking,
    top_selling_products,
    lowest_selling_products,
    highest_revenue_products,
)


st.title("🛒 Vendas")

period = st.selectbox(
    "Período",
    [
        "Hoje",
        "7 dias",
        "30 dias",
        "90 dias",
        "Total"
    ]
)

days_map = {
    "Hoje": 1,
    "7 dias": 7,
    "30 dias": 30,
    "90 dias": 90,
    "Total": None
}

days = days_map[period]

ranking = get_sales_ranking(days)


if ranking.empty:

    st.info(
        "Ainda não existem vendas simuladas."
    )

else:

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Unidades vendidas",
        f"{int(ranking['units_sold'].sum()):,}"
    )

    col2.metric(
        "Receita",
        f"R$ {ranking['revenue'].sum():,.2f}"
    )

    col3.metric(
        "Produtos vendidos",
        f"{len(ranking):,}"
    )

    st.divider()

    st.subheader("🏆 Produtos mais vendidos")

    st.dataframe(
        top_selling_products(
            limit=20,
            days=days
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("💰 Maior receita")

    st.dataframe(
        highest_revenue_products(
            limit=20,
            days=days
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("📉 Menor saída")

    st.dataframe(
        lowest_selling_products(
            limit=20,
            days=days
        ),
        use_container_width=True,
        hide_index=True
    )