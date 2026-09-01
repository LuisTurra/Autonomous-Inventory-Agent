import streamlit as st
import pandas as pd

from src.database.connection import engine
from src.llm.groq_client import GroqClient

st.title("🧠 AI Analyst")

st.caption(
    "Relatório operacional baseado exclusivamente nos dados "
    "de estoque e demanda do sistema."
)


if "ai_report" not in st.session_state:
    st.session_state.ai_report = None



# CONSULTA



@st.cache_data(ttl=30)
def get_inventory_summary():

    query = """
        WITH reference_date AS (
            SELECT
                COALESCE(
                    MAX(sale_timestamp),
                    CURRENT_TIMESTAMP
                ) AS max_date
            FROM sales
        ),

        sales_30d AS (
            SELECT
                s.product_id,
                SUM(s.quantity) AS units_sold_30d
            FROM sales s
            CROSS JOIN reference_date r
            WHERE s.sale_timestamp >=
                r.max_date - INTERVAL '30 days'
            GROUP BY s.product_id
        ),

        sales_previous_30d AS (
            SELECT
                s.product_id,
                SUM(s.quantity) AS units_sold_previous_30d
            FROM sales s
            CROSS JOIN reference_date r
            WHERE s.sale_timestamp >=
                r.max_date - INTERVAL '60 days'
              AND s.sale_timestamp <
                r.max_date - INTERVAL '30 days'
            GROUP BY s.product_id
        )

        SELECT
            i.product_id,

            COALESCE(
                p.product_category_name,
                'Sem categoria'
            ) AS product_category_name,

            COALESCE(i.quantity, 0)
                AS quantity,

            COALESCE(i.reorder_point, 0)
                AS reorder_point,

            COALESCE(i.reorder_quantity, 0)
                AS reorder_quantity,

            COALESCE(
                s30.units_sold_30d,
                0
            ) AS units_sold_30d,

            COALESCE(
                sp30.units_sold_previous_30d,
                0
            ) AS units_sold_previous_30d,

            r.max_date AS reference_date

        FROM inventory i

        LEFT JOIN products p
            ON p.product_id = i.product_id

        LEFT JOIN sales_30d s30
            ON s30.product_id = i.product_id

        LEFT JOIN sales_previous_30d sp30
            ON sp30.product_id = i.product_id

        CROSS JOIN reference_date r

        ORDER BY
            units_sold_30d DESC
    """

    return pd.read_sql(query, engine)




# PREPARAÇÃO DOS DADOS

