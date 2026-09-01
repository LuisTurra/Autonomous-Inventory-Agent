import streamlit as st
import pandas as pd
from sqlalchemy import text
import plotly.express as px
from src.database.connection import engine


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.title("📚 Visão Histórica")

st.caption(
    "Dashboard da base original. "
    "Dados gerados pela simulação são ignorados."
)


# ============================================================
# RESUMO GERAL
# ============================================================

@st.cache_data(ttl=30)
def load_summary():

    query = """
        SELECT
            COUNT(*) AS total_sales,

            COALESCE(
                SUM(quantity),
                0
            ) AS total_units,

            COALESCE(
                SUM(quantity * unit_price),
                0
            ) AS total_revenue,

            COUNT(DISTINCT product_id) AS products

        FROM sales

        WHERE is_simulated = FALSE
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        ).iloc[0]


# ============================================================
# EVOLUÇÃO DAS VENDAS
# ============================================================

@st.cache_data(ttl=30)
def load_sales_evolution():

    query = """
        SELECT
            DATE_TRUNC(
                'month',
                sale_timestamp
            ) AS month,

            SUM(quantity) AS units,

            SUM(
                quantity * unit_price
            ) AS revenue,

            COUNT(*) AS sales

        FROM sales

        WHERE is_simulated = FALSE

        GROUP BY
            DATE_TRUNC(
                'month',
                sale_timestamp
            )

        ORDER BY month
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        )


# ============================================================
# CATEGORIAS
# ============================================================

@st.cache_data(ttl=30)
def load_categories():

    query = """
        SELECT
            COALESCE(
                p.product_category_name,
                'Sem categoria'
            ) AS category,

            SUM(
                s.quantity
            ) AS units,

            SUM(
                s.quantity * s.unit_price
            ) AS revenue

        FROM sales s

        JOIN products p
            ON p.product_id = s.product_id

        WHERE s.is_simulated = FALSE

        GROUP BY
            p.product_category_name

        ORDER BY
            units DESC
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        )


# ============================================================
# TOP PRODUTOS
# ============================================================

@st.cache_data(ttl=30)
def load_top_products():

    query = """
        SELECT
            s.product_id,

            COALESCE(
                p.product_category_name,
                'Sem categoria'
            ) AS category,

            SUM(
                s.quantity
            ) AS units,

            SUM(
                s.quantity * s.unit_price
            ) AS revenue

        FROM sales s

        JOIN products p
            ON p.product_id = s.product_id

        WHERE s.is_simulated = FALSE

        GROUP BY
            s.product_id,
            p.product_category_name

        ORDER BY
            units DESC

        LIMIT 20
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        )


# ============================================================
# PRODUTOS MAIS RENTÁVEIS
# ============================================================

@st.cache_data(ttl=30)
def load_top_revenue_products():

    query = """
        SELECT
            s.product_id,

            COALESCE(
                p.product_category_name,
                'Sem categoria'
            ) AS category,

            SUM(
                s.quantity
            ) AS units,

            SUM(
                s.quantity * s.unit_price
            ) AS revenue

        FROM sales s

        JOIN products p
            ON p.product_id = s.product_id

        WHERE s.is_simulated = FALSE

        GROUP BY
            s.product_id,
            p.product_category_name

        ORDER BY
            revenue DESC

        LIMIT 20
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        )


# ============================================================
# PRODUTOS
# ============================================================

@st.cache_data(ttl=30)
def load_product_summary():

    query = """
        SELECT
            COUNT(*) AS total_products,

            COUNT(
                DISTINCT product_category_name
            ) AS total_categories

        FROM products
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        ).iloc[0]


# ============================================================
# ESTOQUE ORIGINAL
# ============================================================

