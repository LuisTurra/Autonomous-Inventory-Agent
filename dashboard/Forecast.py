import streamlit as st
import pandas as pd

from src.database.connection import engine
from src.analytics.forecasting import forecast_product_demand


st.title("🔮 Previsão de Demanda")

st.caption(
    "Estimativa de demanda futura baseada no histórico de vendas."
)


products = pd.read_sql(
    """
    SELECT
        product_id,
        product_category_name
    FROM products
    ORDER BY product_id
    """,
    engine
)


if products.empty:

    st.info(
        "Nenhum produto encontrado."
    )

else:

    product_id = st.selectbox(
        "Produto",
        products["product_id"].tolist()
    )

    forecast_days = st.slider(
        "Dias para previsão",
        min_value=1,
        max_value=30,
        value=7
    )

    if st.button(
        "🔮 Gerar previsão",
        use_container_width=True
    ):

        result = forecast_product_demand(
            product_id=product_id,
            forecast_days=forecast_days
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Demanda diária estimada",
            f"{result['predicted_daily_demand']:.2f}"
        )

        col2.metric(
            "Demanda total estimada",
            f"{result['predicted_total_demand']:.0f}"
        )

        st.divider()

        history = pd.read_sql(
            """
            SELECT
                DATE(sale_timestamp) AS sale_date,
                SUM(quantity) AS units_sold
            FROM sales
            WHERE product_id = :product_id
            GROUP BY DATE(sale_timestamp)
            ORDER BY sale_date
            """,
            engine,
            params={
                "product_id": product_id
            }
        )

        if not history.empty:

            st.subheader(
                "📈 Histórico de vendas"
            )

            chart = history.set_index(
                "sale_date"
            )[["units_sold"]]

            st.line_chart(chart)

        st.info(
            "A previsão é uma estimativa baseada "
            "no comportamento histórico do produto."
        )