def prepare_analysis_data(data):

    df = data.copy()

    numeric_columns = [
        "quantity",
        "reorder_point",
        "reorder_quantity",
        "units_sold_30d",
        "units_sold_previous_30d",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    # --------------------------------------------------------
    # RISCO DE ESTOQUE
    # --------------------------------------------------------

    def classify_risk(row):

        stock = row["quantity"]
        reorder_point = row["reorder_point"]
        sales_30d = row["units_sold_30d"]

        if stock <= 0:
            return "CRITICAL"

        if stock <= reorder_point:
            return "HIGH"

        if sales_30d > 0 and stock <= sales_30d:
            return "MEDIUM"

        return "LOW"

    df["risk"] = df.apply(classify_risk, axis=1)

    # --------------------------------------------------------
    # COBERTURA
    # --------------------------------------------------------

    daily_sales = df["units_sold_30d"] / 30

    df["days_of_stock"] = (df["quantity"] / daily_sales).where(daily_sales > 0)

    # --------------------------------------------------------
    # VARIAÇÃO DA DEMANDA
    # --------------------------------------------------------

    previous = df["units_sold_previous_30d"]

    current = df["units_sold_30d"]

    df["sales_change_pct"] = (((current - previous) / previous) * 100).where(
        previous > 0
    )

    return df


# ============================================================
# CONSTRUIR RESUMO PARA IA
# ============================================================


def build_ai_summary(df):

    # ========================================================
    # ESTOQUE
    # ========================================================

    out_of_stock = df[df["quantity"] <= 0]

    below_reorder = df[(df["quantity"] > 0) & (df["quantity"] <= df["reorder_point"])]

    near_reorder = df[
        (df["quantity"] > df["reorder_point"])
        & (df["quantity"] <= df["reorder_point"] * 1.25)
    ]

    # ========================================================
    # RISCO
    # ========================================================

    risk_counts = {
        "CRITICAL": int((df["risk"] == "CRITICAL").sum()),
        "HIGH": int((df["risk"] == "HIGH").sum()),
        "MEDIUM": int((df["risk"] == "MEDIUM").sum()),
        "LOW": int((df["risk"] == "LOW").sum()),
    }

    # ========================================================
    # DEMANDA TOTAL
    # ========================================================

    sales_30d = int(df["units_sold_30d"].sum())

    sales_previous = int(df["units_sold_previous_30d"].sum())

    if sales_previous > 0:

        total_change = round(((sales_30d - sales_previous) / sales_previous) * 100, 1)

    else:

        total_change = None

    # ========================================================
    # TOP PRODUTOS
    # ========================================================

    top_products_df = (
        df[df["units_sold_30d"] > 0]
        .sort_values("units_sold_30d", ascending=False)
        .head(10)
    )

    top_products = []

    for _, row in top_products_df.iterrows():

        top_products.append(
            {
                "product_id": str(row["product_id"]),
                "category": str(row["product_category_name"]),
                "stock": int(row["quantity"]),
                "sales_30d": int(row["units_sold_30d"]),
                "reorder_point": int(row["reorder_point"]),
                "days_of_stock": (
                    round(float(row["days_of_stock"]), 1)
                    if pd.notna(row["days_of_stock"])
                    else None
                ),
                "risk": row["risk"],
            }
        )

    # ========================================================
    # PRODUTOS PRIORITÁRIOS
    # ========================================================

    risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    priority_df = df[df["risk"].isin(["CRITICAL", "HIGH", "MEDIUM"])].copy()

    priority_df["risk_order"] = priority_df["risk"].map(risk_order)

    priority_df = priority_df.sort_values(
        ["risk_order", "units_sold_30d"], ascending=[True, False]
    ).head(15)

    priority_products = []

    for _, row in priority_df.iterrows():

        priority_products.append(
            {
                "product_id": str(row["product_id"]),
                "category": str(row["product_category_name"]),
                "stock": int(row["quantity"]),
                "sales_30d": int(row["units_sold_30d"]),
                "reorder_point": int(row["reorder_point"]),
                "reorder_quantity": int(row["reorder_quantity"]),
                "days_of_stock": (
                    round(float(row["days_of_stock"]), 1)
                    if pd.notna(row["days_of_stock"])
                    else None
                ),
                "risk": row["risk"],
            }
        )

    # ========================================================
    # CRESCIMENTO
    # ========================================================

    growth_df = (
        df[df["sales_change_pct"].notna() & (df["sales_change_pct"] > 0)]
        .sort_values("sales_change_pct", ascending=False)
        .head(10)
    )

    growth = []

    for _, row in growth_df.iterrows():

        growth.append(
            {
                "product_id": str(row["product_id"]),
                "category": str(row["product_category_name"]),
                "sales_30d": int(row["units_sold_30d"]),
                "sales_previous_30d": int(row["units_sold_previous_30d"]),
                "change_pct": round(float(row["sales_change_pct"]), 1),
            }
        )

    # ========================================================
    # QUEDA
    # ========================================================

    decline_df = (
        df[df["sales_change_pct"].notna() & (df["sales_change_pct"] < 0)]
        .sort_values("sales_change_pct", ascending=True)
        .head(10)
    )

    decline = []

    for _, row in decline_df.iterrows():

        decline.append(
            {
                "product_id": str(row["product_id"]),
                "category": str(row["product_category_name"]),
                "sales_30d": int(row["units_sold_30d"]),
                "sales_previous_30d": int(row["units_sold_previous_30d"]),
                "change_pct": round(float(row["sales_change_pct"]), 1),
            }
        )

    # ========================================================
    # CATEGORIAS
    # ========================================================

    category_df = (
        df.groupby("product_category_name")
        .agg(
            products=("product_id", "count"),
            stock=("quantity", "sum"),
            sales_30d=("units_sold_30d", "sum"),
        )
        .sort_values("sales_30d", ascending=False)
        .head(10)
        .reset_index()
    )

    categories = []

    for _, row in category_df.iterrows():

        percentage = (row["sales_30d"] / sales_30d) * 100 if sales_30d > 0 else 0

        categories.append(
            {
                "category": str(row["product_category_name"]),
                "products": int(row["products"]),
                "stock": int(row["stock"]),
                "sales_30d": int(row["sales_30d"]),
                "share_pct": round(percentage, 1),
            }
        )

    # ========================================================
    # CONCENTRAÇÃO
    # ========================================================

    selling_products = df[df["units_sold_30d"] > 0]

    selling_product_count = len(selling_products)

    if sales_30d > 0:

        top_10_sales = int(top_products_df["units_sold_30d"].sum())

        top_10_share = round((top_10_sales / sales_30d) * 100, 1)

    else:

        top_10_share = 0

    # ========================================================
    # RESUMO FINAL
    # ========================================================

    return {
        "reference_date": str(df["reference_date"].iloc[0]),
        "inventory": {
            "products_monitored": len(df),
            "total_stock_units": int(df["quantity"].sum()),
            "out_of_stock": len(out_of_stock),
            "below_reorder_point": len(below_reorder),
            "near_reorder_point": len(near_reorder),
        },
        "risk_summary": risk_counts,
        "demand": {
            "sales_30d": sales_30d,
            "sales_previous_30d": (sales_previous),
            "change_pct": total_change,
            "products_with_sales": (selling_product_count),
        },
        "concentration": {"top_10_sales_share_pct": (top_10_share)},
        "priority_products": (priority_products),
        "top_products": top_products,
        "top_categories": categories,
        "demand_growth": growth,
        "demand_decline": decline,
    }


# ============================================================
# CARREGAR
# ============================================================

data = get_inventory_summary()


if data.empty:

    st.info("Não existem dados suficientes para análise.")

    st.stop()


df = prepare_analysis_data(data)

ai_summary = build_ai_summary(df)


# ============================================================
# DASHBOARD
# ============================================================

st.subheader("📊 Visão operacional")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Produtos", f"{len(df):,}")

col2.metric("Estoque", f"{int(df['quantity'].sum()):,}")

col3.metric("Vendas 30d", f"{int(df['units_sold_30d'].sum()):,}")

col4.metric("Produtos críticos", int((df["risk"] == "CRITICAL").sum()))


# ============================================================
# RISCO
# ============================================================

st.divider()

st.subheader("🚦 Classificação de estoque")

c1, c2, c3, c4 = st.columns(4)

c1.metric("🔴 CRITICAL", int((df["risk"] == "CRITICAL").sum()))

c2.metric("🟠 HIGH", int((df["risk"] == "HIGH").sum()))

c3.metric("🟡 MEDIUM", int((df["risk"] == "MEDIUM").sum()))

c4.metric("🟢 LOW", int((df["risk"] == "LOW").sum()))


# ============================================================
# ESTOQUE
# ============================================================

st.divider()

st.subheader("📦 Situação do estoque")

s1, s2, s3 = st.columns(3)

s1.metric("Sem estoque", len(df[df["quantity"] <= 0]))

s2.metric(
    "Abaixo do reorder point",
    len(df[(df["quantity"] <= df["reorder_point"]) & (df["quantity"] > 0)]),
)

s3.metric(
    "Próximos do reorder point",
    len(
        df[
            (df["quantity"] > df["reorder_point"])
            & (df["quantity"] <= df["reorder_point"] * 1.25)
        ]
    ),
)


# ============================================================
# PRIORITÁRIOS
# ============================================================

st.divider()

st.subheader("🎯 Produtos prioritários")

priority_display = df[df["risk"].isin(["CRITICAL", "HIGH", "MEDIUM"])].copy()

risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}

