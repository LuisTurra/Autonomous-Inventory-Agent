import streamlit as st

from src.analytics.inventory_analysis import (
    get_inventory_analysis,
    get_low_stock_products,
    get_out_of_stock_products,
    get_fast_moving_products,
    get_slow_moving_products,
)


st.title("📦 Estoque")

data = get_inventory_analysis()


if data.empty:

    st.info(
        "Nenhum dado de estoque encontrado."
    )

else:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Produtos",
        f"{len(data):,}"
    )

    col2.metric(
        "Unidades em estoque",
        f"{int(data['quantity'].sum()):,}"
    )

    col3.metric(
        "Estoque baixo",
        f"{len(get_low_stock_products()):,}"
    )

    col4.metric(
        "Sem estoque",
        f"{len(get_out_of_stock_products()):,}"
    )

    st.divider()

    st.subheader("📊 Inventory Health")

    display = data[
        [
            "product_id",
            "product_category_name",
            "quantity",
            "sales_per_day",
            "days_of_inventory",
            "status",
        ]
    ].copy()

    display = display.rename(
        columns={
            "product_id": "Produto",
            "product_category_name": "Categoria",
            "quantity": "Estoque",
            "sales_per_day": "Saída/dia",
            "days_of_inventory": "Dias restantes",
            "status": "Status",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🚀 Fast Moving")

    st.dataframe(
        get_fast_moving_products(10),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🐌 Slow Moving")

    st.dataframe(
        get_slow_moving_products(10),
        use_container_width=True,
        hide_index=True
    )