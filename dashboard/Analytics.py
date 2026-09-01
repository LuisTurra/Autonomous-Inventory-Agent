import streamlit as st
import pandas as pd

from src.database.connection import engine


st.title("📊 Analytics")

st.caption(
    "Visão analítica da operação de estoque e vendas."
)


sales = pd.read_sql(
    """
    SELECT
        DATE(sale_timestamp) AS sale_date,
        SUM(quantity) AS units_sold,
        SUM(quantity * unit_price) AS revenue,
        is_simulated
    FROM sales
    GROUP BY
        DATE(sale_timestamp),
        is_simulated
    ORDER BY sale_date
    """,
    engine
)

historical_sales = sales[
    sales["is_simulated"] == False
].copy()

simulated_sales = sales[
    sales["is_simulated"] == True
].copy()
inventory = pd.read_sql(
    """
    SELECT
        COUNT(*) AS products,
        COALESCE(SUM(quantity), 0) AS total_stock,
        COALESCE(
            SUM(
                CASE
                    WHEN quantity <= reorder_point
                    THEN 1
                    ELSE 0
                END
            ),
            0
        ) AS low_stock,
        COALESCE(
            SUM(
                CASE
                    WHEN quantity <= 0
                    THEN 1
                    ELSE 0
                END
            ),
            0
        ) AS out_of_stock
    FROM inventory
    """,
    engine
)


if not sales.empty:

    historical_sales = sales[
        sales["is_simulated"] == False
    ].copy()

    simulated_sales = sales[
        sales["is_simulated"] == True
    ].copy()

    # ========================================================
    # KPIs
    # ========================================================

    historical_units = (
        historical_sales["units_sold"].sum()
        if not historical_sales.empty
        else 0
    )

    simulated_units = (
        simulated_sales["units_sold"].sum()
        if not simulated_sales.empty
        else 0
    )

    historical_revenue = (
        historical_sales["revenue"].sum()
        if not historical_sales.empty
        else 0
    )

    simulated_revenue = (
        simulated_sales["revenue"].sum()
        if not simulated_sales.empty
        else 0
    )

    total_units = (
        historical_units +
        simulated_units
    )

    total_revenue = (
        historical_revenue +
        simulated_revenue
    )

    historical_days = (
        historical_sales["sale_date"].nunique()
        if not historical_sales.empty
        else 0
    )

    simulated_days = (
        simulated_sales["sale_date"].nunique()
        if not simulated_sales.empty
        else 0
    )

    total_days = (
        historical_days +
        simulated_days
    )

    # ========================================================
    # TOTAL
    # ========================================================

    st.subheader("📊 Indicadores gerais")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📦 Unidades vendidas",
        f"{int(total_units):,}"
    )

    col2.metric(
        "💰 Receita total",
        f"R$ {total_revenue:,.2f}"
    )

    col3.metric(
        "📅 Dias com vendas",
        f"{total_days:,}"
    )

    # ========================================================
    # HISTÓRICO X SIMULAÇÃO
    # ========================================================

    st.caption(
        "Separação entre a base histórica original e os dados "
        "gerados pela simulação."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📚 Histórico — unidades",
            f"{int(historical_units):,}"
        )

        st.metric(
            "📚 Histórico — receita",
            f"R$ {historical_revenue:,.2f}"
        )

        st.metric(
            "📚 Histórico — dias",
            f"{historical_days:,}"
        )

    with col2:

        st.metric(
            "🤖 Simulação — unidades",
            f"{int(simulated_units):,}"
        )

        st.metric(
            "🤖 Simulação — receita",
            f"R$ {simulated_revenue:,.2f}"
        )

        st.metric(
            "🤖 Simulação — dias",
            f"{simulated_days:,}"
        )

    with col3:

        st.metric(
            "📊 Total — unidades",
            f"{int(total_units):,}"
        )

        st.metric(
            "📊 Total — receita",
            f"R$ {total_revenue:,.2f}"
        )

        st.metric(
            "📊 Total — dias",
            f"{total_days:,}"
        )

    

    st.divider()

    st.subheader("📈 Evolução das vendas")

if not historical_sales.empty:

    st.caption("📚 Base original")

    historical_chart = historical_sales.set_index(
        "sale_date"
    )[["units_sold"]]

    st.line_chart(
        historical_chart
    )


if not simulated_sales.empty:

    st.caption("🤖 Simulação")

    simulated_chart = simulated_sales.set_index(
        "sale_date"
    )[["units_sold"]]

    st.line_chart(
        simulated_chart
    )

    st.divider()

    st.divider()

st.subheader("💰 Evolução da receita")

if not historical_sales.empty:

    st.caption("📚 Base original 2016-2018")

    historical_revenue = historical_sales.set_index(
        "sale_date"
    )[["revenue"]]

    st.line_chart(
        historical_revenue
    )


if not simulated_sales.empty:

    st.caption("🤖 Simulação 2026")

    simulated_revenue = simulated_sales.set_index(
        "sale_date"
    )[["revenue"]]

    st.line_chart(
        simulated_revenue
    )


if not inventory.empty:

    row = inventory.iloc[0]

    st.divider()

    st.subheader("📦 Saúde do estoque")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Produtos",
        f"{int(row['products']):,}"
    )

    col2.metric(
        "Estoque total",
        f"{int(row['total_stock']):,}"
    )

    col3.metric(
        "Estoque baixo",
        f"{int(row['low_stock']):,}"
    )

    col4.metric(
        "Sem estoque",
        f"{int(row['out_of_stock']):,}"
    )