priority_display["risk_order"] = priority_display["risk"].map(risk_order)

priority_display = priority_display.sort_values(
    ["risk_order", "units_sold_30d"], ascending=[True, False]
)

if priority_display.empty:

    st.success(
        "Nenhum produto apresenta risco CRITICAL, "
        "HIGH ou MEDIUM segundo os critérios atuais."
    )

else:

    st.dataframe(
        priority_display[
            [
                "product_id",
                "product_category_name",
                "quantity",
                "units_sold_30d",
                "reorder_point",
                "reorder_quantity",
                "days_of_stock",
                "risk",
            ]
        ].rename(
            columns={
                "product_id": "Produto",
                "product_category_name": "Categoria",
                "quantity": "Estoque",
                "units_sold_30d": "Vendas 30d",
                "reorder_point": "Ponto reposição",
                "reorder_quantity": "Qtd. reposição",
                "days_of_stock": "Dias estoque",
                "risk": "Risco",
            }
        ),
        width="stretch",
        hide_index=True,
    )


# ============================================================
# DADOS COMPLETOS
# ============================================================

with st.expander("📋 Ver dados completos"):

    st.dataframe(
        df[
            [
                "product_id",
                "product_category_name",
                "quantity",
                "reorder_point",
                "reorder_quantity",
                "units_sold_30d",
                "units_sold_previous_30d",
                "days_of_stock",
                "sales_change_pct",
                "risk",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


# ============================================================
# IA
# ============================================================

st.divider()

st.subheader("🤖 Relatório do AI Analyst")

if st.button("🧠 Gerar relatório executivo", width="stretch"):

    with st.spinner("Analisando estoque e demanda..."):

        try:

            client = GroqClient()

            result = client.analyze_inventory(ai_summary)

            st.session_state.ai_report = result

        except Exception as e:

            st.error(f"Erro ao gerar análise: {e}")


# ============================================================
# EXIBIR RELATÓRIO SALVO
# ============================================================

if st.session_state.ai_report:

    st.markdown(st.session_state.ai_report)