@st.cache_data(ttl=30)
def load_inventory_summary():

    query = """
        SELECT
            COUNT(*) AS products_in_inventory,

            COALESCE(
                SUM(quantity),
                0
            ) AS total_stock,

            COUNT(
                CASE
                    WHEN quantity <= reorder_point
                    THEN 1
                END
            ) AS low_stock

        FROM inventory
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        ).iloc[0]


# ============================================================
# PRODUTOS COM MAIOR ESTOQUE
# ============================================================

@st.cache_data(ttl=30)
def load_inventory():

    query = """
        SELECT
            i.product_id,

            COALESCE(
                p.product_category_name,
                'Sem categoria'
            ) AS category,

            i.quantity,
            i.minimum_stock,
            i.reorder_point,
            i.reorder_quantity

        FROM inventory i

        JOIN products p
            ON p.product_id = i.product_id

        ORDER BY
            i.quantity DESC

        LIMIT 20
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection
        )


# ============================================================
# CARREGAMENTO
# ============================================================

try:

    summary = load_summary()

    sales_evolution = load_sales_evolution()

    categories = load_categories()

    top_products = load_top_products()

    top_revenue_products = (
        load_top_revenue_products()
    )

    product_summary = load_product_summary()

    inventory_summary = (
        load_inventory_summary()
    )

    inventory = load_inventory()

except Exception as e:

    st.error(
        f"Erro ao carregar a base histórica: {e}"
    )

    st.stop()


# ============================================================
# VALORES DOS KPIs
# ============================================================

total_sales = int(
    summary["total_sales"]
)

total_units = int(
    summary["total_units"]
)

total_revenue = float(
    summary["total_revenue"]
)

products_sold = int(
    summary["products"]
)

total_products = int(
    product_summary["total_products"]
)

total_categories = int(
    product_summary["total_categories"]
)

average_sale = (
    total_revenue / total_sales
    if total_sales > 0
    else 0
)

total_stock = int(
    inventory_summary["total_stock"]
)

low_stock = int(
    inventory_summary["low_stock"]
)


# ============================================================
# KPIs PRINCIPAIS
# ============================================================

st.subheader("📊 Resumo da base original")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🛒 Vendas",
    f"{total_sales:,}"
)

col2.metric(
    "📦 Unidades vendidas",
    f"{total_units:,}"
)

col3.metric(
    "💰 Receita",
    f"R$ {total_revenue:,.2f}"
)

col4.metric(
    "🎟️ Média por venda",
    f"R$ {average_sale:,.2f}"
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🏷️ Produtos cadastrados",
    f"{total_products:,}"
)

col2.metric(
    "📂 Categorias",
    f"{total_categories:,}"
)

col3.metric(
    "📦 Estoque atual",
    f"{total_stock:,}"
)

col4.metric(
    "⚠️ Estoque baixo",
    f"{low_stock:,}"
)


st.divider()


# ============================================================
# EVOLUÇÃO HISTÓRICA
# ============================================================

st.subheader("📈 Evolução histórica das vendas")

if sales_evolution.empty:

    st.info(
        "Não existem vendas originais para apresentar."
    )

else:

    chart = sales_evolution.copy()

    chart["month"] = pd.to_datetime(
        chart["month"]
    )

    chart = chart.set_index(
        "month"
    )

    st.line_chart(
        chart["revenue"]
    )


# ============================================================
# VENDAS E UNIDADES
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader("💰 Receita mensal")

    if not sales_evolution.empty:

        chart = sales_evolution.copy()

        chart["month"] = pd.to_datetime(
            chart["month"]
        )

        chart = chart.set_index(
            "month"
        )

        st.bar_chart(
            chart["revenue"]
        )


with col2:

    st.subheader("📦 Unidades vendidas")

    if not sales_evolution.empty:

        chart = sales_evolution.copy()

        chart["month"] = pd.to_datetime(
            chart["month"]
        )

        chart = chart.set_index(
            "month"
        )

        st.bar_chart(
            chart["units"]
        )


st.divider()


# ============================================================
# CATEGORIAS
# ============================================================
st.subheader("🏷️ Categorias mais vendidas")

if categories.empty:

    st.info(
        "Nenhuma categoria encontrada."
    )

else:

    category_chart = (
        categories
        .sort_values(
            by="units",
            ascending=False
        )
        .head(15)
        .copy()
    )

    # Ordem explícita do maior para o menor
    category_order = category_chart[
        "category"
    ].tolist()

    fig = px.bar(
        category_chart,
        x="units",
        y="category",
        orientation="h",
        category_orders={
            "category": category_order
        },
        labels={
            "units": "Unidades vendidas",
            "category": "Categoria"
        },
        text="units"
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig.update_layout(
        yaxis={
            "categoryorder": "array",
            "categoryarray": category_order
        },
        xaxis_title="Unidades vendidas",
        yaxis_title="Categoria",
        height=600
    )
    fig.update_yaxes(
    autorange="reversed"
)
    st.plotly_chart(
        fig,
        width="stretch"
    )

st.divider()


# ============================================================
# RANKING DE PRODUTOS
# ============================================================

st.subheader("🏆 Produtos mais vendidos")

if top_products.empty:

    st.info(
        "Nenhum produto encontrado."
    )

else:

    products_table = (
        top_products
        .copy()
    )

    products_table.insert(
        0,
        "Posição",
        range(
            1,
            len(products_table) + 1
        )
    )

    products_table["revenue"] = (
        products_table["revenue"]
        .map(
            lambda value:
            f"R$ {value:,.2f}"
        )
    )

    products_table.columns = [
        "Posição",
        "Produto",
        "Categoria",
        "Unidades",
        "Receita"
    ]

    st.dataframe(
        products_table,
        width="stretch",
        hide_index=True
    )


st.divider()


# ============================================================
# PRODUTOS POR RECEITA
# ============================================================

st.subheader("💰 Produtos com maior receita")

if top_revenue_products.empty:

    st.info(
        "Nenhum produto encontrado."
    )

else:

    revenue_table = (
        top_revenue_products
        .copy()
    )

    revenue_table.insert(
        0,
        "Posição",
        range(
            1,
            len(revenue_table) + 1
        )
    )

    revenue_table["revenue"] = (
        revenue_table["revenue"]
        .map(
            lambda value:
            f"R$ {value:,.2f}"
        )
    )

    revenue_table.columns = [
        "Posição",
        "Produto",
        "Categoria",
        "Unidades",
        "Receita"
    ]

    st.dataframe(
        revenue_table,
        width="stretch",
        hide_index=True
    )


st.divider()


# ============================================================
# ESTOQUE
# ============================================================

st.subheader("📦 Visão do estoque")

if inventory.empty:

    st.info(
        "Nenhum registro de estoque encontrado."
    )

else:

    inventory_table = inventory.copy()

    inventory_table.columns = [
        "Produto",
        "Categoria",
        "Estoque",
        "Estoque mínimo",
        "Ponto de reposição",
        "Quantidade de reposição"
    ]

    st.dataframe(
        inventory_table,
        width="stretch",
        hide_index=True
    )


st.divider()


# ============================================================
# INFORMAÇÃO SOBRE A BASE
# ============================================================

st.subheader("🔎 Sobre os dados")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Produtos cadastrados",
    f"{total_products:,}"
)

col2.metric(
    "Categorias",
    f"{total_categories:,}"
)

col3.metric(
    "Produtos vendidos",
    f"{products_sold:,}"
)


st.divider()


# ============================================================
# GARANTIA DE SEPARAÇÃO
# ============================================================

st.info(
    "🔒 **Base original isolada:** "
    "as métricas de vendas, receita, unidades, "
    "categorias e rankings utilizam exclusivamente "
    "`sales.is_simulated = FALSE`. "
    "Registros criados pela simulação não são "
    "considerados neste dashboard."
)